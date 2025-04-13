import asyncio
from datetime import datetime, timedelta, timezone
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import json
from typing import Dict, Optional

from database import (
    create_session_db,
    update_session_stats_db,
    finalize_session_db,
    add_prediction_db,
    SessionMetrics
)
from Predictor.predictor_utilities.predict import PlumPredictor

SESSION_TIMEOUT_MINUTES = 5

class SessionManager:
    _instance: Optional["SessionManager"] = None
    active_connections: Dict[str, WebSocket] = {}
    session_timers: Dict[str, asyncio.Task] = {}

    def __new__(cls, predictor: PlumPredictor):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
            cls._instance.predictor = predictor
            print("Session Manager Initialized (Singleton)")
        return cls._instance

    def __init__(self, predictor: PlumPredictor):
        # This will only be called once due to the Singleton pattern
        pass

    async def _start_inactivity_timer(self, session_id: str, db: AsyncSession):
        if session_id in self.session_timers:
            self.session_timers[session_id].cancel()
            print(f"Cancelled previous timer for session {session_id}")

        self.session_timers[session_id] = asyncio.create_task(
            self._check_inactivity(session_id, db)
        )
        print(f"Started inactivity timer for session {session_id}")

    async def _check_inactivity(self, session_id: str, db: AsyncSession):
        try:
            await asyncio.sleep(SESSION_TIMEOUT_MINUTES * 60)
            print(f"Session {session_id} timed out due to inactivity.")
            websocket = self.active_connections.get(session_id)
            if websocket:
                try:
                    await websocket.send_json({"status": "closing", "reason": "inactivity_timeout"})
                    await websocket.close(code=1000)
                except Exception as e:
                    print(f"Error sending closing message or closing WebSocket for {session_id}: {e}")

            await self.disconnect(session_id, db, is_timeout=True)

        except asyncio.CancelledError:
            print(f"Inactivity timer cancelled for session {session_id}.")
            pass
        except Exception as e:
            print(f"Error in inactivity checker for {session_id}: {e}")
            await self.disconnect(session_id, db, is_timeout=False)


    async def connect(self, websocket: WebSocket, db: AsyncSession) -> str:
        await websocket.accept()

        # Close any existing active connection
        if self.active_connections:
            old_session_id, old_websocket = next(iter(self.active_connections.items()))
            print(f"Closing existing active session: {old_session_id}")
            if old_websocket.client_state != 3:  # 3 is WebSocketState.CLOSED
                try:
                    await old_websocket.send_json({"status": "closing", "reason": "new_session_started"})
                    await old_websocket.close(code=1000)
                    await finalize_session_db(db, old_session_id)
                    if old_session_id in self.session_timers:
                        self.session_timers[old_session_id].cancel()
                        del self.session_timers[old_session_id]
                    del self.active_connections[old_session_id]
                    print(f"Successfully closed previous session: {old_session_id}")
                except Exception as e:
                    print(f"Error closing previous session {old_session_id}: {e}")
                    if old_session_id in self.session_timers:
                        self.session_timers[old_session_id].cancel()
                        del self.session_timers[old_session_id]
                    if old_session_id in self.active_connections:
                        del self.active_connections[old_session_id]

        session_id = str(uuid.uuid4())
        self.active_connections[session_id] = websocket
        print(f"WebSocket connected: {session_id}")

        try:
            await create_session_db(db, session_id)
            await self._start_inactivity_timer(session_id, db)
            await websocket.send_json({"status": "connected", "session_id": session_id})
            return session_id
        except Exception as e:
            print(f"Error during session connect for {session_id}: {e}")
            await self.disconnect(session_id, db, is_timeout=False)
            return None

    
    async def disconnect(self, session_id: str, db: AsyncSession, is_timeout: bool = False):
        print(f"Disconnecting session: {session_id}, Timeout: {is_timeout}")
        if session_id in self.session_timers:
            self.session_timers[session_id].cancel()
            del self.session_timers[session_id]
        if session_id in self.active_connections:
            websocket = self.active_connections.pop(session_id)
            try:
                if not is_timeout and websocket.client_state != 3: 
                    await websocket.close(code=1000)
                    print(f"Closed WebSocket connection for {session_id}")
            except RuntimeError as e:
                if "WebSocket is not connected" not in str(e):
                    print(f"RuntimeError closing WebSocket for {session_id}: {e}")
            except Exception as e:
                print(f"Error closing WebSocket for {session_id}: {e}")

        try:
            await db.refresh(db.get_bind())
            await finalize_session_db(db, session_id)
        except Exception as e:
            print(f"Error finalizing session {session_id} in DB: {e}")
            await db.rollback()
    
    
    async def handle_message(self, session_id: str, data: bytes, db: AsyncSession):
        websocket = self.active_connections.get(session_id)
        if not websocket:
            print(f"Warning: Received message for unknown or disconnected session {session_id}")
            return
        await self._start_inactivity_timer(session_id, db)

        try:
            temp_filename = f"stream_{session_id}_{datetime.now(timezone.utc).timestamp()}.jpg"
            prediction_result = self.predictor.predict_image(data, temp_filename)

            if "error" in prediction_result:
                print(f"Prediction error for session {session_id}: {prediction_result['error']}")
                await websocket.send_json({"status": "error", "message": prediction_result['error']})
                return

            if not prediction_result or "prediction" not in prediction_result or not prediction_result["prediction"]:
                print(f"Invalid prediction result structure for session {session_id}")
                await websocket.send_json({"status": "error", "message": "Invalid prediction result structure"})
                return

            try:
                db_prediction, superclass = await add_prediction_db(db, session_id, temp_filename, prediction_result)
                updated_session_metrics = await update_session_stats_db(db, session_id, superclass)
                await db.commit()
            except Exception as db_err:
                print(f"Database error during message handling for session {session_id}: {db_err}")
                await db.rollback()
                await websocket.send_json({"status": "error", "message": f"Database error: {db_err}"})
                return

            response_data = {
                "status": "prediction_result",
                "prediction": prediction_result,
                "session_stats": {
                    "total_images_processed": updated_session_metrics.total_images_processed,
                    "predictions_by_category": updated_session_metrics.predictions_by_category,
                    "last_updated": updated_session_metrics.last_updated.isoformat(),
                } if updated_session_metrics else None
            }

            await websocket.send_json(response_data)

        except WebSocketDisconnect:
            print(f"WebSocket disconnected unexpectedly during message handling for {session_id}.")
            raise
        except Exception as e:
            print(f"Error handling message for session {session_id}: {e}")
            try:
                await websocket.send_json({"status": "error", "message": f"Internal server error: {e}"})
            except Exception as send_e:
                print(f"Failed to send error message back to client {session_id}: {send_e}")


from Predictor.predictor_utilities.predict import predictor as global_predictor
session_manager = SessionManager(predictor=global_predictor)