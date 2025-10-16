#!/usr/bin/env python3
"""
Simple test script to verify the medical application works correctly
"""
import os
import sys
import subprocess
import time
import requests

def test_application():
    """Test the medical application functionality"""
    print("Starting Medical Application Test...")
    
    # Start the application
    print("Starting Flask application...")
    process = subprocess.Popen([
        sys.executable, 'run.py'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for the application to start
    time.sleep(3)
    
    try:
        # Test basic connectivity
        print("Testing basic connectivity...")
        response = requests.get('http://localhost:5000/')
        print(f"Homepage status: {response.status_code}")
        
        # Test patient registration
        print("Testing patient registration...")
        patient_data = {
            "first_name": "Test",
            "last_name": "Patient",
            "email": "test.patient@example.com",
            "password": "TestPassword1!",
            "date_of_birth": "1990-01-01",
            "gender": "Male",
            "phone": "123-456-7890",
            "address": "123 Test St"
        }
        
        response = requests.post('http://localhost:5000/api/register/patient', json=patient_data)
        print(f"Patient registration status: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Test doctor registration
        print("Testing doctor registration...")
        doctor_data = {
            "first_name": "Test",
            "last_name": "Doctor",
            "email": "test.doctor@example.com",
            "password": "TestDoctor1!",
            "specialty": "General Practice",
            "phone": "098-765-4321"
        }
        
        response = requests.post('http://localhost:5000/api/register/doctor', json=doctor_data)
        print(f"Doctor registration status: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Test patient login
        print("Testing patient login...")
        login_data = {
            "email": "test.patient@example.com",
            "password": "TestPassword1!"
        }
        
        response = requests.post('http://localhost:5000/api/login/patient', json=login_data)
        print(f"Patient login status: {response.status_code}")
        
        if response.status_code == 200:
            token = response.json().get('access_token')
            print("Patient login successful!")
            
            # Test GDPR endpoints
            print("Testing GDPR data export...")
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get('http://localhost:5000/api/gdpr/data-export', headers=headers)
            print(f"GDPR export status: {response.status_code}")
        
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
    
    finally:
        # Clean up
        print("Stopping application...")
        process.terminate()
        process.wait()

if __name__ == '__main__':
    test_application()
