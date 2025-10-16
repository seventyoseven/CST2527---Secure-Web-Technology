from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date, time
from src.models.user import db, Appointment, Doctor, Patient

appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route('/doctors', methods=['GET'])
@jwt_required()
def get_doctors():
    """Get list of all doctors for appointment booking"""
    doctors = Doctor.query.all()
    return jsonify([doctor.to_dict() for doctor in doctors]), 200

@appointments_bp.route('/appointments', methods=['POST'])
@jwt_required()
def book_appointment():
    """Book a new appointment (patients only)"""
    current_user = get_jwt_identity()
    
    if current_user['type'] != 'patient':
        return jsonify({'error': 'Only patients can book appointments'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['doctor_id', 'appointment_date', 'appointment_time']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    try:
        # Parse date and time
        appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
        appointment_time = datetime.strptime(data['appointment_time'], '%H:%M').time()
        
        # Check if doctor exists
        doctor = Doctor.query.get(data['doctor_id'])
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404
        
        # Check for conflicting appointments
        existing_appointment = Appointment.query.filter_by(
            doctor_id=data['doctor_id'],
            appointment_date=appointment_date,
            appointment_time=appointment_time
        ).first()
        
        if existing_appointment:
            return jsonify({'error': 'This time slot is already booked'}), 400
        
        # Create new appointment
        new_appointment = Appointment(
            patient_id=current_user['id'],
            doctor_id=data['doctor_id'],
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            reason=data.get('reason', '')
        )
        
        db.session.add(new_appointment)
        db.session.commit()
        
        return jsonify({
            'message': 'Appointment booked successfully',
            'appointment': new_appointment.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': 'Invalid date or time format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to book appointment'}), 500

@appointments_bp.route('/appointments', methods=['GET'])
@jwt_required()
def get_appointments():
    """Get appointments for current user"""
    current_user = get_jwt_identity()
    
    if current_user['type'] == 'patient':
        appointments = Appointment.query.filter_by(patient_id=current_user['id']).all()
    elif current_user['type'] == 'doctor':
        appointments = Appointment.query.filter_by(doctor_id=current_user['id']).all()
    else:
        return jsonify({'error': 'Invalid user type'}), 400
    
    return jsonify([appointment.to_dict() for appointment in appointments]), 200

@appointments_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
@jwt_required()
def get_appointment(appointment_id):
    """Get specific appointment details"""
    current_user = get_jwt_identity()
    
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    
    # Check if user has access to this appointment
    if current_user['type'] == 'patient' and appointment.patient_id != current_user['id']:
        return jsonify({'error': 'Access denied'}), 403
    elif current_user['type'] == 'doctor' and appointment.doctor_id != current_user['id']:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(appointment.to_dict()), 200

@appointments_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@jwt_required()
def update_appointment(appointment_id):
    """Update appointment (patients can update reason, doctors can update all fields)"""
    current_user = get_jwt_identity()
    
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    
    # Check if user has access to this appointment
    if current_user['type'] == 'patient' and appointment.patient_id != current_user['id']:
        return jsonify({'error': 'Access denied'}), 403
    elif current_user['type'] == 'doctor' and appointment.doctor_id != current_user['id']:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    try:
        # Patients can only update reason
        if current_user['type'] == 'patient':
            if 'reason' in data:
                appointment.reason = data['reason']
        
        # Doctors can update date, time, and reason
        elif current_user['type'] == 'doctor':
            if 'appointment_date' in data:
                appointment.appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
            if 'appointment_time' in data:
                appointment.appointment_time = datetime.strptime(data['appointment_time'], '%H:%M').time()
            if 'reason' in data:
                appointment.reason = data['reason']
        
        db.session.commit()
        return jsonify({
            'message': 'Appointment updated successfully',
            'appointment': appointment.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({'error': 'Invalid date or time format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update appointment'}), 500

@appointments_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
@jwt_required()
def cancel_appointment(appointment_id):
    """Cancel appointment"""
    current_user = get_jwt_identity()
    
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    
    # Check if user has access to this appointment
    if current_user['type'] == 'patient' and appointment.patient_id != current_user['id']:
        return jsonify({'error': 'Access denied'}), 403
    elif current_user['type'] == 'doctor' and appointment.doctor_id != current_user['id']:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        db.session.delete(appointment)
        db.session.commit()
        return jsonify({'message': 'Appointment cancelled successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to cancel appointment'}), 500
