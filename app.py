from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
from models import db, User, Job, Application
from config import Config
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()  # creates tables if they don't exist

mail = Mail(app)

# -------------------- HOME --------------------
@app.route('/')
def home():
    jobs = Job.query.order_by(Job.posted_at.desc()).limit(5).all()
    return render_template('home.html', jobs=jobs)

# -------------------- JOB LIST --------------------
@app.route('/jobs')
def jobs():
    query = request.args.get('q')
    if query:
        jobs = Job.query.filter(Job.title.ilike(f"%{query}%")).all()
    else:
        jobs = Job.query.all()
    return render_template('jobs.html', jobs=jobs)

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('job_detail.html', job=job)

# -------------------- REGISTER --------------------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        is_employer = 'is_employer' in request.form

        user = User(username=username, email=email, password=password, is_employer=is_employer)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# -------------------- LOGIN --------------------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['is_employer'] = user.is_employer
            flash('Logged in successfully!', 'success')
            return redirect(url_for('employer_dashboard' if user.is_employer else 'candidate_dashboard'))
        else:
            flash('Invalid credentials', 'danger')

    return render_template('login.html')

# -------------------- LOGOUT --------------------
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('home'))

# -------------------- EMPLOYER DASHBOARD --------------------
@app.route('/employer/dashboard', methods=['GET','POST'])
def employer_dashboard():
    if not session.get('is_employer'):
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))

    user = User.query.get(session['user_id'])

    # Posting new job
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        company = request.form['company']
        location = request.form['location']

        job = Job(title=title, description=description, company=company, location=location, employer_id=user.id)
        db.session.add(job)
        db.session.commit()

        flash('Job posted successfully!', 'success')
        return redirect(url_for('employer_dashboard'))

    jobs = Job.query.filter_by(employer_id=user.id).order_by(Job.posted_at.desc()).all()
    return render_template('employer_dashboard.html', jobs=jobs)

# -------------------- CANDIDATE DASHBOARD --------------------
@app.route('/candidate/dashboard')
def candidate_dashboard():
    if not session.get('user_id') or session.get('is_employer'):
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))

    user = User.query.get(session['user_id'])
    return render_template('candidate_dashboard.html', applications=user.applications)

# -------------------- APPLY FOR JOB --------------------
@app.route('/apply/<int:job_id>', methods=['GET','POST'])
def apply(job_id):
    job = Job.query.get_or_404(job_id)

    if request.method == 'POST':
        file = request.files['resume']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        application = Application(
            job_id=job_id,
            candidate_id=session['user_id'],
            resume=filename,
            message=request.form['message']
        )
        db.session.add(application)
        db.session.commit()

        flash('Application submitted successfully!', 'success')
        return redirect(url_for('candidate_dashboard'))

    return render_template('apply.html', job=job)

# -------------------- EDIT JOB --------------------
@app.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)

    # Only employer who posted can edit
    if job.employer_id != session.get('user_id'):
        flash('Access denied.', 'danger')
        return redirect(url_for('employer_dashboard'))

    if request.method == 'POST':
        job.title = request.form['title']
        job.company = request.form['company']
        job.location = request.form['location']
        job.description = request.form['description']
        db.session.commit()

        flash('Job updated successfully!', 'success')
        return redirect(url_for('employer_dashboard'))

    return render_template('edit_job.html', job=job)

# -------------------- DELETE JOB --------------------
@app.route('/delete_job/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)

    # Only employer who posted can delete
    if job.employer_id != session.get('user_id'):
        flash('Access denied.', 'danger')
        return redirect(url_for('employer_dashboard'))

    db.session.delete(job)
    db.session.commit()
    flash('Job and its applications deleted successfully!', 'success')
    return redirect(url_for('employer_dashboard'))

# -------------------- RUN APP --------------------
if __name__ == "__main__":
    app.run(debug=False)
