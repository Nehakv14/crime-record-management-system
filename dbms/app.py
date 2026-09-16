from flask import Flask, render_template, request, redirect, flash, session, url_for, send_file, Response
from models import db, User, bcrypt, StateRecord,CrimeRecord,CrimeFile,PoliceOfficer,Complaint
from config import Config
import os, io, json
from werkzeug.utils import secure_filename
import google.generativeai as genai

genai.configure(api_key="AIzaSyA5dO1JnttrqTVkW1dEQIetUparAAgedxo")
model = genai.GenerativeModel("gemini-2.0-pro-exp")

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = "your_secret_key"

db.init_app(app)
bcrypt.init_app(app)

with app.app_context():
    db.create_all()

# Function to check allowed file type
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"pdf"}

# Load crime data from JSON
with open("crime_data.json", "r") as file:
    crime_data = json.load(file)

# List of states
STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat",
    "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh",
    "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
    "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh",
    "Uttarakhand", "West Bengal"
]


@app.route("/", methods=["GET", "POST"])
@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        form_type = request.form.get("form_type")

        if form_type == "login":
            user_id = request.form["login_id"]
            password = request.form["login_password"]
            selected_role = request.form["login_role"]

            user = User.query.filter_by(id=user_id).first()

            if user and user.check_password(password):
                if user.role == selected_role:
                    session["user_id"] = user.id
                    session["role"] = selected_role

                    # Redirect based on role
                    if selected_role == "user":
                        return redirect(url_for("user_dashboard"))
                    elif selected_role == "police":
                        return redirect(url_for("dashboard"))
                else:
                    flash("Incorrect role selected. Please choose the correct role.", "danger")
            else:
                flash("Invalid ID or Password", "danger")

        elif form_type == "register":
            user_id = request.form["id"]
            name = request.form["name"]
            password = request.form["password"]
            confirm_password = request.form["confirm_password"]
            selected_role = request.form["role"]

            if password != confirm_password:
                flash("Passwords do not match!", "danger")
            elif User.query.filter_by(id=user_id).first():
                flash("ID already registered!", "warning")
            else:
                new_user = User(id=user_id, name=name, role=selected_role)
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()
                flash("Registration Successful! You can now log in.", "success")

    return render_template("signin.html")



@app.route("/user-dashboard")
def user_dashboard():
    # Fetch police officers and files to file a complaint (you can extend this with more details)
    officers = PoliceOfficer.query.all()
    return render_template("user_dashboard.html", officers=officers)



@app.route("/dashboard")
def dashboard():
    # Fetch all state records with PDFs
    state_pdf_entries = {record.state_name: record for record in StateRecord.query.all()}

    # Create a list with all states, ensuring we include those without PDFs
    pdf_entries = [
        {
            "state_name": state,
            "has_pdf": state in state_pdf_entries,  # Check if state has a PDF
        }
        for state in STATES
    ]

    return render_template("dashboard.html", pdf_entries=pdf_entries)

# Delete a crime record and its associated files
@app.route('/delete-crime/<int:crime_id>', methods=['POST'])
def delete_crime(crime_id):
    crime = CrimeRecord.query.get_or_404(crime_id)
    
    # Deletes associated files because of cascade="all, delete-orphan"
    db.session.delete(crime)
    db.session.commit()
    
    flash("Crime record deleted successfully.", "success")
    return redirect(url_for("crime_records"))


# Delete an individual file attached to a crime
@app.route('/delete-file/<int:file_id>', methods=['POST'])
def delete_file(file_id):
    file = CrimeFile.query.get_or_404(file_id)
    db.session.delete(file)
    db.session.commit()
    
    flash("File deleted successfully.", "success")
    return redirect(url_for("crime_records"))



@app.route("/download_pdf/<state_name>")
def download_pdf(state_name):
    record = StateRecord.query.filter_by(state_name=state_name).first()

    if not record or not record.pdf_data:
        return "PDF not found", 404

    return Response(record.pdf_data, mimetype="application/pdf",
                    headers={"Content-Disposition": f"attachment; filename={state_name}.pdf"})



@app.route("/crime/<string:state>")
def state_crime(state):
    state = state.replace("-", " ").title()  # Normalize state names
    data = crime_data.get(state, {})
    return render_template("state_crime.html", state=state, data=data)


@app.route('/crime-records', methods=['GET', 'POST'])
def crime_records():
    if request.method == 'POST':
        crime_type = request.form['crime_type']
        description = request.form['description']
        status = request.form['status']
        officer_id = request.form['officer_id']  # Changed from contact/email to dropdown value

        officer = PoliceOfficer.query.get(officer_id)
        if not officer:
            flash("Officer not found", "danger")
            return redirect(url_for('crime_records'))

        new_crime = CrimeRecord(
            crime_type=crime_type,
            description=description,
            status=status,
            officer_id=officer.id
        )
        db.session.add(new_crime)
        db.session.commit()
        flash("Crime record added successfully", "success")
        return redirect(url_for('crime_records'))

    # GET request
    crimes = CrimeRecord.query.all()
    officers = PoliceOfficer.query.all()  # ✅ Added this line
    files_by_crime = {
        crime.id: CrimeFile.query.filter_by(crime_id=crime.id).all()
        for crime in crimes
    }

    return render_template(
        'crime_records.html',
        crimes=crimes,
        officers=officers,  # ✅ Added this line
        files_by_crime=files_by_crime
    )



@app.route("/download-file/<int:file_id>")
def download_file(file_id):
    file = CrimeFile.query.get(file_id)
    if not file:
        return "File not found", 404
    return Response(
        file.file_data,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={file.filename}"}
    )

request_count = 0


@app.route("/ai-assistant", methods=["GET", "POST"])
def ai_assistant():
    global request_count
    summary = ""
    answer = ""
    input_text = ""
    question = ""

    if request.method == "POST":
        input_text = request.form.get("input_text")
        question = request.form.get("question")

        try:
            if input_text and not question:
                summary = model.generate_content(input_text).text
                request_count += 1
            elif input_text and question:
                summary = model.generate_content(input_text).text
                request_count += 1
                qna_prompt = f"Based on this summary:\n{summary}\n\nAnswer this question:\n{question}"
                answer = model.generate_content(qna_prompt).text
                request_count += 1
        except Exception as e:
            answer = f"Error during AI processing: {e}"

    return render_template(
        "ai_assistant.html",
        summary=summary,
        answer=answer,
        input_text=input_text,
        question=question,
        request_count=request_count
    )


@app.route("/upload-file/<int:crime_id>", methods=["POST"])
def upload_file(crime_id):
    file = request.files.get("file")
    if file:
        new_file = CrimeFile(
            crime_id=crime_id,
            filename=file.filename,
            file_data=file.read()
        )
        db.session.add(new_file)
        db.session.commit()
        flash("File uploaded successfully.", "success")
    else:
        flash("No file selected.", "warning")
    return redirect(url_for("crime_records"))



@app.route("/police-officers")
def police_officers():
    officers = PoliceOfficer.query.all()
    return render_template("police_officers.html", officers=officers)


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("signin"))


@app.route('/complaints')
def complaints():
    complaints_data = Complaint.query.order_by(Complaint.id.asc()).all()
    return render_template('complaints.html', complaints=complaints_data)


@app.route("/file-complaint", methods=["POST"])
def file_complaint():
    if "user_id" not in session or session.get("role") != "user":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("signin"))

    user_id = session["user_id"]
    title = request.form["title"]
    description = request.form["description"]
    location = request.form['location']

    complaint = Complaint(user_id=user_id, title=title, description=description,location=location)
    db.session.add(complaint)
    db.session.commit()

    flash("Complaint submitted successfully.", "success")
    return redirect(url_for("user_dashboard"))


@app.route("/user/complaints")
def user_complaints():
    complaints = Complaint.query.all()
    return render_template("complaints.html", complaints=complaints, user_type="user")

@app.route("/police/complaints")
def police_complaints():
    complaints = Complaint.query.all()
    return render_template("complaints.html", complaints=complaints, user_type="police")

@app.route('/map')
def map_sidebar():
    complaints = Complaint.query.all()
    return render_template('map_sidebar.html', complaints=complaints, show_map=True)

if __name__ == "__main__":
    app.run(debug=True) 


