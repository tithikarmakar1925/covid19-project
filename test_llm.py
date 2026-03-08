

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print(" Loading modules...")

try:
    from app.local_llm import llm_service
    print(" LLM service imported successfully")
except ImportError as e:
    print(f" Import error: {e}")
    print("\n Make sure you're in E:\\Covid19\\ml-api folder")
    print("   And app/local_llm.py exists")
    sys.exit(1)

async def test_extraction():
    """Test feature extraction"""

    print(" TEST 1: FEATURE EXTRACTION FROM NATURAL LANGUAGE")
 
    
    test_cases = [
        "I am a 45 year old female with diabetes. I have fever and headache.",
        "Male patient, 32 years old, no allergies, feeling tired after vaccine.",
        "60 year old woman with high blood pressure and allergic reactions history."
    ]
    
    for i, text in enumerate(test_cases, 1):
       
        print(f"Test Case {i}:")
        print(f"Input: '{text}'")
        print()
        
        try:
            features = await llm_service.extract_features(text)
            
            print("Extracted Features:")
            print(f"  ├─ Age: {features.get('age', 'Unknown')}")
            gender_map = {0: 'Male', 1: 'Female', None: 'Unknown'}
            print(f"  ├─ Gender: {gender_map.get(features.get('gender'), 'Unknown')}")
            print(f"  ├─ Chronic Disease: {'Yes ' if features.get('has_chronic_disease') else 'No ✓'}")
            print(f"  ├─ Allergies: {'Yes ' if features.get('has_allergies') else 'No ✓'}")
            symptoms = features.get('symptoms', [])
            print(f"  └─ Symptoms: {', '.join(symptoms) if symptoms else 'None detected'}")
            
        except Exception as e:
            print(f" Error: {e}")
    


async def test_advice():
    """Test medical advice generation"""
  
    print("💡 TEST 2: MEDICAL ADVICE GENERATION")
 
    
    test_cases = [
        {
            "symptoms": "mild fever and body aches after vaccination",
            "risk_level": "Low Risk",
            "probability": 0.25
        },
        {
            "symptoms": "severe headache with existing chronic disease",
            "risk_level": "Moderate Risk",
            "probability": 0.55
        },
        {
            "symptoms": "multiple symptoms with history of allergic reactions",
            "risk_level": "High Risk",
            "probability": 0.78
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        
        print(f"Test Case {i}:")
        print(f"Symptoms: {case['symptoms']}")
        print(f"Risk Assessment: {case['risk_level']} ({case['probability']:.1%} probability)")
        print()
        
        try:
            advice = await llm_service.generate_advice(
                case['symptoms'],
                case['risk_level'],
                case['probability']
            )
            
            print("Generated Medical Advice:")
            
            # Print advice with nice formatting
            for line in advice.split('\n'):
                if line.strip():
                    print(f"  {line}")
            print()
            
        except Exception as e:
            print(f" Error: {e}")
    


async def main():
    """Main test function"""
 
    print("   TESTING LOCAL LLM SERVICE (Qwen 2.5 0.5B)")

    
    print(" System Information:")
    print(f"  ├─ Python: {sys.version.split()[0]}")
    print(f"  ├─ Working Directory: {os.getcwd()}")
    print(f"  └─ LLM Model Loaded: {'Yes ✓' if llm_service.model_loaded else 'No (Fallback mode) '}")
    
    try:
        # Test 1: Feature Extraction
        await test_extraction()
        
        # Test 2: Advice Generation
        await test_advice()
        
        # Summary
       
        print("   ALL TESTS COMPLETED SUCCESSFULLY!")
        
        
        print(" Next Steps:")
        print("  1. Start API: uvicorn app.main:app --reload")
        print("  2. Open browser: http://localhost:8000/docs")
        print("  3. Test /api/analyze endpoint with sample data")
        print()
        
    except Exception as e:
        print(f"\n Test failed: {e}")
        import traceback
        traceback.print_exc()
        
    # Test 3: Doctor Recommendations (NEW!)
    print("\n" + "="*70)
    print(" TEST 3: DOCTOR RECOMMENDATION SYSTEM")
    print("="*70)
    
    # Sample doctors (you'll get from MongoDB later)
    sample_doctors = [
        {
            "name": "Dr. Ahmed Rahman",
            "specialty": "General Physician",
            "hospital": "Dhaka Medical College Hospital",
            "phone": "01711-123456",
            "location": "Dhaka",
            "rating": 4.5
        },
        {
            "name": "Dr. Fatima Begum",
            "specialty": "Immunologist",
            "hospital": "Square Hospital",
            "phone": "01812-234567",
            "location": "Dhaka",
            "rating": 4.8
        },
        {
            "name": "Dr. Kamal Hossain",
            "specialty": "Cardiologist",
            "hospital": "United Hospital",
            "phone": "01913-345678",
            "location": "Dhaka",
            "rating": 4.7
        }
    ]
    
    print("\n Available Doctors:")
    for doc in sample_doctors:
        print(f"\n   {doc['name']}")
        print(f"     Specialty: {doc['specialty']}")
        print(f"     Hospital: {doc['hospital']}")
        print(f"     Phone: {doc['phone']}")
        print(f"     Location: {doc['location']}")
        print(f"     Rating:  {doc['rating']}/5.0")
    
         

if __name__ == "__main__":
    print("\n Starting tests (this may take a few seconds)...\n")
    asyncio.run(main())