import asyncio
from datetime import datetime, timedelta, timezone
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import json

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
    def __init__(self, predictor: PlumPredictor):
        self.active_connections: dict[str, WebSocket] = {}
        self.session_timers: dict[str, asyncio.Task] = {}
        self.predictor = predictor
        print("Session Manager Initialized")

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

    async def disconnect(self, session_id: str, db: AsyncSession, is_timeout: bool = False):
        print(f"Disconnecting session: {session_id}, Timeout: {is_timeout}")
        if session_id in self.session_timers:
            self.session_timers[session_id].cancel()
            del self.session_timers[session_id]
        if session_id in self.active_connections:
            websocket = self.active_connections.pop(session_id)
            try:
                if not is_timeout:
                    await websocket.close(code=1000)
                    print(f"Closed WebSocket connection for {session_id}")
            except RuntimeError as e:
                 if "WebSocket is not connected" not in str(e):
                     print(f"RuntimeError closing WebSocket for {session_id}: {e}")
            except Exception as e:
                print(f"Error closing WebSocket for {session_id}: {e}")

        try:
            await finalize_session_db(db, session_id)
        except Exception as e:
            print(f"Error finalizing session {session_id} in DB: {e}")

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

            db_prediction, superclass = await add_prediction_db(db, session_id, temp_filename, prediction_result)
            updated_session_metrics = await update_session_stats_db(db, session_id, superclass)

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