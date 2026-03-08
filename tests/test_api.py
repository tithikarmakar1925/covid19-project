from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app, startup_event
import asyncio

async def setup_test_app():
    await startup_event()

asyncio.run(setup_test_app())

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "endpoints" in data

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "model" in data

def test_get_features():
    response = client.get("/features")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["total_features"] == 8

def test_prediction():
    payload = {
        "age": 45,
        "gender": 1,
        "marital_status": 1,
        "employment_status": 1,
        "region": 0,
        "prev_chronic_conditions": 1,
        "allergic_reaction": 0,
        "receiving_immu0therapy": 0
    }
    response = client.post("/predict", json=payload)
    
    if response.status_code != 200:
        print(f"\nStatus Code: {response.status_code}")
        print(f"ERROR: {response.json()}")
        return False
    
    data = response.json()
    assert "risk_level" in data
    assert "probability" in data
    print(f"\nPrediction Result:")
    print(f"  Risk Level: {data['risk_level']}")
    print(f"  Probability: {data['probability']:.1%}")
    return True

def test_get_regions():
    response = client.get("/api/regions")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["total"] == 11

if __name__ == "__main__":
    print("Running API tests...")
    
    try:
        test_root()
        print("Root endpoint: PASSED")
    except Exception as e:
        print(f"Root endpoint: FAILED - {e}")
    
    try:
        test_health_check()
        print("Health check: PASSED")
    except Exception as e:
        print(f"Health check: FAILED - {e}")
    
    try:
        test_get_features()
        print("Features endpoint: PASSED")
    except Exception as e:
        print(f"Features endpoint: FAILED - {e}")
    
    try:
        if test_prediction():
            print("Prediction endpoint: PASSED")
    except Exception as e:
        print(f"Prediction endpoint: FAILED - {e}")
    
    try:
        test_get_regions()
        print("Regions endpoint: PASSED")
    except Exception as e:
        print(f"Regions endpoint: FAILED - {e}")
 
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
 