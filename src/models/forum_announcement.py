from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db, User
from src.models.course import Course

class ForumTopic(db.Model):
    __tablename__ = 'forum_topics'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_post_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', backref='created_topics', foreign_keys=[created_by_user_id])
    course = db.relationship('Course', backref='forum_topics')
    posts = db.relationship('ForumPost', backref='topic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ForumTopic {self.title}>'

class ForumPost(db.Model):
    __tablename__ = 'forum_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('forum_topics.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    parent_post_id = db.Column(db.Integer, db.ForeignKey('forum_posts.id'), nullable=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    author = db.relationship('User', backref='forum_posts')
    replies = db.relationship('ForumPost', backref=db.backref('parent_post', remote_side=[id]))
    
    def __repr__(self):
        return f'<ForumPost {self.id} by User {self.user_id}>'

class Announcement(db.Model):
    __tablename__ = 'announcements'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=True)
    is_published = db.Column(db.Boolean, default=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', backref='created_announcements')
    course = db.relationship('Course', backref='announcements')
    
    def __repr__(self):
        return f'<Announcement {self.title}>'
