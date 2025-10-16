# Secure Medical Web Application

## Overview

This is a secure, GDPR-compliant medical web application designed for a doctor's surgery. The application provides comprehensive functionality for patient appointment booking, doctor medical notes management, and secure data handling.

## Features

### Core Functionality
- **Patient Registration & Authentication**: Secure patient account creation and login
- **Doctor Registration & Authentication**: Secure doctor account creation and login
- **Appointment Booking**: Patients can book appointments with specific doctors
- **Medical Notes Management**: Doctors can store and manage patient medical records
- **GDPR Compliance**: Full compliance with data protection regulations

### Security Features
- **Password Security**: Strong password requirements with bcrypt hashing
- **Rate Limiting**: Protection against brute force attacks
- **Input Validation**: Comprehensive input sanitization and validation
- **Security Headers**: Implementation of security headers (CSP, HSTS, etc.)
- **SQL Injection Protection**: Parameterized queries and input validation
- **Authentication**: JWT-based authentication system
- **Audit Logging**: Security event logging for monitoring

### GDPR Compliance
- **Data Export**: Users can export all their personal data
- **Data Rectification**: Users can update their personal information
- **Data Deletion**: Users can request deletion of their data
- **Consent Management**: Tracking and management of user consent
- **Privacy Policy**: Comprehensive privacy policy and data processing information
- **Data Retention**: Clear data retention policies

## Technology Stack

### Backend
- **Flask**: Python web framework
- **PostgreSQL**: Secure database system
- **SQLAlchemy**: ORM for database operations
- **Flask-JWT-Extended**: JWT authentication
- **bcrypt**: Password hashing
- **psycopg2**: PostgreSQL adapter

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with responsive design
- **JavaScript**: Interactive functionality
- **Font Awesome**: Icons

### Security
- **HTTPS**: Secure communication (production)
- **CSRF Protection**: Cross-site request forgery protection
- **XSS Protection**: Cross-site scripting prevention
- **Content Security Policy**: Strict CSP headers
- **Rate Limiting**: Request rate limiting

## Database Schema

### Tables
1. **patients**: Patient information and credentials
2. **doctors**: Doctor information and credentials
3. **appointments**: Appointment scheduling data
4. **medical_notes**: Medical records and notes

### Security Configuration
- Encrypted connections
- User privilege separation
- Audit logging enabled
- Secure authentication methods

## API Endpoints

### Authentication
- `POST /api/register/patient` - Patient registration
- `POST /api/register/doctor` - Doctor registration
- `POST /api/login/patient` - Patient login
- `POST /api/login/doctor` - Doctor login

### Appointments
- `GET /api/appointments` - Get user appointments
- `POST /api/appointments` - Book new appointment

### Medical Notes
- `GET /api/medical-notes` - Get medical notes
- `POST /api/medical-notes` - Create medical note

### GDPR Compliance
- `GET /api/gdpr/data-export` - Export user data
- `DELETE /api/gdpr/data-deletion` - Request data deletion
- `PUT /api/gdpr/data-rectification` - Update user data
- `GET /api/gdpr/consent-status` - Get consent status
- `POST /api/gdpr/consent` - Update consent preferences
- `GET /api/gdpr/data-processing-purposes` - Get data processing info
- `GET /api/gdpr/privacy-policy` - Get privacy policy

### User Management
- `GET /api/patients` - Get all patients (for doctors)
- `GET /api/doctors` - Get all doctors

## Installation & Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Virtual environment

### Database Setup
1. Install PostgreSQL
2. Create database and user:
   ```sql
   CREATE DATABASE medical_app;
   CREATE USER medical_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE medical_app TO medical_user;
   ```

### Application Setup
1. Clone the repository
2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python run.py
   ```

## Security Considerations

### Password Policy
- Minimum 8 characters
- Must contain uppercase, lowercase, numbers, and special characters
- Protection against common weak passwords

### Data Protection
- All sensitive data encrypted at rest
- Secure transmission with HTTPS
- Regular security audits and monitoring
- Compliance with medical data protection standards

### Access Control
- Role-based access (patients vs doctors)
- JWT token-based authentication
- Session management and timeout
- Rate limiting on sensitive endpoints

## GDPR Compliance Details

### Legal Basis
- **Healthcare Service Delivery**: Vital interests and consent
- **Appointment Management**: Contract performance and consent
- **System Security**: Legitimate interests

### Data Retention
- Medical records: 7 years after last treatment
- Appointment data: 2 years after appointment
- User accounts: Until deletion requested
- Audit logs: 1 year

### User Rights
- Right to access personal data
- Right to rectify inaccurate data
- Right to erase personal data
- Right to restrict processing
- Right to data portability
- Right to object to processing
- Right to withdraw consent

## Testing

Run the test suite:
```bash
python test_deployment.py
```

This will test:
- Application startup
- Patient and doctor registration
- Authentication system
- GDPR endpoints
- Basic functionality

## Deployment

### Production Considerations
- Use environment variables for sensitive configuration
- Enable HTTPS with valid SSL certificates
- Configure proper database security
- Set up monitoring and logging
- Regular security updates
- Backup and disaster recovery

### Environment Variables
- `FLASK_ENV`: Set to 'production' for production deployment
- `SECRET_KEY`: Application secret key
- `JWT_SECRET_KEY`: JWT signing key
- `DATABASE_URL`: PostgreSQL connection string

## Support & Maintenance

### Monitoring
- Security event logging
- Performance monitoring
- Error tracking
- Audit trail maintenance

### Updates
- Regular security patches
- Dependency updates
- Feature enhancements
- Compliance updates

## License

This application is designed for educational and demonstration purposes. Ensure compliance with local healthcare regulations and data protection laws before production use.

## Contact

For questions about GDPR compliance, security features, or technical implementation, please refer to the comprehensive documentation and security configuration files included in this project.
