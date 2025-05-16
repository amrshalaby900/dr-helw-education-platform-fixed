from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db, User
from src.models.course import Course, Lecture

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    lecture_id = db.Column(db.Integer, db.ForeignKey('lectures.id'), nullable=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    course = db.relationship('Course', backref='quizzes')
    lecture = db.relationship('Lecture', backref='quizzes')
    questions = db.relationship('Question', backref='quiz', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Quiz {self.title}>'

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), default='multiple_choice')
    options = db.Column(db.Text, nullable=True)  # JSON string for multiple choice options
    correct_answer = db.Column(db.Text, nullable=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student_answers = db.relationship('StudentAnswer', backref='question', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Question {self.id}: {self.text[:20]}...>'

class StudentAnswer(db.Model):
    __tablename__ = 'student_answers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    answer_text = db.Column(db.Text, nullable=True)
    is_correct = db.Column(db.Boolean, default=False)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='answers')
    
    def __repr__(self):
        return f'<StudentAnswer {self.id} by User {self.user_id}>'
