from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from Predictor.predictor_utilities.predict import predictor

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/predict")
async def predict_endpoint(file: UploadFile = File(...)):
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

@app.get("/")
async def root():
    return {"message": "PlumVision Backend is running!"}