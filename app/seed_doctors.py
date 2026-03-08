# ml-api/app/seed_doctors.py

from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

REGIONS = {
    0: "Dhaka",
    1: "Chittagong", 
    2: "Rajshahi",
    3: "Khulna",
    4: "Barisal",
    5: "Sylhet",
    6: "Rangpur",
    7: "Mymensingh",
    8: "Cumilla",
    9: "Gazipur",
    10: "Narayanganj"
}

DOCTORS_DATA = [
    {
        "name": "Dr. Ahmed Rahman",
        "specialty": "General Physician",
        "hospital": "Dhaka Medical College Hospital",
        "region": 0,
        "phone": "+880-1712-345678",
        "email": "dr.ahmed@dmch.gov.bd",
        "rating": 4.7,
        "experience_years": 15,
        "languages": ["Bengali", "English"],
        "consultation_fee": 500,
        "chamber_address": "Secretariat Road, Dhaka 1000",
        "availability": {
            "days": ["Saturday", "Sunday", "Monday", "Wednesday"],
            "hours": "5:00 PM - 9:00 PM"
        },
        "qualifications": ["MBBS (DMC)", "FCPS (Medicine)"],
        "specializations": ["General Medicine", "Vaccine Counseling"]
    },
    {
        "name": "Dr. Fatema Begum",
        "specialty": "Immunologist",
        "hospital": "Bangabandhu Sheikh Mujib Medical University",
        "region": 0,
        "phone": "+880-1812-234567",
        "email": "dr.fatema@bsmmu.edu.bd",
        "rating": 4.9,
        "experience_years": 20,
        "languages": ["Bengali", "English", "Hindi"],
        "consultation_fee": 1200,
        "chamber_address": "Shahbag, Dhaka 1000",
        "availability": {
            "days": ["Tuesday", "Thursday", "Saturday"],
            "hours": "4:00 PM - 8:00 PM"
        },
        "qualifications": ["MBBS (DMC)", "MD (Immunology)", "PhD"],
        "specializations": ["Clinical Immunology", "Allergy Management", "Vaccine Safety"]
    },
    {
        "name": "Dr. Kamal Hossain",
        "specialty": "General Physician",
        "hospital": "Square Hospital",
        "region": 0,
        "phone": "+880-1912-345678",
        "email": "dr.kamal@squarehospital.com",
        "rating": 4.6,
        "experience_years": 12,
        "languages": ["Bengali", "English"],
        "consultation_fee": 800,
        "chamber_address": "18/F Bir Uttam Qazi Nuruzzaman Sarak, Dhaka 1205",
        "availability": {
            "days": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"],
            "hours": "10:00 AM - 2:00 PM"
        },
        "qualifications": ["MBBS (DMC)", "FCPS (Medicine)"],
        "specializations": ["Internal Medicine", "Preventive Healthcare"]
    },
    {
        "name": "Dr. Nur Islam Chowdhury",
        "specialty": "General Physician",
        "hospital": "Chittagong Medical College Hospital",
        "region": 1,
        "phone": "+880-1712-456789",
        "email": "dr.nur@cmch.gov.bd",
        "rating": 4.5,
        "experience_years": 18,
        "languages": ["Bengali", "English"],
        "consultation_fee": 400,
        "chamber_address": "Panchlaish, Chittagong",
        "availability": {
            "days": ["Saturday", "Sunday", "Monday", "Wednesday", "Friday"],
            "hours": "6:00 PM - 9:00 PM"
        },
        "qualifications": ["MBBS (CMC)", "MD (Medicine)"],
        "specializations": ["General Medicine", "Chronic Disease Management"]
    },
    {
        "name": "Dr. Ayesha Siddique",
        "specialty": "Immunologist",
        "hospital": "Chevron Clinical Laboratory",
        "region": 1,
        "phone": "+880-1812-567890",
        "email": "dr.ayesha@chevron.com.bd",
        "rating": 4.8,
        "experience_years": 14,
        "languages": ["Bengali", "English"],
        "consultation_fee": 900,
        "chamber_address": "Agrabad, Chittagong",
        "availability": {
            "days": ["Tuesday", "Thursday", "Saturday"],
            "hours": "5:00 PM - 8:00 PM"
        },
        "qualifications": ["MBBS (CMC)", "MD (Immunology)"],
        "specializations": ["Allergy Testing", "Immunotherapy", "Vaccine Counseling"]
    },
    {
        "name": "Dr. Hasibul Alam",
        "specialty": "General Physician",
        "hospital": "Rajshahi Medical College Hospital",
        "region": 2,
        "phone": "+880-1912-678901",
        "email": "dr.hasib@rmch.gov.bd",
        "rating": 4.4,
        "experience_years": 10,
        "languages": ["Bengali"],
        "consultation_fee": 350,
        "chamber_address": "Laxmipur, Rajshahi",
        "availability": {
            "days": ["Saturday", "Sunday", "Monday", "Wednesday", "Friday"],
            "hours": "5:00 PM - 8:00 PM"
        },
        "qualifications": ["MBBS (RMC)", "FCPS (Medicine)"],
        "specializations": ["General Medicine", "Family Healthcare"]
    },
    {
        "name": "Dr. Shamima Akter",
        "specialty": "General Physician",
        "hospital": "Khulna Medical College Hospital",
        "region": 3,
        "phone": "+880-1712-789012",
        "email": "dr.shamima@kmch.gov.bd",
        "rating": 4.6,
        "experience_years": 13,
        "languages": ["Bengali", "English"],
        "consultation_fee": 400,
        "chamber_address": "South Central Road, Khulna",
        "availability": {
            "days": ["Saturday", "Sunday", "Tuesday", "Thursday"],
            "hours": "6:00 PM - 9:00 PM"
        },
        "qualifications": ["MBBS (KMC)", "MD (Medicine)"],
        "specializations": ["Internal Medicine", "Women's Health"]
    },
    {
        "name": "Dr. Rafiqul Islam",
        "specialty": "Immunologist",
        "hospital": "Sylhet MAG Osmani Medical College",
        "region": 5,
        "phone": "+880-1812-890123",
        "email": "dr.rafiq@somch.gov.bd",
        "rating": 4.7,
        "experience_years": 16,
        "languages": ["Bengali", "English", "Sylheti"],
        "consultation_fee": 700,
        "chamber_address": "Jalalabad, Sylhet",
        "availability": {
            "days": ["Sunday", "Monday", "Wednesday", "Friday"],
            "hours": "5:00 PM - 8:00 PM"
        },
        "qualifications": ["MBBS (SOMCH)", "MD (Immunology)", "FCPS"],
        "specializations": ["Clinical Immunology", "Infectious Diseases"]
    }
]

def seed_doctors():
    mongo_uri = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
    db_name = os.getenv("DB_NAME", "covid_db")
    
    try:
        client = MongoClient(mongo_uri)
        db = client[db_name]
        doctors_collection = db["doctors"]
        
        doctors_collection.delete_many({})
        print(f"Cleared existing doctor data from {db_name}")
        
        result = doctors_collection.insert_many(DOCTORS_DATA)
        print(f"Inserted {len(result.inserted_ids)} doctors successfully")
        
        doctors_collection.create_index("region")
        doctors_collection.create_index("specialty")
        doctors_collection.create_index([("rating", -1)])
        doctors_collection.create_index("hospital")
        print("Created database indexes")
        
        print("\nDoctor database seeded successfully")
        print(f"Database: {db_name}")
        print(f"Collection: doctors")
        print(f"Total records: {doctors_collection.count_documents({})}")
        
    except Exception as e:
        print(f"Error seeding doctors: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    seed_doctors()