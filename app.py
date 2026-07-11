from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'medislot-dev-secret-key-change-this-in-production'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'medislot.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB

# ---- Change these credentials before deploying anywhere real ----
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'mugesh14'
# -------------------------------------------------------------------

DEPARTMENTS = {
    'General Physician': [
        {'name': 'Dr. A. Sharma', 'fee': 400, 'experience': 9},
        {'name': 'Dr. R. Iyer', 'fee': 350, 'experience': 5},
    ],
    'Cardiologist': [
        {'name': 'Dr. S. Mehta', 'fee': 900, 'experience': 14},
        {'name': 'Dr. K. Rao', 'fee': 750, 'experience': 8},
    ],
    'Dermatologist': [
        {'name': 'Dr. P. Nair', 'fee': 600, 'experience': 10},
        {'name': 'Dr. V. Singh', 'fee': 550, 'experience': 6},
    ],
    'Orthopedic': [
        {'name': 'Dr. M. Reddy', 'fee': 800, 'experience': 12},
        {'name': 'Dr. T. Kumar', 'fee': 650, 'experience': 7},
    ],
    'Pediatrician': [
        {'name': 'Dr. N. Joshi', 'fee': 500, 'experience': 11},
        {'name': 'Dr. L. Fernandes', 'fee': 450, 'experience': 4},
    ],
}

def find_doctor(department, doctor_name):
    for doc in DEPARTMENTS.get(department, []):
        if doc['name'] == doctor_name:
            return doc
    return None


TIME_SLOTS = [
    '09:00 AM - 10:00 AM',
    '10:00 AM - 11:00 AM',
    '11:00 AM - 12:00 PM',
    '02:00 PM - 03:00 PM',
    '03:00 PM - 04:00 PM',
    '04:00 PM - 05:00 PM',
]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            mobile TEXT NOT NULL,
            email TEXT,
            address TEXT,
            department TEXT,
            doctor TEXT,
            appointment_date TEXT,
            time_slot TEXT,
            consultation_mode TEXT,
            symptoms TEXT,
            medical_history TEXT,
            report_filename TEXT,
            consultation_fee TEXT,
            doctor_experience TEXT,
            payment_method TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()


@app.route('/terms')
def terms():
    return render_template('terms.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = {
            'full_name': request.form.get('full_name', '').strip(),
            'age': request.form.get('age', '').strip(),
            'gender': request.form.get('gender', ''),
            'mobile': request.form.get('mobile', '').strip(),
            'email': request.form.get('email', '').strip(),
            'address': request.form.get('address', '').strip(),
            'department': request.form.get('department', ''),
            'doctor': request.form.get('doctor', ''),
            'appointment_date': request.form.get('appointment_date', ''),
            'time_slot': request.form.get('time_slot', ''),
            'consultation_mode': request.form.get('consultation_mode', ''),
            'symptoms': request.form.get('symptoms', '').strip(),
            'medical_history': request.form.get('medical_history', '').strip(),
            'consultation_fee': request.form.get('consultation_fee', '').strip(),
            'payment_method': request.form.get('payment_method', ''),
        }
        terms = request.form.get('terms')

        if not data['full_name'] or not data['mobile'] or not data['appointment_date'] \
                or not data['time_slot'] or not terms:
            flash('Please fill in all required fields and accept the terms & conditions.', 'error')
            return render_template('index.html', departments=list(DEPARTMENTS.keys()), doctors=DEPARTMENTS,
                                    time_slots=TIME_SLOTS, form=request.form)

        # Trust the server-side doctor list for the fee/experience, not the client field
        doctor_info = find_doctor(data['department'], data['doctor'])
        doctor_experience = ''
        if doctor_info:
            data['consultation_fee'] = str(doctor_info['fee'])
            doctor_experience = str(doctor_info['experience'])

        report_filename = ''
        report_file = request.files.get('report_file')
        if report_file and report_file.filename:
            report_filename = secure_filename(report_file.filename)
            report_file.save(os.path.join(app.config['UPLOAD_FOLDER'], report_filename))

        conn = get_db()
        conn.execute('''
            INSERT INTO appointments (
                full_name, age, gender, mobile, email, address, department, doctor,
                appointment_date, time_slot, consultation_mode, symptoms, medical_history,
                report_filename, consultation_fee, doctor_experience, payment_method, created_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ''', (
            data['full_name'], data['age'], data['gender'], data['mobile'], data['email'],
            data['address'], data['department'], data['doctor'], data['appointment_date'],
            data['time_slot'], data['consultation_mode'], data['symptoms'],
            data['medical_history'], report_filename, data['consultation_fee'],
            doctor_experience, data['payment_method'], datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        conn.commit()
        conn.close()

        flash('Your appointment has been booked. We will contact you shortly to confirm.', 'success')
        return redirect(url_for('index'))

    return render_template('index.html', departments=list(DEPARTMENTS.keys()), doctors=DEPARTMENTS,
                            time_slots=TIME_SLOTS, form={})


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Welcome back, Admin. Here are the latest appointments.', 'success')
            return redirect(url_for('admin_dashboard'))
        flash('Incorrect username or password. Please try again.', 'error')
        return redirect(url_for('admin_login'))

    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')


@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash('Please log in to view the appointments table.', 'error')
        return redirect(url_for('admin_login'))

    conn = get_db()
    appointments = conn.execute('SELECT * FROM appointments ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('admin_dashboard.html', appointments=appointments)


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('admin_login'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
