from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from src.models.user import db, Patient, Doctor, Appointment, MedicalNote
import json

gdpr_bp = Blueprint('gdpr', __name__)

@gdpr_bp.route('/gdpr/data-export', methods=['GET'])
@jwt_required()
def export_user_data():
    """Export all user data in JSON format (GDPR Article 20 - Right to data portability)"""
    current_user = get_jwt_identity()
    
    try:
        if current_user['type'] == 'patient':
            patient = Patient.query.get(current_user['id'])
            if not patient:
                return jsonify({'error': 'Patient not found'}), 404
            
            # Collect all patient data
            patient_data = patient.to_dict()
            
            # Get appointments
            appointments = Appointment.query.filter_by(patient_id=current_user['id']).all()
            patient_data['appointments'] = [appointment.to_dict() for appointment in appointments]
            
            # Get medical notes
            medical_notes = MedicalNote.query.filter_by(patient_id=current_user['id']).all()
            patient_data['medical_notes'] = [note.to_dict() for note in medical_notes]
            
            # Add metadata
            export_data = {
                'export_date': datetime.utcnow().isoformat(),
                'data_subject': 'patient',
                'data': patient_data
            }
            
        elif current_user['type'] == 'doctor':
            doctor = Doctor.query.get(current_user['id'])
            if not doctor:
                return jsonify({'error': 'Doctor not found'}), 404
            
            # Collect all doctor data
            doctor_data = doctor.to_dict()
            
            # Get appointments
            appointments = Appointment.query.filter_by(doctor_id=current_user['id']).all()
            doctor_data['appointments'] = [appointment.to_dict() for appointment in appointments]
            
            # Get medical notes created by doctor
            medical_notes = MedicalNote.query.filter_by(doctor_id=current_user['id']).all()
            doctor_data['medical_notes'] = [note.to_dict() for note in medical_notes]
            
            # Add metadata
            export_data = {
                'export_date': datetime.utcnow().isoformat(),
                'data_subject': 'doctor',
                'data': doctor_data
            }
        
        return jsonify(export_data), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to export data'}), 500

@gdpr_bp.route('/gdpr/data-deletion', methods=['DELETE'])
@jwt_required()
def request_data_deletion():
    """Request deletion of all user data (GDPR Article 17 - Right to erasure)"""
    current_user = get_jwt_identity()
    
    try:
        if current_user['type'] == 'patient':
            patient = Patient.query.get(current_user['id'])
            if not patient:
                return jsonify({'error': 'Patient not found'}), 404
            
            # Delete related data first (due to foreign key constraints)
            MedicalNote.query.filter_by(patient_id=current_user['id']).delete()
            Appointment.query.filter_by(patient_id=current_user['id']).delete()
            
            # Delete patient record
            db.session.delete(patient)
            db.session.commit()
            
            return jsonify({'message': 'Patient data deleted successfully'}), 200
            
        elif current_user['type'] == 'doctor':
            doctor = Doctor.query.get(current_user['id'])
            if not doctor:
                return jsonify({'error': 'Doctor not found'}), 404
            
            # Note: In a real system, you might want to handle this differently
            # as deleting a doctor might affect patient care continuity
            # You might want to anonymize rather than delete
            
            # Delete related data first
            MedicalNote.query.filter_by(doctor_id=current_user['id']).delete()
            Appointment.query.filter_by(doctor_id=current_user['id']).delete()
            
            # Delete doctor record
            db.session.delete(doctor)
            db.session.commit()
            
            return jsonify({'message': 'Doctor data deleted successfully'}), 200
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete data'}), 500

@gdpr_bp.route('/gdpr/data-rectification', methods=['PUT'])
@jwt_required()
def rectify_user_data():
    """Update/rectify user data (GDPR Article 16 - Right to rectification)"""
    current_user = get_jwt_identity()
    data = request.get_json()
    
    try:
        if current_user['type'] == 'patient':
            patient = Patient.query.get(current_user['id'])
            if not patient:
                return jsonify({'error': 'Patient not found'}), 404
            
            # Update allowed fields
            allowed_fields = ['first_name', 'last_name', 'date_of_birth', 'gender', 'address', 'phone']
            for field in allowed_fields:
                if field in data:
                    setattr(patient, field, data[field])
            
            db.session.commit()
            return jsonify({
                'message': 'Patient data updated successfully',
                'data': patient.to_dict()
            }), 200
            
        elif current_user['type'] == 'doctor':
            doctor = Doctor.query.get(current_user['id'])
            if not doctor:
                return jsonify({'error': 'Doctor not found'}), 404
            
            # Update allowed fields
            allowed_fields = ['first_name', 'last_name', 'specialty', 'phone']
            for field in allowed_fields:
                if field in data:
                    setattr(doctor, field, data[field])
            
            db.session.commit()
            return jsonify({
                'message': 'Doctor data updated successfully',
                'data': doctor.to_dict()
            }), 200
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update data'}), 500

@gdpr_bp.route('/gdpr/consent-status', methods=['GET'])
@jwt_required()
def get_consent_status():
    """Get current consent status for data processing"""
    current_user = get_jwt_identity()
    
    # In a real implementation, you would have a separate consent table
    # For this demo, we'll return a basic consent status
    consent_status = {
        'data_processing_consent': True,
        'marketing_consent': False,
        'analytics_consent': True,
        'consent_date': datetime.utcnow().isoformat(),
        'consent_version': '1.0'
    }
    
    return jsonify(consent_status), 200

@gdpr_bp.route('/gdpr/consent', methods=['POST'])
@jwt_required()
def update_consent():
    """Update consent preferences"""
    current_user = get_jwt_identity()
    data = request.get_json()
    
    # In a real implementation, you would store this in a consent table
    # For this demo, we'll just acknowledge the consent update
    
    allowed_consents = ['data_processing_consent', 'marketing_consent', 'analytics_consent']
    updated_consents = {}
    
    for consent_type in allowed_consents:
        if consent_type in data:
            updated_consents[consent_type] = data[consent_type]
    
    return jsonify({
        'message': 'Consent preferences updated successfully',
        'updated_consents': updated_consents,
        'update_date': datetime.utcnow().isoformat()
    }), 200

@gdpr_bp.route('/gdpr/data-processing-purposes', methods=['GET'])
def get_data_processing_purposes():
    """Get information about data processing purposes (GDPR Article 13/14)"""
    purposes = {
        'purposes': [
            {
                'purpose': 'Healthcare Service Delivery',
                'legal_basis': 'Vital interests and consent',
                'data_categories': ['Personal identification', 'Health data', 'Contact information'],
                'retention_period': '7 years after last treatment',
                'description': 'Processing patient data to provide medical care and maintain health records'
            },
            {
                'purpose': 'Appointment Management',
                'legal_basis': 'Contract performance and consent',
                'data_categories': ['Personal identification', 'Contact information', 'Appointment details'],
                'retention_period': '2 years after appointment',
                'description': 'Managing and scheduling patient appointments with healthcare providers'
            },
            {
                'purpose': 'System Security and Audit',
                'legal_basis': 'Legitimate interests',
                'data_categories': ['Access logs', 'System usage data'],
                'retention_period': '1 year',
                'description': 'Ensuring system security and maintaining audit trails for compliance'
            }
        ],
        'data_controller': {
            'name': 'MediCare Medical Practice',
            'contact': 'privacy@medicare.com',
            'dpo_contact': 'dpo@medicare.com'
        },
        'rights': [
            'Right to access your data',
            'Right to rectify inaccurate data',
            'Right to erase your data',
            'Right to restrict processing',
            'Right to data portability',
            'Right to object to processing',
            'Right to withdraw consent'
        ]
    }
    
    return jsonify(purposes), 200

@gdpr_bp.route('/gdpr/privacy-policy', methods=['GET'])
def get_privacy_policy():
    """Get the current privacy policy"""
    privacy_policy = {
        'version': '1.0',
        'effective_date': '2024-01-01',
        'last_updated': datetime.utcnow().isoformat(),
        'policy_url': '/privacy-policy',
        'summary': {
            'data_collected': [
                'Personal identification information',
                'Health and medical information',
                'Contact information',
                'Appointment and scheduling data'
            ],
            'data_usage': [
                'Providing healthcare services',
                'Managing appointments',
                'Maintaining medical records',
                'System security and compliance'
            ],
            'data_sharing': 'Data is not shared with third parties except as required by law or for emergency medical care',
            'data_retention': 'Medical data retained for 7 years, appointment data for 2 years, as per legal requirements',
            'user_rights': 'Users have full GDPR rights including access, rectification, erasure, and portability'
        }
    }
    
    return jsonify(privacy_policy), 200
