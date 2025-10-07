from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

# --- Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    role = db.Column(db.String(10))
    profile_pic = db.Column(db.String(200))

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

class Mark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    subject = db.Column(db.String(50))
    score = db.Column(db.Integer)

# --- Utils ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# --- Routes ---
@app.route('/')
def home():
    return render_template('welcome.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user'] = user.username
            session['role'] = user.role
            if user.role == 'admin':
                return redirect('/admin_dashboard')
            return redirect('/teacher_dashboard')
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'role' in session and session['role'] == 'admin':
        students = Student.query.all()
        marks = Mark.query.all()
        return render_template('admin_dashboard.html', students=students, marks=marks)
    return redirect('/login')

@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'role' in session and session['role'] == 'teacher':
        students = Student.query.all()
        marks = Mark.query.all()
        return render_template('teacher_dashboard.html', students=students, marks=marks)
    return redirect('/login')

@app.route('/upload_profile', methods=['POST'])
def upload_profile():
    if 'user' not in session:
        return redirect('/login')
    file = request.files['profile_pic']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(filepath)
        user = User.query.filter_by(username=session['user']).first()
        user.profile_pic = filepath
        db.session.commit()
        flash('Profile uploaded!')
    return redirect('/teacher_dashboard')

@app.route('/save_marks', methods=['POST'])
def save_marks():
    if 'role' not in session:
        return redirect('/login')
    data = request.json
    for record in data:
        student_id = record['student_id']
        for subject, score in record['scores'].items():
            mark = Mark.query.filter_by(student_id=student_id, subject=subject).first()
            if mark:
                mark.score = score
            else:
                new_mark = Mark(student_id=student_id, subject=subject, score=score)
                db.session.add(new_mark)
    db.session.commit()
    return {'status':'success'}

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)
