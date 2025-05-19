import flask
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id=db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique = True) #email for username
    password=db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    DOB =  db.Column(db.String(150))
    user_type = db.Column(db.String(50))
    # discussions = db.relationship('Discussion', back_populates='author')
    # replies = db.relationship('Reply', back_populates='author')
    
class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.Integer(), unique = True)
    course_name = db.Column(db.String(150))
    course_limit = db.Column(db.Integer)
    course_desc = db.Column(db.String(1000))
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    resources = db.Column(db.String(150), nullable=True)
    resource_link = db.Column(db.String(300), nullable=True)

    
class Request(db.Model, UserMixin):
    __tablename__ = 'requests'
    id=db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    status = db.Column(db.String(50), default='pending')

class Enrollment(db.Model, UserMixin):
    __tablename__ = 'enrollments'
    id=db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

class Quiz(db.Model, UserMixin):
    __tablename__ = 'quizzes'
    id=db.Column(db.Integer, primary_key=True)
    quiz_name = db.Column(db.String(150))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

class QuizQuestion(db.Model, UserMixin):
    __tablename__ = 'quizQuestions'
    id=db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(150))
    option1 = db.Column(db.String(150))
    option2 = db.Column(db.String(150))
    option3 = db.Column(db.String(150))
    max_grade = db.Column(db.Integer)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'))
    
class QuizSubmission(db.Model, UserMixin):
    __tablename__ = 'quizSubmissions'
    id=db.Column(db.Integer, primary_key=True)
    selected_option = db.Column(db.String(150))
    given_grade = db.Column(db.Integer)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'))
    quizQuestion_id = db.Column(db.Integer, db.ForeignKey('quizQuestions.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Essay(db.Model, UserMixin):
    __tablename__ = 'essays'
    id=db.Column(db.Integer, primary_key=True)
    essay_name = db.Column(db.String(150))

    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

class EssayQuestion(db.Model, UserMixin):
    __tablename__ = 'essayQuestions'
    id=db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(150))
    file_upload = db.Column(db.LargeBinary)
    question_type = db.Column(db.String(150))
    max_grade = db.Column(db.Integer)
    essay_id = db.Column(db.Integer, db.ForeignKey('essays.id'))

class EssaySubmission(db.Model, UserMixin):
    __tablename__ = 'essaySubmissions'
    id=db.Column(db.Integer, primary_key=True)
    answer_text = db.Column(db.String(150))
    answer_file = db.Column(db.LargeBinary)
    answer_type = db.Column(db.String(150))
    given_grade = db.Column(db.Integer)
    essay_id = db.Column(db.Integer, db.ForeignKey('essays.id'))
    essayQuestion_id = db.Column(db.Integer, db.ForeignKey('essayQuestions.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Discussion(db.Model):
    __tablename__ = 'discussions'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    content = db.Column(db.String(1000))
    date_posted = db.Column(db.DateTime(timezone=True), default=func.now())
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # replies = db.relationship('Reply', backref='discussion', lazy=True)

    # # Relationships
    # author = db.relationship('User', back_populates='discussions')

class Reply(db.Model):
    __tablename__ = 'replies'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000))
    date_posted = db.Column(db.DateTime(timezone=True), default=func.now())
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussions.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


