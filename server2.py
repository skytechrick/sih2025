from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
import numpy as np
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
import warnings
warnings.filterwarnings('ignore')

# Initialize FastAPI app
app = FastAPI(
    title="Fertilizer Recommendation API",
    description="API for calculating fertilizer requirements and costs based on crop and soil conditions",
    version="1.0.0"
)

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define input models based on your requirements
class NutrientLevel(BaseModel):
    nitrogen: int
    phosphorus: int
    potassium: int

class FertilizerRequest(BaseModel):
    cropName: str
    areaInAcres: float
    soilNutrientLevelKnown: bool
    nutrientLevel: Optional[NutrientLevel] = None
    laborCostPerDay: int
    noOfLabors: int

# Define response models
class FertilizerBreakdown(BaseModel):
    fertilizer: str
    quantity: float
    cost: float
    pricePerKg: float

class FertilizerResponse(BaseModel):
    crop: str
    area: float
    fertilizerCost: float
    laborCost: float
    totalCost: float
    fertilizerBreakdown: List[FertilizerBreakdown]
    recommendations: List[str]
    availableFertilizerRates: List[Dict]

# Load fertilizer rate dataset
fertilizer_data = {
    "Fertilizer": [
        "Urea (45 kg bag)", 
        "DAP (50 kg bag)",
        "MOP (50 kg bag)",
        "SSP (50 kg bag)",
        "NPK 10-26-26 (50 kg bag)",
        "NPK 12-32-16 (50 kg bag)",
        "NPK 20-20-0-13 (50 kg bag)"
    ],
    "MRP_Rs_per_bag": [
        242,
        1350,
        1699.35,
        526.80,
        1469.75,
        1493.26,
        1263.78
    ],
    "Bag_Size_kg": [
        45,
        50,
        50,
        50,
        50,
        50,
        50
    ]
}

fertilizer_rates = pd.DataFrame(fertilizer_data)
fertilizer_rates['Price_per_kg'] = fertilizer_rates['MRP_Rs_per_bag'] / fertilizer_rates['Bag_Size_kg']

# Create simplified fertilizer names for matching
fertilizer_mapping = {
    "Urea": "Urea (45 kg bag)",
    "DAP": "DAP (50 kg bag)",
    "MOP": "MOP (50 kg bag)",
    "SSP": "SSP (50 kg bag)",
    "NPK 10-26-26": "NPK 10-26-26 (50 kg bag)",
    "NPK 12-32-16": "NPK 12-32-16 (50 kg bag)",
    "NPK 20-20-0-13": "NPK 20-20-0-13 (50 kg bag)"
}

# Fertilizer nutrient content (kg nutrient per kg fertilizer)
fertilizer_nutrients = {
    "Urea": {"N": 0.46, "P": 0, "K": 0},
    "DAP": {"N": 0.18, "P": 0.46, "K": 0},
    "MOP": {"N": 0, "P": 0, "K": 0.60},
    "SSP": {"N": 0, "P": 0.16, "K": 0},
    "NPK 10-26-26": {"N": 0.10, "P": 0.26, "K": 0.26},
    "NPK 12-32-16": {"N": 0.12, "P": 0.32, "K": 0.16},
    "NPK 20-20-0-13": {"N": 0.20, "P": 0.20, "K": 0, "S": 0.13}
}

# Crop nutrient requirements (kg per acre)
crop_nutrient_requirements = {
    "wheat": {"N": 80, "P": 30, "K": 20},
    "rice": {"N": 100, "P": 40, "K": 40},
    "cotton": {"N": 80, "P": 40, "K": 40},
    "maize": {"N": 90, "P": 30, "K": 30},
    "sugarcane": {"N": 150, "P": 60, "K": 60},
    "potato": {"N": 120, "P": 50, "K": 100},
    "ground nuts": {"N": 20, "P": 40, "K": 40},
    "pulses": {"N": 20, "P": 50, "K": 20},
    "vegetables": {"N": 100, "P": 50, "K": 80}
}

# Typical soil nutrient levels for different soil types (kg/acre)
typical_soil_nutrients = {
    "sandy": {"N": 20, "P": 15, "K": 25},
    "loamy": {"N": 35, "P": 25, "K": 40},
    "clay": {"N": 45, "P": 35, "K": 50},
    "default": {"N": 30, "P": 20, "K": 30}
}

@app.get("/")
async def root():
    return {
        "message": "Fertilizer Recommendation API",
        "status": "active",
        "endpoints": {
            "docs": "/docs",
            "calculate": "/calculate (POST)",
            "crop_types": "/crop-types",
            "fertilizer_types": "/fertilizer-types"
        }
    }

@app.get("/crop-types")
async def get_crop_types():
    """Get available crop types"""
    return {"crop_types": list(crop_nutrient_requirements.keys())}

@app.get("/fertilizer-types")
async def get_fertilizer_types():
    """Get available fertilizer types with prices"""
    fertilizers = []
    for _, row in fertilizer_rates.iterrows():
        fertilizers.append({
            "name": row['Fertilizer'],
            "price_per_kg": round(row['Price_per_kg'], 2),
            "mrp_per_bag": row['MRP_Rs_per_bag'],
            "bag_size_kg": row['Bag_Size_kg']
        })
    return {"fertilizers": fertilizers}

@app.post("/calculate", response_model=FertilizerResponse)
async def calculate_fertilizer_requirements(request: FertilizerRequest):
    """
    Calculate fertilizer requirements based on crop, area, and soil conditions
    
    Request JSON:
    {
        "cropName": "wheat",
        "areaInAcres": 5.0,
        "soilNutrientLevelKnown": true,
        "nutrientLevel": {
            "nitrogen": 25,
            "phosphorus": 15,
            "potassium": 20
        },
        "laborCostPerDay": 500,
        "noOfLabors": 2
    }
    """
    try:
        # Convert crop name to lowercase for matching
        crop = request.cropName.lower()
        acres = request.areaInAcres
        
        # Handle soil nutrient levels
        if request.soilNutrientLevelKnown and request.nutrientLevel:
            soil_N = request.nutrientLevel.nitrogen
            soil_P = request.nutrientLevel.phosphorus
            soil_K = request.nutrientLevel.potassium
            soil_source = "user_provided"
        else:
            # Use default values if not provided
            soil_N = typical_soil_nutrients["default"]["N"]
            soil_P = typical_soil_nutrients["default"]["P"]
            soil_K = typical_soil_nutrients["default"]["K"]
            soil_source = "default_values"
        
        # Calculate fertilizer requirements
        if crop in crop_nutrient_requirements:
            crop_needs = crop_nutrient_requirements[crop]
            
            # Calculate required nutrients after accounting for soil content
            N_required = max(0, crop_needs["N"] - soil_N)
            P_required = max(0, crop_needs["P"] - soil_P)
            K_required = max(0, crop_needs["K"] - soil_K)
            
            # Calculate fertilizer requirements
            # For Phosphorus (using DAP)
            DAP_needed = P_required / fertilizer_nutrients["DAP"]["P"]
            N_from_DAP = DAP_needed * fertilizer_nutrients["DAP"]["N"]
            
            # For Nitrogen (using Urea, accounting for N from DAP)
            Urea_needed = max(0, (N_required - N_from_DAP)) / fertilizer_nutrients["Urea"]["N"]
            
            # For Potassium (using MOP)
            MOP_needed = K_required / fertilizer_nutrients["MOP"]["K"]
            
            # Scale to acreage
            requirements = {
                "Urea": Urea_needed * acres,
                "DAP": DAP_needed * acres,
                "MOP": MOP_needed * acres
            }
            
        else:
            # Default generic recommendation for unknown crops
            requirements = {"Urea": 100 * acres, "DAP": 50 * acres, "MOP": 40 * acres}
        
        # Fertilizer Cost Calculation
        fertilizer_cost = 0
        fertilizer_breakdown = []
        
        for fert, total_qty in requirements.items():
            full_fert_name = fertilizer_mapping.get(fert)
            
            if full_fert_name:
                rate_row = fertilizer_rates[fertilizer_rates['Fertilizer'] == full_fert_name]
                
                if not rate_row.empty:
                    price_per_kg = rate_row.iloc[0]['Price_per_kg']
                    cost = total_qty * price_per_kg
                    fertilizer_cost += cost
                    fertilizer_breakdown.append({
                        "fertilizer": fert,
                        "quantity": round(total_qty, 2),
                        "cost": round(cost, 2),
                        "pricePerKg": round(price_per_kg, 2)
                    })
        
        # Labour Cost
        labour_cost = request.laborCostPerDay * request.noOfLabors
        total_cost = fertilizer_cost + labour_cost
        
        # Prepare recommendations
        recommendations = [
            "Consider splitting nitrogen applications for better efficiency",
            "Apply fertilizers at the right growth stages for optimal uptake",
            "Consider soil pH when selecting fertilizers",
            "Regular soil testing (every 2-3 years) helps maintain nutrient balance"
        ]
        
        if not request.soilNutrientLevelKnown:
            recommendations.insert(0, "For precise recommendations, consider soil nutrient testing")
        
        # Prepare available fertilizer rates for response
        available_rates = []
        for _, row in fertilizer_rates.iterrows():
            available_rates.append({
                "fertilizer": row['Fertilizer'],
                "pricePerKg": round(row['Price_per_kg'], 2),
                "mrpPerBag": row['MRP_Rs_per_bag'],
                "bagSizeKg": row['Bag_Size_kg']
            })
        
        # Prepare response
        response = FertilizerResponse(
            crop=request.cropName,
            area=request.areaInAcres,
            fertilizerCost=round(fertilizer_cost, 2),
            laborCost=round(labour_cost, 2),
            totalCost=round(total_cost, 2),
            fertilizerBreakdown=fertilizer_breakdown,
            recommendations=recommendations,
            availableFertilizerRates=available_rates
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Calculation error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)