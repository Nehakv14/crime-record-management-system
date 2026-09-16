from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique ID
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user') 

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def is_police(self):
        return self.role == 'police'  # Helper method to check if the user is a police officer
    
    complaints = db.relationship("Complaint", back_populates="user")

class StateRecord(db.Model):  # Make sure the class name matches the database table
    __tablename__ = "state_pdfs"  # Your table name

    state_name = db.Column(db.String(255), primary_key=True)  # Corrected column name
    pdf_data = db.Column(db.LargeBinary, nullable=False)  


class CrimeFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crime_id = db.Column(db.Integer, db.ForeignKey('crime_record.id'), nullable=False)
    filename = db.Column(db.String(255))
    file_data = db.Column(db.LargeBinary, nullable=False)


class PoliceOfficer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100), nullable=False)
    photo_filename = db.Column(db.String(255))
    def __repr__(self):
        return f'<PoliceOfficer {self.name}>'


class CrimeRecord(db.Model):
    __tablename__ = "crime_record"
    id = db.Column(db.Integer, primary_key=True)
    crime_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(100), default="Pending")

    officer_id = db.Column(db.Integer, db.ForeignKey("police_officer.id"), nullable=False)

    # Relationship to PoliceOfficer
    officer = db.relationship("PoliceOfficer", backref="crime_records")

    # Related files
    files = db.relationship("CrimeFile", backref="crime", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<CrimeRecord {self.crime_type} by Officer {self.officer.name}>'


from sqlalchemy import Integer, ForeignKey

class Complaint(db.Model):
    __tablename__ = 'complaint'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign Key linking to User table
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default="Pending")
    timestamp = db.Column(db.DateTime, default=db.func.now())
    location = db.Column(db.String(255), nullable=True)

    
    # Establish reverse relationship with User
    user = db.relationship("User", back_populates="complaints")
    
    @property
    def username(self):
        return self.user.name  