from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Patient(db.Model):
    __tablename__ = 'patients'
    
    patient_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(50))
    address = db.Column(db.Text)
    phone = db.Column(db.String(50))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='patient', lazy=True)
    medical_notes = db.relationship('MedicalNote', backref='patient', lazy=True)

    def __repr__(self):
        return f'<Patient {self.first_name} {self.last_name}>'

    def to_dict(self):
        return {
            'patient_id': self.patient_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'address': self.address,
            'phone': self.phone,
            'email': self.email
        }

class Doctor(db.Model):
    __tablename__ = 'doctors'
    
    doctor_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    specialty = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)
    medical_notes = db.relationship('MedicalNote', backref='doctor', lazy=True)

    def __repr__(self):
        return f'<Doctor {self.first_name} {self.last_name}>'

    def to_dict(self):
        return {
            'doctor_id': self.doctor_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'specialty': self.specialty,
            'phone': self.phone,
            'email': self.email
        }

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    appointment_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Appointment {self.appointment_id}>'

    def to_dict(self):
        return {
            'appointment_id': self.appointment_id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'appointment_time': self.appointment_time.isoformat() if self.appointment_time else None,
            'reason': self.reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'patient_name': f"{self.patient.first_name} {self.patient.last_name}" if self.patient else None,
            'doctor_name': f"{self.doctor.first_name} {self.doctor.last_name}" if self.doctor else None
        }

class MedicalNote(db.Model):
    __tablename__ = 'medical_notes'
    
    note_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'), nullable=False)
    note_date = db.Column(db.Date, nullable=False)
    note_details = db.Column(db.Text)
    medication = db.Column(db.Text)
    treatment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<MedicalNote {self.note_id}>'

    def to_dict(self):
        return {
            'note_id': self.note_id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'note_date': self.note_date.isoformat() if self.note_date else None,
            'note_details': self.note_details,
            'medication': self.medication,
            'treatment': self.treatment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'patient_name': f"{self.patient.first_name} {self.patient.last_name}" if self.patient else None,
            'doctor_name': f"{self.doctor.first_name} {self.doctor.last_name}" if self.doctor else None
        }
