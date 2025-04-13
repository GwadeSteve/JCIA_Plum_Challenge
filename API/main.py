from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from Predictor.predictor_utilities.predict import predictor
from database import Prediction, get_db, create_db_and_tables
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

app = FastAPI()

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
    await create_db_and_tables()

@app.post("/api/predict")
async def predict_endpoint(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only images are allowed.")

    try:
        contents = await file.read()
        prediction_result = predictor.predict_image(contents, file.filename)

        if prediction_result and "prediction" in prediction_result and prediction_result["prediction"]:
            top_prediction = prediction_result["prediction"][0]
            top_class_name = top_prediction["class"]
            top_probability = top_prediction["probability"]
            superclass_mapping = prediction_result["superclass_mapping"].get(top_class_name)
            inference_time = prediction_result["inference_time"]

            db_prediction = Prediction(
                image_name=prediction_result["image_name"],
                predicted_class=top_class_name,
                probability=top_probability,
                superclass=superclass_mapping,
                inference_time=inference_time
            )
            db.add(db_prediction)
            await db.commit()
            await db.refresh(db_prediction)

            prediction_result["resume"] = {
                "predicted_class": top_class_name,
                "probability": top_probability,
                "superclass": superclass_mapping
            }
        else:
            prediction_result["resume"] = {"error": "Could not get top prediction."}

        return prediction_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {e}")

@app.get("/api/predictions")
async def get_predictions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Prediction))
    predictions = result.scalars().all()
    if predictions:
        return predictions
    return {"message": "No predictions for the moment"}

@app.get("/api/metrics")
async def get_metrics(db: AsyncSession = Depends(get_db)):
    return {"message": "This endpoint is currently configured for session metrics."}

@app.get("/")
async def root():
    return {"message": "PlumVision Backend is running!"}