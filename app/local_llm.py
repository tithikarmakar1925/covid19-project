import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import json
import re
import asyncio
import os
from typing import Dict
from dotenv import load_dotenv
load_dotenv()

class LocalLLMService:

    def __init__(self):
        print("\n" + "="*60)
        print("Loading Local LLM (Qwen 2.5 0.5B)...")
        print("="*60)
        
        self.model_name = os.getenv(
            "LLM_MODEL", 
            "Qwen/Qwen2.5-0.5B-Instruct"
        )
        
        try:
            print(f"Model: {self.model_name}")
            print(f"First time? Downloading model (~1GB)...")
            print(f"   Location: C:\\Users\\{os.getenv('USERNAME')}\\.cache\\huggingface\\")
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32,
                device_map="cpu",
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            print("Model loaded successfully!")
            print(f"Device: CPU")
            print(f"Memory: ~1GB RAM")
            print("="*60 + "\n")
            
            self.model_loaded = True
            
        except Exception as e:
            print(f"Model loading failed: {e}")
            print("Using fallback mode (rule-based extraction)")
            print("LLM features will use pattern matching instead")
            print("="*60 + "\n")
            self.model_loaded = False
    
    async def extract_features(self, symptoms_text: str) -> Dict:
        
        print(f"\nExtracting features from: '{symptoms_text[:100]}...'")
        
        if not self.model_loaded:
            print("Using fallback extraction (rule-based)")
            return self._fallback_extraction(symptoms_text)
        
        prompt = f"""You are a medical data extraction expert. Extract patient information CAREFULLY.

Patient says: "{symptoms_text}"

CRITICAL GENDER RULES:
- Look for these EXACT keywords:
  * FEMALE indicators: female, woman, girl, she, her, lady, mom, mother, wife → return 1
  * MALE indicators: male, man, boy, he, his, gentleman, dad, father, husband → return 0
  * If NO gender words found → return null
- Age: Find number between 18-100 (look for "X years old", "age X", "X yr")
- Chronic disease: diabetes, hypertension, asthma, heart disease → true
- Allergies: allergy, allergic, reaction → true

Return ONLY valid JSON (no extra text):
{{
  "age": <number or null>,
  "gender": <0 or 1 or null>,
  "has_chronic_disease": <true or false>,
  "has_allergies": <true or false>,
  "symptoms": ["fever", "pain"]
}}

JSON:"""

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                self._generate_text,
                prompt,
                150
            )
            
            print(f"   LLM Response: {response[:100]}...")
            
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                extracted = json.loads(json_match.group())
                
                if extracted.get('gender') is None:
                    text_lower = symptoms_text.lower()
                    female_kw = ['female', 'woman', 'girl', 'she', 'her', 'lady', 'mom', 'mother', 'wife']
                    male_kw = ['male', 'man', 'boy', 'he', 'his', 'gentleman', 'dad', 'father', 'husband']
                    
                    if any(kw in text_lower for kw in female_kw):
                        extracted['gender'] = 1
                        print("   Gender auto-detected: Female (1)")
                    elif any(kw in text_lower for kw in male_kw):
                        extracted['gender'] = 0
                        print("   Gender auto-detected: Male (0)")
                
                validated = self._validate_features(extracted)
                print(f"Extracted: Age={validated['age']}, Gender={validated['gender']}, Symptoms={len(validated['symptoms'])}")
                return validated
            else:
                print("JSON parsing failed, using fallback")
                return self._fallback_extraction(symptoms_text)
                
        except Exception as e:
            print(f"LLM error: {e}")
            return self._fallback_extraction(symptoms_text)
    
    async def generate_advice(
        self, 
        symptoms: str, 
        risk_level: str, 
        probability: float
    ) -> str:
 
        print(f"\nGenerating advice for {risk_level} ({probability:.1%} probability)")
        
        if not self.model_loaded:
            print("Using fallback advice (template-based)")
            return self._fallback_advice(risk_level, probability)
        
        prompt = f"""You are a medical advisor. Write brief patient guidance.

Patient symptoms: {symptoms}
Risk level: {risk_level} ({probability:.1%})

Write EXACTLY 4-5 short sentences:
1. Explain what {risk_level} means in simple terms
2. Immediate action patient should take
3. When to see a doctor
4. One specific preventive tip

STRICT RULES:
- NO signatures, NO names, NO email addresses
- NO medication prescriptions or drug names
- NO placeholders like [Your Name] or [Contact]
- Total length: 150-200 words maximum
- Use simple language, be direct

Medical Advice:"""

        try:
            loop = asyncio.get_event_loop()
            advice = await loop.run_in_executor(
                None,
                self._generate_text,
                prompt,
                200
            )
            
            advice = advice.strip()
            
            advice = re.sub(r'\[.*?\]', '', advice)
            advice = re.sub(r'\{.*?\}', '', advice)
            advice = re.sub(r'(?i)(sincerely|regards|best wishes).*', '', advice, flags=re.DOTALL)
            advice = re.sub(r'(?i)(dr\.|doctor|consultant)[\s\w]+$', '', advice)
            advice = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '', advice)
            advice = re.sub(r'\+?\d[\d\-\s]{8,}', '', advice)
            advice = re.sub(r'[-=_]{3,}', '', advice)
            advice = re.sub(r'(?i)note:.*$', '', advice, flags=re.DOTALL)
            advice = re.sub(r'(?i)disclaimer:.*$', '', advice, flags=re.DOTALL)
            advice = re.sub(r'\s+', ' ', advice).strip()
            
            if len(advice) < 50 or len(advice) > 800:
                print(f"    Advice length issue ({len(advice)} chars), using fallback")
                return self._fallback_advice(risk_level, probability)
            
            if any(bad in advice for bad in ['[', '{', 'Your Name', 'Contact', '@']):
                print("    Artifacts detected, using fallback")
                return self._fallback_advice(risk_level, probability)
            
            print(f"    Clean advice: {len(advice)} characters")
            return advice
            
        except Exception as e:
            print(f"    Advice generation error: {e}")
            return self._fallback_advice(risk_level, probability)
    
    def _generate_text(self, prompt: str, max_tokens: int = 200) -> str:

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )
        
        with torch.no_grad(): 
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=0.3,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.1,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        generated_text = self.tokenizer.decode(
            outputs[0], 
            skip_special_tokens=True
        )
        
        response = generated_text[len(prompt):].strip()
        
        return response
    
    def _fallback_extraction(self, symptoms_text: str) -> Dict:
        
        text_lower = symptoms_text.lower()
        
        age = None
        age_patterns = [
            r'\b(\d{1,3})\s*(?:years? old|yr|y\.o\.)',
            r'\bage[:\s]+(\d{1,3})',
            r'\b(\d{1,3})\s*(?:year|yr)',
        ]
        for pattern in age_patterns:
            match = re.search(pattern, text_lower)
            if match:
                age_value = int(match.group(1))
                if 18 <= age_value <= 100:
                    age = age_value
                    break
        
        gender = None
        female_keywords = ['female', 'woman', 'girl', 'she', 'her', 'lady', 'mom', 'mother', 'wife']
        male_keywords = ['male', 'man', 'boy', 'he', 'his', 'gentleman', 'dad', 'father', 'husband']
        
        if any(kw in text_lower for kw in female_keywords):
            gender = 1
        elif any(kw in text_lower for kw in male_keywords):
            gender = 0
        
        chronic_keywords = [
            'diabetes', 'diabetic', 'sugar',
            'hypertension', 'blood pressure', 'bp',
            'asthma', 'heart disease', 'cardiac',
            'chronic', 'kidney disease', 'liver disease'
        ]
        has_chronic = any(kw in text_lower for kw in chronic_keywords)
        
        allergy_keywords = [
            'allergy', 'allergic', 'allergies',
            'reaction', 'sensitive', 'sensitivity'
        ]
        has_allergies = any(kw in text_lower for kw in allergy_keywords)
        
        symptom_keywords = [
            'fever', 'temperature', 'pain', 'headache', 
            'fatigue', 'tired', 'weakness', 'cough',
            'breathless', 'breathing', 'nausea', 'vomit',
            'dizziness', 'dizzy', 'swelling', 'rash',
            'ache', 'sore', 'chills', 'shiver'
        ]
        symptoms = [s for s in symptom_keywords if s in text_lower]
        
        return {
            "age": age,
            "gender": gender,
            "has_chronic_disease": has_chronic,
            "has_allergies": has_allergies,
            "symptoms": symptoms
        }
    
    def _fallback_advice(self, risk_level: str, probability: float) -> str:

        advice_templates = {
            "High Risk": f"""Based on your health profile, our assessment indicates a HIGH RISK of vaccine side effects (probability: {probability:.1%}).

What this means: There is a significant likelihood that you may experience vaccine-related side effects given your current health conditions.

What you should do:
- Schedule a medical consultation WITHIN 24 HOURS before proceeding with vaccination
- Discuss your complete medical history with your doctor
- Your healthcare provider may recommend specific preventive measures or alternative vaccination strategies

When to seek help: If you experience severe symptoms like difficulty breathing, chest pain, or severe allergic reactions after vaccination, seek emergency medical care immediately.

Note: This is a risk assessment based on statistical analysis. Only a qualified healthcare provider can give personalized medical advice.""",

            "Moderate Risk": f"""Your assessment indicates a MODERATE RISK of vaccine side effects (probability: {probability:.1%}).

What this means: You may experience some side effects, but they are typically manageable with proper care and monitoring.

What you should do:
- Consult with a healthcare provider before vaccination to discuss your health profile
- Inform the vaccination staff about any existing medical conditions
- Plan to rest for 24-48 hours after vaccination
- Have basic medications (like paracetamol) available as prescribed by your doctor

When to see a doctor: If side effects are severe or last more than 3 days, or if you develop concerning symptoms like high fever (>102°F), persistent vomiting, or breathing difficulties.

Preventive tip: Stay well-hydrated, get adequate rest, and avoid strenuous activities for 48 hours post-vaccination.""",

            "Low Risk": f"""Your assessment shows a LOW RISK of vaccine side effects (probability: {probability:.1%}).

What this means: You have a lower likelihood of experiencing significant vaccine side effects. This is encouraging!

What you should do:
- You can proceed with vaccination as scheduled
- Still inform medical staff about any health conditions or medications
- Monitor yourself for any unusual symptoms for 24-48 hours after vaccination
- Stay hydrated and well-rested

Normal reactions: Mild soreness at injection site, slight fatigue, or low-grade fever are normal immune responses and typically resolve within 1-2 days.

When to seek help: If you develop symptoms that concern you or persist beyond 3 days, consult with a healthcare provider for peace of mind.

Remember: Even with low risk, everyone's body responds differently. Listen to your body and don't hesitate to seek medical advice if needed."""
        }
        
        return advice_templates.get(
            risk_level, 
            "Please consult a healthcare provider for personalized medical guidance."
        )
    
    def _validate_features(self, features: Dict) -> Dict:

        validated = {
            "age": None,
            "gender": None,
            "has_chronic_disease": False,
            "has_allergies": False,
            "symptoms": []
        }
        
        if isinstance(features.get("age"), (int, float)):
            age = int(features["age"])
            if 18 <= age <= 100:
                validated["age"] = age
        
        if features.get("gender") in [0, 1]:
            validated["gender"] = features["gender"]
        elif features.get("gender") is None:
            validated["gender"] = None
        
        validated["has_chronic_disease"] = bool(features.get("has_chronic_disease", False))
        validated["has_allergies"] = bool(features.get("has_allergies", False))
        
        if isinstance(features.get("symptoms"), list):
            validated["symptoms"] = [
                str(s) for s in features["symptoms"] 
                if isinstance(s, str)
            ]
        
        return validated

print("\nInitializing Local LLM Service...")
llm_service = LocalLLMService()