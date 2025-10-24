from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_employer = db.Column(db.Boolean, default=False)
    
    # Relationship for jobs and applications
    jobs = db.relationship('Job', backref='employer', lazy=True, cascade='all, delete-orphan')
    applications = db.relationship('Application', backref='candidate', lazy=True, cascade='all, delete-orphan')


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    employer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Cascade delete applications automatically
    applications = db.relationship('Application', backref='job', lazy=True, cascade='all, delete-orphan')


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resume = db.Column(db.String(200))
    message = db.Column(db.Text)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
