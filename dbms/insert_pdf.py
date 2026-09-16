from app import app, db  
from models import StateRecord
import os

def insert_pdf(state_name, pdf_path):
    with app.app_context():  # Ensure the app context is active
        if not os.path.exists(pdf_path):
            print(f"Error: PDF file not found at {pdf_path}")
            return
        
        with open(pdf_path, "rb") as file:
            pdf_content = file.read()  # Read the file in binary mode

        existing_entry = StateRecord.query.get(state_name)  # Fetch by correct column name

        if existing_entry:
            existing_entry.pdf_data = pdf_content  # Update existing entry
        else:
            new_entry = StateRecord(state_name=state_name, pdf_data=pdf_content)  # Corrected column names
            db.session.add(new_entry)

        db.session.commit()
        print(f"PDF for {state_name} inserted successfully!")

# Example usage
insert_pdf("Andhra Pradesh", r"C:\Users\stran\Downloads\andhrapdf.pdf")
insert_pdf("Arunachal Pradesh",r"C:\Users\stran\Downloads\arunachal pradesh.pdf")
insert_pdf("Assam", r"C:\Users\stran\Downloads\crime_data-dec-2020.pdf")
insert_pdf("Bihar", r"C:\Users\stran\Downloads\Crime in Bihar.pdf")
insert_pdf("Chhattisgarh", r"C:\Users\stran\Downloads\ipc-crime-during-year-2020-2021.pdf")
insert_pdf("Goa", r"C:\Users\stran\Downloads\goa.pdf")
insert_pdf("Gujarat", r"C:\Users\stran\Downloads\JETIR2501553.pdf")
insert_pdf("Haryana", r"C:\Users\stran\Downloads\JSS-55-1-3-001-18-2223-Sharma-M-Tx1.pmd.pdf")
insert_pdf("Himachal Pradesh", r"C:\Users\stran\Downloads\CrimeReview-2013.pdf")
insert_pdf("Jharkhand", r"C:\Users\stran\Downloads\CrimeReview-2013.pdf")
insert_pdf("Karnataka", r"C:\Users\stran\Downloads\karnataka.pdf")
insert_pdf("Kerala", r"C:\Users\stran\Downloads\kerala.pdf")
insert_pdf("Madhya Pradesh", r"C:\Users\stran\Downloads\mp.pdf")
insert_pdf("Maharashtra", r"C:\Users\stran\Downloads\mp.pdf")
insert_pdf("Manipur", r"C:\Users\stran\Downloads\mp.pdf")
insert_pdf("Meghalaya", r"C:\Users\stran\Downloads\mp.pdf")

insert_pdf("Mizoram", r"C:\Users\stran\Downloads\mp.pdf")
insert_pdf("Nagaland", r"C:\Users\stran\Downloads\mp.pdf")
insert_pdf("Odisha", r"C:\Users\stran\Downloads\mp.pdf")
insert_pdf("Punjab", r"C:\Users\stran\Downloads\mp.pdf")
insert_pdf("Rajasthan", r"C:\Users\stran\Downloads\mp.pdf")
insert_pdf("Sikkim", r"C:\Users\stran\Downloads\mp.pdf")
insert_pdf("Tamil Nadu", r"C:\Users\stran\Downloads\mp.pdf")
insert_pdf("Telangana", r"C:\Users\stran\Downloads\mp.pdf")
insert_pdf("Tripura", r"C:\Users\stran\Downloads\mp.pdf")
insert_pdf("Uttar Pradesh", r"C:\Users\stran\Downloads\mp.pdf")
insert_pdf("Uttarakhand", r"C:\Users\stran\Downloads\mp.pdf")
insert_pdf("West Bengal", r"C:\Users\stran\Downloads\mp.pdf")






