from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from datetime import datetime
import os

class PDFReportGenerator:
    
    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_report(
        self,
        patient_data: dict,
        prediction_result: dict,
        doctors: list,
        filename: str = None
    ) -> str:
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"covid_report_{timestamp}.pdf"
        
        filepath = os.path.join(self.output_dir, filename)
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4
        
        y_position = height - 50
        
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, y_position, "COVID-19 Vaccine Side Effect Report")
        y_position -= 30
        
        c.setFont("Helvetica", 10)
        c.drawString(50, y_position, f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        y_position -= 40
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, "Patient Information")
        y_position -= 20
        
        c.setFont("Helvetica", 11)
        patient_info = [
            f"Age: {patient_data.get('age')} years",
            f"Gender: {'Female' if patient_data.get('gender') == 1 else 'Male'}",
            f"Region: {patient_data.get('region_name', 'N/A')}",
            f"Chronic Conditions: {'Yes' if patient_data.get('prev_chronic_conditions') == 1 else 'No'}",
            f"Allergies: {'Yes' if patient_data.get('allergic_reaction') == 1 else 'No'}"
        ]
        
        for info in patient_info:
            c.drawString(70, y_position, info)
            y_position -= 18
        
        y_position -= 20
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, "Risk Assessment")
        y_position -= 20
        
        risk_level = prediction_result.get('risk_level', 'Unknown')
        probability = prediction_result.get('probability', 0) * 100
        
        if risk_level == "High Risk":
            color = colors.red
        elif risk_level == "Moderate Risk":
            color = colors.orange
        else:
            color = colors.green
        
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(70, y_position, f"{risk_level}: {probability:.1f}%")
        c.setFillColor(colors.black)
        y_position -= 30
        
        c.setFont("Helvetica", 11)
        c.drawString(70, y_position, f"Confidence: {prediction_result.get('confidence', 0) * 100:.1f}%")
        y_position -= 30
        
        if doctors and len(doctors) > 0:
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y_position, "Recommended Doctors")
            y_position -= 20
            
            for idx, doctor in enumerate(doctors[:3], 1):
                c.setFont("Helvetica-Bold", 11)
                c.drawString(70, y_position, f"{idx}. Dr. {doctor.get('name')}")
                y_position -= 15
                
                c.setFont("Helvetica", 10)
                c.drawString(90, y_position, f"Specialty: {doctor.get('specialty')}")
                y_position -= 13
                c.drawString(90, y_position, f"Hospital: {doctor.get('hospital')}")
                y_position -= 13
                c.drawString(90, y_position, f"Phone: {doctor.get('phone')}")
                y_position -= 13
                c.drawString(90, y_position, f"Fee: {doctor.get('consultation_fee')} BDT")
                y_position -= 20
        
        y_position -= 20
        c.setFont("Helvetica-Italic", 9)
        c.drawString(50, y_position, "Disclaimer: This report is for informational purposes only.")
        y_position -= 12
        c.drawString(50, y_position, "Please consult with a qualified healthcare provider for medical advice.")
        
        c.showPage()
        c.save()
        
        return filepath

pdf_generator = PDFReportGenerator()