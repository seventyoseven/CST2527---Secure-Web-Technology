from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import bcrypt
from src.models.user import db, Patient, Doctor
from src.security_config import (
    rate_limit, validate_input, validate_password_strength, 
    sanitize_input, log_security_event, check_suspicious_activity
)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register/patient', methods=['POST'])
@rate_limit(max_requests=5, window_minutes=15)  # Limit registration attempts
def register_patient():
    data = request.get_json()
    
    # Sanitize input data
    data = sanitize_input(data)
    
    # Validate input
    validation_errors = validate_input(
        data, 
        required_fields=['first_name', 'last_name', 'email', 'password'],
        email_fields=['email'],
        phone_fields=['phone'] if 'phone' in data else None
    )
    
    if validation_errors:
        log_security_event('invalid_registration_attempt', {
            'errors': validation_errors,
            'user_type': 'patient'
        })
        return jsonify({'error': validation_errors}), 400
    
    # Validate password strength
    password_errors = validate_password_strength(data['password'])
    if password_errors:
        return jsonify({'error': password_errors}), 400
    
    # Check if patient already exists
    existing_patient = Patient.query.filter_by(email=data['email']).first()
    if existing_patient:
        log_security_event('duplicate_registration_attempt', {
            'email': data['email'],
            'user_type': 'patient'
        })
        return jsonify({'error': 'Patient with this email already exists'}), 400
    
    # Hash password
    password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Create new patient
    new_patient = Patient(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        password_hash=password_hash,
        date_of_birth=data.get('date_of_birth'),
        gender=data.get('gender'),
        address=data.get('address'),
        phone=data.get('phone')
    )
    
    try:
        db.session.add(new_patient)
        db.session.commit()
        
        log_security_event('successful_registration', {
            'user_type': 'patient',
            'user_id': new_patient.patient_id
        })
        
        return jsonify({'message': 'Patient registered successfully'}), 201
    except Exception as e:
        db.session.rollback()
        log_security_event('registration_error', {
            'error': str(e),
            'user_type': 'patient'
        })
        return jsonify({'error': 'Registration failed'}), 500

@auth_bp.route('/register/doctor', methods=['POST'])
def register_doctor():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['first_name', 'last_name', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check if doctor already exists
    existing_doctor = Doctor.query.filter_by(email=data['email']).first()
    if existing_doctor:
        return jsonify({'error': 'Doctor with this email already exists'}), 400
    
    # Hash password
    password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Create new doctor
    new_doctor = Doctor(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        password_hash=password_hash,
        specialty=data.get('specialty'),
        phone=data.get('phone')
    )
    
    try:
        db.session.add(new_doctor)
        db.session.commit()
        return jsonify({'message': 'Doctor registered successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500

@auth_bp.route('/login/patient', methods=['POST'])
@rate_limit(max_requests=10, window_minutes=15)  # Limit login attempts
def login_patient():
    data = request.get_json()
    
    # Sanitize input data
    data = sanitize_input(data)
    
    # Validate input
    validation_errors = validate_input(
        data, 
        required_fields=['email', 'password'],
        email_fields=['email']
    )
    
    if validation_errors:
        log_security_event('invalid_login_attempt', {
            'errors': validation_errors,
            'user_type': 'patient'
        })
        return jsonify({'error': validation_errors}), 400
    
    patient = Patient.query.filter_by(email=data['email']).first()
    
    if patient and bcrypt.checkpw(data['password'].encode('utf-8'), patient.password_hash.encode('utf-8')):
        access_token = create_access_token(identity={'id': patient.patient_id, 'type': 'patient'})
        
        log_security_event('successful_login', {
            'user_type': 'patient',
            'user_id': patient.patient_id
        })
        
        check_suspicious_activity(patient.patient_id, 'data_access')
        
        return jsonify({
            'access_token': access_token,
            'user': patient.to_dict()
        }), 200
    else:
        log_security_event('failed_login_attempt', {
            'email': data['email'],
            'user_type': 'patient'
        })
        
        check_suspicious_activity(data['email'], 'failed_login')
        
        return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/login/doctor', methods=['POST'])
def login_doctor():
    data = request.get_json()
    
    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password are required'}), 400
    
    doctor = Doctor.query.filter_by(email=data['email']).first()
    
    if doctor and bcrypt.checkpw(data['password'].encode('utf-8'), doctor.password_hash.encode('utf-8')):
        access_token = create_access_token(identity={'id': doctor.doctor_id, 'type': 'doctor'})
        return jsonify({
            'access_token': access_token,
            'user': doctor.to_dict()
        }), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user = get_jwt_identity()
    
    if current_user['type'] == 'patient':
        patient = Patient.query.get(current_user['id'])
        if patient:
            return jsonify(patient.to_dict()), 200
    elif current_user['type'] == 'doctor':
        doctor = Doctor.query.get(current_user['id'])
        if doctor:
            return jsonify(doctor.to_dict()), 200
    
    return jsonify({'error': 'User not found'}), 404
