import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, WebSocket, WebSocketDisconnect, Query 
from starlette.websockets import WebSocketState 
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from Predictor.predictor_utilities.predict import predictor
from database import (
    Prediction, SessionMetrics, get_db, 
    create_db_and_tables,add_prediction_db, 
    finalize_session_db, create_session_db, AsyncSessionLocal )
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from stream_manager import session_manager

app = FastAPI(title="PlumVision API")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    print("Starting up PlumVision API...")
    await create_db_and_tables()
    print("PlumVision API running...")


@app.websocket("/ws/stream")
async def websocket_stream_endpoint(
    websocket: WebSocket
):
    session_id: Optional[str] = None
    try:
        session_id = await session_manager.connect(websocket)
        if session_id:
            try:
                while True:
                    data = await websocket.receive_bytes()
                    await session_manager.handle_message(session_id, data)
            except WebSocketDisconnect:
                print(f"WebSocket disconnected: {session_id}")
            except Exception as e:
                print(f"WebSocket error for session {session_id}: {e}")
        else:
            print("Failed to establish session.")
    finally:
        if session_id:
            await session_manager.disconnect(session_id)


@app.post("/api/predict", response_model=dict)
async def predict_endpoint(
    file: UploadFile = File(...),
    session_id: Optional[str] = Query(None, description="Optional session ID to associate prediction with"), # Optional Session ID
    db: AsyncSession = Depends(get_db)
):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only images are allowed.")

    try:
        contents = await file.read()
        prediction_result = predictor.predict_image(contents, file.filename)

        if "error" in prediction_result:
            raise HTTPException(status_code=500, detail=f"Prediction error: {prediction_result['error']}")

        if prediction_result and "prediction" in prediction_result and prediction_result["prediction"]:
            db_prediction, superclass = await add_prediction_db(db, session_id, file.filename, prediction_result)
            await db.commit()

            top_prediction = prediction_result["prediction"][0]
            prediction_result["resume"] = {
                "predicted_class": top_prediction["class"],
                "probability": top_prediction["probability"],
                "superclass": superclass
            }
        else:
            prediction_result["resume"] = {"error": "Could not get valid prediction."}
            print(f"Warning: Prediction result was missing expected fields: {prediction_result}")


        return prediction_result

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Error processing single image upload: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
    
    
@app.get("/api/predictions", response_model=List[dict])
async def get_predictions(
    session_id: Optional[str] = Query(None, description="Filter predictions by session ID"),
    limit: int = Query(100, description="Maximum number of predictions to return"),
    db: AsyncSession = Depends(get_db)
):
    query = select(Prediction).order_by(Prediction.timestamp.desc())
    if session_id:
        query = query.where(Prediction.session_id == session_id)
    query = query.limit(limit)

    result = await db.execute(query)
    predictions = result.scalars().all()

    return [
        {
            "id": p.id, "session_id": p.session_id, "image_name": p.image_name,
            "predicted_class": p.predicted_class, "probability": p.probability,
            "superclass": p.superclass, "inference_time": p.inference_time,
            "timestamp": p.timestamp.isoformat()
        } for p in predictions
    ]


@app.get("/api/sessions", response_model=List[dict])
async def get_sessions(
    active_only: bool = Query(False, description="Return only currently active sessions"),
    limit: int = Query(50, description="Maximum number of sessions to return"),
    db: AsyncSession = Depends(get_db)
):
    query = select(SessionMetrics).order_by(SessionMetrics.start_time.desc())
    if active_only:
        active_ids_mem = list(session_manager.active_connections.keys())
        query = query.where(SessionMetrics.session_id.in_(active_ids_mem) | SessionMetrics.is_active == True)

    query = query.limit(limit)
    result = await db.execute(query)
    sessions = result.scalars().all()

    return [
        {
            "session_id": s.session_id, "is_active": s.is_active,
            "total_images_processed": s.total_images_processed,
            "predictions_by_category": s.predictions_by_category,
            "start_time": s.start_time.isoformat(),
            "last_updated": s.last_updated.isoformat(),
            "end_time": s.end_time.isoformat() if s.end_time else None,
            "duration_seconds": s.duration_seconds
         } for s in sessions
    ]


@app.get("/api/sessions/{session_id}", response_model=dict)
async def get_session_details(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SessionMetrics).where(SessionMetrics.session_id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session.session_id, "is_active": session.is_active,
        "total_images_processed": session.total_images_processed,
        "predictions_by_category": session.predictions_by_category,
        "start_time": session.start_time.isoformat(),
        "last_updated": session.last_updated.isoformat(),
        "end_time": session.end_time.isoformat() if session.end_time else None,
        "duration_seconds": session.duration_seconds
    }


@app.get("/")
async def root():
    return {"message": "PlumVision Backend is running!"}