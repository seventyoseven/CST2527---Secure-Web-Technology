// Global variables
let currentUser = null;
let currentUserType = 'patient';
let currentRegisterUserType = 'patient';
let authToken = null;

// API Base URL
const API_BASE = '/api';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is already logged in
    const token = localStorage.getItem('authToken');
    const user = localStorage.getItem('currentUser');
    
    if (token && user) {
        authToken = token;
        currentUser = JSON.parse(user);
        showDashboard();
    }
    
    // Set up event listeners
    setupEventListeners();
    
    // Set minimum date for appointment booking to today
    const today = new Date().toISOString().split('T')[0];
    const appointmentDateInput = document.getElementById('appointmentDate');
    const noteDateInput = document.getElementById('noteDate');
    
    if (appointmentDateInput) {
        appointmentDateInput.min = today;
    }
    if (noteDateInput) {
        noteDateInput.value = today;
    }
});

// Set up event listeners
function setupEventListeners() {
    // Login form
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    
    // Register form
    document.getElementById('registerForm').addEventListener('submit', handleRegister);
    
    // Booking form
    document.getElementById('bookingForm').addEventListener('submit', handleBooking);
    
    // Medical note form
    document.getElementById('medicalNoteForm').addEventListener('submit', handleMedicalNote);
    
    // Mobile menu toggle
    const hamburger = document.getElementById('hamburger');
    const navMenu = document.getElementById('nav-menu');
    
    if (hamburger) {
        hamburger.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            if (event.target === modal) {
                closeModal();
            }
        });
    });
}

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.classList.add('show');
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 4000);
}

function showLoading() {
    document.getElementById('loadingSpinner').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingSpinner').style.display = 'none';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

function formatTime(timeString) {
    const time = new Date(`2000-01-01T${timeString}`);
    return time.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}

// API functions
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    };
    
    if (authToken) {
        config.headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    try {
        const response = await fetch(url, config);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `HTTP error! status: ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// Modal functions
function showLoginModal(userType = 'patient') {
    setUserType(userType);
    document.getElementById('loginModal').style.display = 'block';
    closeOtherModals('loginModal');
}

function showRegisterModal(userType = 'patient') {
    setRegisterUserType(userType);
    document.getElementById('registerModal').style.display = 'block';
    closeOtherModals('registerModal');
}

function showBookingModal() {
    document.getElementById('bookingModal').style.display = 'block';
    closeOtherModals('bookingModal');
    loadDoctors();
}

function showMedicalNoteModal() {
    document.getElementById('medicalNoteModal').style.display = 'block';
    closeOtherModals('medicalNoteModal');
    loadPatients();
}

function closeModal() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.style.display = 'none';
    });
}

function closeOtherModals(keepOpen) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (modal.id !== keepOpen) {
            modal.style.display = 'none';
        }
    });
}

// User type toggle functions
function setUserType(type) {
    currentUserType = type;
    const buttons = document.querySelectorAll('#loginModal .toggle-btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    
    if (type === 'patient') {
        buttons[0].classList.add('active');
    } else {
        buttons[1].classList.add('active');
    }
}

function setRegisterUserType(type) {
    currentRegisterUserType = type;
    const buttons = document.querySelectorAll('#registerModal .toggle-btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    
    const patientFields = document.getElementById('patientFields');
    const doctorFields = document.getElementById('doctorFields');
    
    if (type === 'patient') {
        buttons[0].classList.add('active');
        patientFields.style.display = 'block';
        doctorFields.style.display = 'none';
    } else {
        buttons[1].classList.add('active');
        patientFields.style.display = 'none';
        doctorFields.style.display = 'block';
    }
}

// Authentication functions
async function handleLogin(event) {
    event.preventDefault();
    showLoading();
    
    const formData = new FormData(event.target);
    const loginData = {
        email: formData.get('email'),
        password: formData.get('password')
    };
    
    try {
        const response = await apiRequest(`/login/${currentUserType}`, {
            method: 'POST',
            body: JSON.stringify(loginData)
        });
        
        authToken = response.access_token;
        currentUser = response.user;
        
        // Store in localStorage
        localStorage.setItem('authToken', authToken);
        localStorage.setItem('currentUser', JSON.stringify(currentUser));
        localStorage.setItem('userType', currentUserType);
        
        showNotification('Login successful!', 'success');
        closeModal();
        showDashboard();
        
    } catch (error) {
        showNotification(error.message, 'error');
    } finally {
        hideLoading();
    }
}

async function handleRegister(event) {
    event.preventDefault();
    showLoading();
    
    const formData = new FormData(event.target);
    const registerData = {
        first_name: formData.get('firstName'),
        last_name: formData.get('lastName'),
        email: formData.get('email'),
        password: formData.get('password')
    };
    
    // Add type-specific fields
    if (currentRegisterUserType === 'patient') {
        registerData.date_of_birth = formData.get('dateOfBirth') || null;
        registerData.gender = formData.get('gender') || null;
        registerData.phone = formData.get('phone') || null;
        registerData.address = formData.get('address') || null;
    } else {
        registerData.specialty = formData.get('specialty') || null;
        registerData.phone = formData.get('phone') || null;
    }
    
    try {
        await apiRequest(`/register/${currentRegisterUserType}`, {
            method: 'POST',
            body: JSON.stringify(registerData)
        });
        
        showNotification('Registration successful! Please login.', 'success');
        closeModal();
        showLoginModal(currentRegisterUserType);
        
    } catch (error) {
        showNotification(error.message, 'error');
    } finally {
        hideLoading();
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    localStorage.removeItem('userType');
    
    // Hide dashboard and show main page
    document.getElementById('dashboard').style.display = 'none';
    document.querySelector('.hero').style.display = 'flex';
    document.querySelector('.about').style.display = 'block';
    document.querySelector('.contact').style.display = 'block';
    
    showNotification('Logged out successfully', 'info');
}

// Dashboard functions
function showDashboard() {
    // Hide main page sections
    document.querySelector('.hero').style.display = 'none';
    document.querySelector('.about').style.display = 'none';
    document.querySelector('.contact').style.display = 'none';
    
    // Show dashboard
    document.getElementById('dashboard').style.display = 'block';
    
    // Set user name
    document.getElementById('userName').textContent = 
        `${currentUser.first_name} ${currentUser.last_name}`;
    
    // Show appropriate dashboard
    const userType = localStorage.getItem('userType') || 'patient';
    if (userType === 'patient') {
        document.getElementById('patientDashboard').style.display = 'block';
        document.getElementById('doctorDashboard').style.display = 'none';
        loadPatientData();
    } else {
        document.getElementById('patientDashboard').style.display = 'none';
        document.getElementById('doctorDashboard').style.display = 'block';
        loadDoctorData();
    }
}

// Patient dashboard functions
async function loadPatientData() {
    try {
        // Load appointments
        const appointments = await apiRequest('/appointments');
        displayPatientAppointments(appointments);
        
        // Load medical notes
        const medicalNotes = await apiRequest('/medical-notes');
        displayPatientMedicalNotes(medicalNotes);
        
    } catch (error) {
        showNotification('Failed to load patient data', 'error');
    }
}

function displayPatientAppointments(appointments) {
    const container = document.getElementById('patientAppointments');
    
    if (appointments.length === 0) {
        container.innerHTML = '<p>No appointments scheduled.</p>';
        return;
    }
    
    container.innerHTML = appointments.map(appointment => `
        <div class="appointment-item">
            <h4>Dr. ${appointment.doctor_name}</h4>
            <p class="date-time">${formatDate(appointment.appointment_date)} at ${formatTime(appointment.appointment_time)}</p>
            <p><strong>Reason:</strong> ${appointment.reason || 'Not specified'}</p>
        </div>
    `).join('');
}

function displayPatientMedicalNotes(notes) {
    const container = document.getElementById('patientMedicalNotes');
    
    if (notes.length === 0) {
        container.innerHTML = '<p>No medical records available.</p>';
        return;
    }
    
    container.innerHTML = notes.map(note => `
        <div class="note-item">
            <h4>Dr. ${note.doctor_name} - ${formatDate(note.note_date)}</h4>
            <p><strong>Notes:</strong> ${note.note_details || 'No notes'}</p>
            <p><strong>Medication:</strong> ${note.medication || 'None prescribed'}</p>
            <p><strong>Treatment:</strong> ${note.treatment || 'No treatment specified'}</p>
        </div>
    `).join('');
}

// Doctor dashboard functions
async function loadDoctorData() {
    try {
        // Load appointments
        const appointments = await apiRequest('/appointments');
        displayDoctorAppointments(appointments);
        
        // Load medical notes
        const medicalNotes = await apiRequest('/medical-notes');
        displayDoctorMedicalNotes(medicalNotes);
        
        // Load patients list
        const patients = await apiRequest('/patients');
        displayPatientsList(patients);
        
    } catch (error) {
        showNotification('Failed to load doctor data', 'error');
    }
}

function displayDoctorAppointments(appointments) {
    const container = document.getElementById('doctorAppointments');
    
    if (appointments.length === 0) {
        container.innerHTML = '<p>No appointments scheduled.</p>';
        return;
    }
    
    container.innerHTML = appointments.map(appointment => `
        <div class="appointment-item">
            <h4>${appointment.patient_name}</h4>
            <p class="date-time">${formatDate(appointment.appointment_date)} at ${formatTime(appointment.appointment_time)}</p>
            <p><strong>Reason:</strong> ${appointment.reason || 'Not specified'}</p>
        </div>
    `).join('');
}

function displayDoctorMedicalNotes(notes) {
    const container = document.getElementById('doctorMedicalNotes');
    
    if (notes.length === 0) {
        container.innerHTML = '<p>No medical notes created.</p>';
        return;
    }
    
    container.innerHTML = notes.map(note => `
        <div class="note-item">
            <h4>${note.patient_name} - ${formatDate(note.note_date)}</h4>
            <p><strong>Notes:</strong> ${note.note_details || 'No notes'}</p>
            <p><strong>Medication:</strong> ${note.medication || 'None prescribed'}</p>
            <p><strong>Treatment:</strong> ${note.treatment || 'No treatment specified'}</p>
        </div>
    `).join('');
}

function displayPatientsList(patients) {
    const container = document.getElementById('patientsList');
    
    if (patients.length === 0) {
        container.innerHTML = '<p>No patients registered.</p>';
        return;
    }
    
    container.innerHTML = patients.map(patient => `
        <div class="patient-item">
            <h4>${patient.first_name} ${patient.last_name}</h4>
            <p><strong>Email:</strong> ${patient.email}</p>
            <p><strong>Phone:</strong> ${patient.phone || 'Not provided'}</p>
            <p><strong>Date of Birth:</strong> ${patient.date_of_birth ? formatDate(patient.date_of_birth) : 'Not provided'}</p>
        </div>
    `).join('');
}

// Appointment booking functions
async function loadDoctors() {
    try {
        const doctors = await apiRequest('/doctors');
        const select = document.getElementById('doctorSelect');
        
        select.innerHTML = '<option value="">Choose a doctor...</option>';
        doctors.forEach(doctor => {
            const option = document.createElement('option');
            option.value = doctor.doctor_id;
            option.textContent = `Dr. ${doctor.first_name} ${doctor.last_name} - ${doctor.specialty || 'General Practice'}`;
            select.appendChild(option);
        });
        
    } catch (error) {
        showNotification('Failed to load doctors', 'error');
    }
}

async function handleBooking(event) {
    event.preventDefault();
    showLoading();
    
    const formData = new FormData(event.target);
    const bookingData = {
        doctor_id: parseInt(formData.get('doctor_id')),
        appointment_date: formData.get('appointment_date'),
        appointment_time: formData.get('appointment_time'),
        reason: formData.get('reason')
    };
    
    try {
        await apiRequest('/appointments', {
            method: 'POST',
            body: JSON.stringify(bookingData)
        });
        
        showNotification('Appointment booked successfully!', 'success');
        closeModal();
        loadPatientData(); // Refresh patient data
        
        // Reset form
        event.target.reset();
        
    } catch (error) {
        showNotification(error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Medical notes functions
async function loadPatients() {
    try {
        const patients = await apiRequest('/patients');
        const select = document.getElementById('patientSelect');
        
        select.innerHTML = '<option value="">Choose a patient...</option>';
        patients.forEach(patient => {
            const option = document.createElement('option');
            option.value = patient.patient_id;
            option.textContent = `${patient.first_name} ${patient.last_name}`;
            select.appendChild(option);
        });
        
    } catch (error) {
        showNotification('Failed to load patients', 'error');
    }
}

async function handleMedicalNote(event) {
    event.preventDefault();
    showLoading();
    
    const formData = new FormData(event.target);
    const noteData = {
        patient_id: parseInt(formData.get('patient_id')),
        note_date: formData.get('note_date'),
        note_details: formData.get('note_details'),
        medication: formData.get('medication'),
        treatment: formData.get('treatment')
    };
    
    try {
        await apiRequest('/medical-notes', {
            method: 'POST',
            body: JSON.stringify(noteData)
        });
        
        showNotification('Medical note saved successfully!', 'success');
        closeModal();
        loadDoctorData(); // Refresh doctor data
        
        // Reset form
        event.target.reset();
        
    } catch (error) {
        showNotification(error.message, 'error');
    } finally {
        hideLoading();
    }
}
