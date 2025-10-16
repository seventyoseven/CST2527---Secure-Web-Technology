from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
from src.models.user import db, MedicalNote, Patient, Doctor

medical_notes_bp = Blueprint('medical_notes', __name__)

@medical_notes_bp.route('/medical-notes', methods=['POST'])
@jwt_required()
def create_medical_note():
    """Create a new medical note (doctors only)"""
    current_user = get_jwt_identity()
    
    if current_user['type'] != 'doctor':
        return jsonify({'error': 'Only doctors can create medical notes'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['patient_id', 'note_date']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    try:
        # Parse date
        note_date = datetime.strptime(data['note_date'], '%Y-%m-%d').date()
        
        # Check if patient exists
        patient = Patient.query.get(data['patient_id'])
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Create new medical note
        new_note = MedicalNote(
            patient_id=data['patient_id'],
            doctor_id=current_user['id'],
            note_date=note_date,
            note_details=data.get('note_details', ''),
            medication=data.get('medication', ''),
            treatment=data.get('treatment', '')
        )
        
        db.session.add(new_note)
        db.session.commit()
        
        return jsonify({
            'message': 'Medical note created successfully',
            'note': new_note.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': 'Invalid date format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create medical note'}), 500

@medical_notes_bp.route('/medical-notes', methods=['GET'])
@jwt_required()
def get_medical_notes():
    """Get medical notes for current user"""
    current_user = get_jwt_identity()
    
    if current_user['type'] == 'patient':
        # Patients can only see their own medical notes
        notes = MedicalNote.query.filter_by(patient_id=current_user['id']).all()
    elif current_user['type'] == 'doctor':
        # Doctors can see all notes they've created
        notes = MedicalNote.query.filter_by(doctor_id=current_user['id']).all()
    else:
        return jsonify({'error': 'Invalid user type'}), 400
    
    return jsonify([note.to_dict() for note in notes]), 200

@medical_notes_bp.route('/medical-notes/patient/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_patient_medical_notes(patient_id):
    """Get medical notes for a specific patient (doctors only)"""
    current_user = get_jwt_identity()
    
    if current_user['type'] != 'doctor':
        return jsonify({'error': 'Only doctors can access patient medical notes'}), 403
    
    # Check if patient exists
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    # Get all medical notes for this patient
    notes = MedicalNote.query.filter_by(patient_id=patient_id).all()
    
    return jsonify([note.to_dict() for note in notes]), 200

@medical_notes_bp.route('/medical-notes/<int:note_id>', methods=['GET'])
@jwt_required()
def get_medical_note(note_id):
    """Get specific medical note details"""
    current_user = get_jwt_identity()
    
    note = MedicalNote.query.get(note_id)
    if not note:
        return jsonify({'error': 'Medical note not found'}), 404
    
    # Check if user has access to this note
    if current_user['type'] == 'patient' and note.patient_id != current_user['id']:
        return jsonify({'error': 'Access denied'}), 403
    elif current_user['type'] == 'doctor' and note.doctor_id != current_user['id']:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(note.to_dict()), 200

@medical_notes_bp.route('/medical-notes/<int:note_id>', methods=['PUT'])
@jwt_required()
def update_medical_note(note_id):
    """Update medical note (doctors only)"""
    current_user = get_jwt_identity()
    
    if current_user['type'] != 'doctor':
        return jsonify({'error': 'Only doctors can update medical notes'}), 403
    
    note = MedicalNote.query.get(note_id)
    if not note:
        return jsonify({'error': 'Medical note not found'}), 404
    
    # Check if doctor owns this note
    if note.doctor_id != current_user['id']:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    try:
        # Update fields if provided
        if 'note_date' in data:
            note.note_date = datetime.strptime(data['note_date'], '%Y-%m-%d').date()
        if 'note_details' in data:
            note.note_details = data['note_details']
        if 'medication' in data:
            note.medication = data['medication']
        if 'treatment' in data:
            note.treatment = data['treatment']
        
        db.session.commit()
        return jsonify({
            'message': 'Medical note updated successfully',
            'note': note.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({'error': 'Invalid date format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update medical note'}), 500

@medical_notes_bp.route('/medical-notes/<int:note_id>', methods=['DELETE'])
@jwt_required()
def delete_medical_note(note_id):
    """Delete medical note (doctors only)"""
    current_user = get_jwt_identity()
    
    if current_user['type'] != 'doctor':
        return jsonify({'error': 'Only doctors can delete medical notes'}), 403
    
    note = MedicalNote.query.get(note_id)
    if not note:
        return jsonify({'error': 'Medical note not found'}), 404
    
    # Check if doctor owns this note
    if note.doctor_id != current_user['id']:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        db.session.delete(note)
        db.session.commit()
        return jsonify({'message': 'Medical note deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete medical note'}), 500

@medical_notes_bp.route('/patients', methods=['GET'])
@jwt_required()
def get_patients():
    """Get list of all patients (doctors only)"""
    current_user = get_jwt_identity()
    
    if current_user['type'] != 'doctor':
        return jsonify({'error': 'Only doctors can access patient list'}), 403
    
    patients = Patient.query.all()
    return jsonify([patient.to_dict() for patient in patients]), 200
