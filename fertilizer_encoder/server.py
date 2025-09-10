from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
import xgboost as xgb
from fastapi.middleware.cors import CORSMiddleware
import warnings
warnings.filterwarnings('ignore')

# Initialize FastAPI app
app = FastAPI(
    title="Fertilizer Prediction API",
    description="API for predicting the best fertilizer based on environmental conditions and soil nutrients",
    version="1.0.0"
)

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (adjust for production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Global variables for model and preprocessing objects
xgb_model = None
scaler = None
label_encoders = None
le_fertilizer = None

# Define input data model (matches your predict_fertilizer function)
class FertilizerRequest(BaseModel):
    temperature: float
    humidity: float
    moisture: float
    soil_type: str
    crop_type: str
    nitrogen: float
    potassium: float
    phosphorous: float

# Define response model
class FertilizerResponse(BaseModel):
    recommended_fertilizer: str
    confidence: float
    alternatives: list

def load_models():
    """Load the ML model and preprocessing objects"""
    global xgb_model, scaler, label_encoders, le_fertilizer
    
    try:
        # Load the model files (assuming they're in the same directory)
        xgb_model = joblib.load('fertilizer_predictor_xgb.pkl')
        scaler = joblib.load('scaler.pkl')
        label_encoders = joblib.load('label_encoders.pkl')
        le_fertilizer = joblib.load('fertilizer_encoder.pkl')
        
        print("✅ All models loaded successfully!")
        
    except Exception as e:
        print(f"❌ Error loading models: {str(e)}")
        raise HTTPException(status_code=500, detail="Model files not found. Please train the model first.")

# Load models when the server starts
@app.on_event("startup")
async def startup_event():
    try:
        load_models()
        print("🚀 Server started successfully with loaded models!")
    except Exception as e:
        print(f"⚠️  Server started without models: {str(e)}")

@app.get("/")
async def root():
    """API status endpoint"""
    return {
        "message": "Fertilizer Prediction API", 
        "status": "active",
        "endpoints": {
            "docs": "/docs",
            "predict": "/predict (POST)",
            "soil_types": "/soil-types",
            "crop_types": "/crop-types",
            "fertilizer_types": "/fertilizer-types"
        }
    }

@app.post("/predict", response_model=FertilizerResponse)
async def predict_fertilizer(request: FertilizerRequest):
    """
    Predict the best fertilizer for given conditions
    
    This endpoint uses your existing predict_fertilizer function logic
    """
    if xgb_model is None:
        raise HTTPException(status_code=503, detail="Models not loaded. Please train the model first.")
    
    try:
        # VALIDATE INPUTS (using your existing logic)
        valid_soil_types = list(label_encoders['Soil Type'].classes_)
        valid_crop_types = list(label_encoders['Crop Type'].classes_)
        
        if request.soil_type not in valid_soil_types:
            raise HTTPException(status_code=400, 
                              detail=f"Invalid soil type. Available options: {valid_soil_types}")
        
        if request.crop_type not in valid_crop_types:
            raise HTTPException(status_code=400, 
                              detail=f"Invalid crop type. Available options: {valid_crop_types}")

        # ENCODE CATEGORICAL VARIABLES (your existing code)
        soil_encoded = label_encoders['Soil Type'].transform([request.soil_type])[0]
        crop_encoded = label_encoders['Crop Type'].transform([request.crop_type])[0]

        # PREPARE INPUT DATA (your existing code)
        input_data = np.array([[request.temperature, request.humidity, request.moisture, 
                              soil_encoded, crop_encoded, request.nitrogen, 
                              request.potassium, request.phosphorous]])

        # SCALE THE INPUT (your existing code)
        input_scaled = scaler.transform(input_data)

        # GET PREDICTION (your existing code)
        prediction_proba = xgb_model.predict_proba(input_scaled)[0]
        prediction_encoded = np.argmax(prediction_proba)

        # GET TOP PREDICTIONS (your existing code)
        fertilizer_name = le_fertilizer.inverse_transform([prediction_encoded])[0]
        confidence = float(prediction_proba[prediction_encoded])

        # GET TOP 3 ALTERNATIVES (your existing code)
        sorted_indices = np.argsort(prediction_proba)[::-1][:3]
        alternatives = []

        for i in sorted_indices[1:]:  # Skip the top prediction
            alternatives.append({
                'fertilizer': le_fertilizer.inverse_transform([i])[0],
                'confidence': float(prediction_proba[i])
            })

        return FertilizerResponse(
            recommended_fertilizer=fertilizer_name,
            confidence=confidence,
            alternatives=alternatives
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")

@app.get("/soil-types")
async def get_soil_types():
    """Get available soil types"""
    if label_encoders is None:
        raise HTTPException(status_code=503, detail="Models not loaded. Please train the model first.")
    return {"soil_types": list(label_encoders['Soil Type'].classes_)}

@app.get("/crop-types")
async def get_crop_types():
    """Get available crop types"""
    if label_encoders is None:
        raise HTTPException(status_code=503, detail="Models not loaded. Please train the model first.")
    return {"crop_types": list(label_encoders['Crop Type'].classes_)}

@app.get("/fertilizer-types")
async def get_fertilizer_types():
    """Get available fertilizer types"""
    if le_fertilizer is None:
        raise HTTPException(status_code=503, detail="Models not loaded. Please train the model first.")
    return {"fertilizers": list(le_fertilizer.classes_)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)