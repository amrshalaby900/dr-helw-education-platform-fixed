from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db, User
from src.models.course import Course, Lecture

class StudentProgress(db.Model):
    __tablename__ = 'student_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lecture_id = db.Column(db.Integer, db.ForeignKey('lectures.id'), nullable=False)
    completed_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='progress')
    lecture = db.relationship('Lecture', backref='student_progress')
    
    def __repr__(self):
        return f'<StudentProgress User {self.user_id} Lecture {self.lecture_id}>'
