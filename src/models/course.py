from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db, User

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    creator = db.relationship('User', backref='created_courses', foreign_keys=[created_by_user_id])
    lectures = db.relationship('Lecture', backref='course', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Course {self.title}>'

class Lecture(db.Model):
    __tablename__ = 'lectures'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    video_url = db.Column(db.String(500), nullable=True)
    text_content = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, default=0)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Lecture {self.title}>'
