from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
import joblib

from typing import Dict, List, Optional, Any
import os
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
load_dotenv()

app = FastAPI(
    title="COVID-19 Side Effect Prediction API",
    description="ML API for predicting vaccine side effects with doctor recommendations",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = None
mongodb_client = None
db = None

MONGO_URI = os.getenv("MONGODB_URL")
DB_NAME = os.getenv("DB_NAME")

FEATURE_NAMES = [
    'Age', 'Gender', 'Marital_status', 'Employment_status',
    'Region', 'Prev_chronic_conditions', 'allergic_reaction',
    'receiving_immu0therapy'
]

FEATURE_INFO = {
    'Age': 'Patient age (18-100 years)',
    'Gender': '0=Male, 1=Female',
    'Marital_status': '0=Single, 1=Married, 2=Divorced, 3=Widowed',
    'Employment_status': '0=Unemployed, 1=Employed, 2=Student, 3=Retired',
    'Region': 'Geographic region (0-10)',
    'Prev_chronic_conditions': '0=No, 1=Yes',
    'allergic_reaction': '0=No, 1=Yes',
    'receiving_immu0therapy': '0=No, 1=Yes'
}

REGION_NAMES = {
    0: "Dhaka", 1: "Chittagong", 2: "Rajshahi", 3: "Khulna", 4: "Barisal",
    5: "Sylhet", 6: "Rangpur", 7: "Mymensingh", 8: "Cumilla",
    9: "Gazipur", 10: "Narayanganj"
}

@app.on_event("startup")
async def startup_event():
    global model, mongodb_client, db
    
    try:
        model_path = os.path.join("models", "covid_model_8feature.pkl")
        model = joblib.load(model_path)
        print(f"Model loaded: {type(model).__name__}")
        if hasattr(model, "n_features_in_"):
            print(f"Expected features: {model.n_features_in_}")
    except Exception as e:
        print(f"Model loading error: {e}")
    
    try:
        mongodb_client = AsyncIOMotorClient(MONGO_URI)
        db = mongodb_client[DB_NAME]
        await db.command("ping")
        print(f"MongoDB connected: {DB_NAME}")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        print("MongoDB disconnected")

class PredictionInput(BaseModel):
    age: int = Field(..., ge=18, le=100)
    gender: int = Field(..., ge=0, le=1)
    marital_status: int = Field(..., ge=0, le=3)
    employment_status: int = Field(..., ge=0, le=3)
    region: int = Field(..., ge=0, le=10)
    prev_chronic_conditions: int = Field(..., ge=0, le=1)
    allergic_reaction: int = Field(..., ge=0, le=1)
    receiving_immu0therapy: int = Field(..., ge=0, le=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "age": 45, "gender": 1, "marital_status": 1,
                "employment_status": 1, "region": 0,
                "prev_chronic_conditions": 1, "allergic_reaction": 0,
                "receiving_immu0therapy": 0
            }
        }

class PredictionOutput(BaseModel):
    success: bool
    prediction: int
    risk_level: str
    probability: float
    confidence: float
    feature_importance: Dict[str, float]
    timestamp: str

class DoctorInfo(BaseModel):
    name: str
    specialty: str
    hospital: str
    region: int
    region_name: str
    phone: str
    email: str
    rating: float
    experience_years: int
    languages: List[str]
    consultation_fee: int
    chamber_address: str
    availability: Dict[str, Any]
    qualifications: List[str]
    specializations: List[str]

class DoctorRecommendationOutput(BaseModel):
    success: bool
    count: int
    region: int
    region_name: str
    risk_level: str
    doctors: List[DoctorInfo]

@app.get("/")
async def root():
    return {
        "message": "COVID-19 Vaccine Side Effect Prediction API",
        "version": "2.0.0",
        "status": "running",
        "model_loaded": model is not None,
        "database_connected": db is not None,
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "predict": "/predict",
            "doctors": "/api/doctors",
            "regions": "/api/regions"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model": "loaded" if model is not None else "not loaded",
        "database": "connected" if db is not None else "disconnected",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/features")
async def get_features():
    features_list = [
        {"name": name, "description": FEATURE_INFO.get(name, "")}
        for name in FEATURE_NAMES
    ]
    return {
        "success": True,
        "total_features": len(FEATURE_NAMES),
        "features": features_list
    }

@app.post("/predict", response_model=PredictionOutput)
async def predict(input_data: PredictionInput):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        features_dict = {
            'Age': input_data.age,
            'Gender': input_data.gender,
            'Marital_status': input_data.marital_status,
            'Employment_status': input_data.employment_status,
            'Region': input_data.region,
            'Prev_chronic_conditions': input_data.prev_chronic_conditions,
            'allergic_reaction': input_data.allergic_reaction,
            'receiving_immu0therapy': input_data.receiving_immu0therapy
        }
        
        features_df = pd.DataFrame([features_dict])
        
        prediction = int(model.predict(features_df)[0])
        probabilities = model.predict_proba(features_df)[0]
        side_effect_probability = probabilities[1]
        
        if side_effect_probability > 0.7:
            risk_level = "High Risk"
        elif side_effect_probability > 0.4:
            risk_level = "Moderate Risk"
        else:
            risk_level = "Low Risk"
        
        feature_importance = {}
        if hasattr(model, 'feature_importances_'):
            for name, imp in zip(FEATURE_NAMES, model.feature_importances_):
                feature_importance[name] = float(imp)
        
        return PredictionOutput(
            success=True,
            prediction=prediction,
            risk_level=risk_level,
            probability=float(side_effect_probability),
            confidence=float(max(probabilities)),
            feature_importance=feature_importance,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/api/doctors", response_model=DoctorRecommendationOutput)
async def get_recommended_doctors(
    region: int = Query(..., ge=0, le=10),
    risk_level: str = Query("Moderate Risk"),
    limit: int = Query(5, ge=1, le=10)
):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected")
    
    try:
        if risk_level == "High Risk":
            specialty_filter = {"specialty": "Immunologist"}
        else:
            specialty_filter = {"specialty": {"$in": ["General Physician", "Immunologist"]}}
        
        query = {"region": region, **specialty_filter}
        doctors_cursor = db["doctors"].find(query).sort("rating", -1).limit(limit)
        doctors = await doctors_cursor.to_list(length=limit)
        
        if len(doctors) < 3:
            nearby_regions = [r for r in range(region - 1, region + 2) if 0 <= r <= 10]
            query = {"region": {"$in": nearby_regions}, **specialty_filter}
            doctors_cursor = db["doctors"].find(query).sort("rating", -1).limit(limit)
            doctors = await doctors_cursor.to_list(length=limit)
        
        doctor_list = [
            DoctorInfo(
                name=doc["name"],
                specialty=doc["specialty"],
                hospital=doc["hospital"],
                region=doc["region"],
                region_name=REGION_NAMES.get(doc["region"], "Unknown"),
                phone=doc["phone"],
                email=doc["email"],
                rating=doc["rating"],
                experience_years=doc["experience_years"],
                languages=doc["languages"],
                consultation_fee=doc["consultation_fee"],
                chamber_address=doc["chamber_address"],
                availability=doc["availability"],
                qualifications=doc["qualifications"],
                specializations=doc["specializations"]
            )
            for doc in doctors
        ]
        
        return DoctorRecommendationOutput(
            success=True,
            count=len(doctor_list),
            region=region,
            region_name=REGION_NAMES.get(region, "Unknown"),
            risk_level=risk_level,
            doctors=doctor_list
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch doctors: {str(e)}")

@app.get("/api/regions")
async def get_regions():
    regions_list = [{"code": code, "name": name} for code, name in REGION_NAMES.items()]
    return {"success": True, "total": len(regions_list), "regions": regions_list}