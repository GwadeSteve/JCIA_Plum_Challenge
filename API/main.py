from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from typing import List

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
async def predict(file: UploadFile = File(...)):
    if not file:
        return {
            "error": "No file uploaded"
            }

    content = await file.read()
    return {"filename": file.filename}

@app.get("/")
async def root():
    return {"message": "PlumVision Backend is running!"}