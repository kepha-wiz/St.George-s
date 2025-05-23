import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By 
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy.sql import func
import flask
import os

import sys
sys.path.append('../')
#sys.path.append('C:/Users/Admin/amey3/EduPool/flask/')
#from . import db


from flask_login import UserMixin
from sqlalchemy.sql import func


basename = os.getcwd()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + basename + '/../instance/database.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Admin/amey3/EduPool/flask/instance/database.db'
db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id=db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique = True) #email for username
    password=db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    DOB =  db.Column(db.String(150))
    user_type = db.Column(db.String(50))
    
class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.Integer(), unique = True)
    course_name = db.Column(db.String(150))
    course_limit = db.Column(db.Integer)
    course_desc = db.Column(db.String(1000))
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
class Request(db.Model, UserMixin):
    __tablename__ = 'requests'
    id=db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    
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
    question = db.Column(db.String(150))
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

class Reply(db.Model):
    __tablename__ = 'replies'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000))
    date_posted = db.Column(db.DateTime(timezone=True), default=func.now())
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussions.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class AdminTestCase(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()  # Initialize WebDriver
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def test_create_assignment_quiz(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000")  # Navigate to Login Page URL

        # Query the database to retrieve a random user of type "Teacher"
        random_teacher = User.query.filter_by(user_type='teacher').order_by(func.random()).first()

        # Fill in the login fields with the username and password of the random teacher
        username_field = driver.find_element(By.ID, "username")
        username_field.send_keys(random_teacher.username)

        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(random_teacher.password)

        # Find the login button and click it
        login_button = driver.find_element(By.ID, "submit")
        login_button.click()  # Click the login button

        # Check if the home screen shows up after successful login
        self.assertNotEqual(driver.current_url, "http://127.0.0.1:5000", "Screen should change after successful login")

        # Find the first enrolled course and click on it
        enrolled_courses = driver.find_elements(By.CLASS_NAME, "card")
        enrolled_courses[0].click()

        # Find the "Create Assignment" button and click it
        create_assignment_button = driver.find_element(By.ID, "create_assignment_button")
        create_assignment_button.click()

        # Enter assignment details
        title_field = driver.find_element(By.ID, "title")
        title_field.send_keys("Sample Assignment Title")

        # Select the "Quiz" assignment type radio button
        quiz_radio_button = driver.find_element(By.ID, "quiz")
        quiz_radio_button.click()

        # Enter a random question and options
        question_field = driver.find_element(By.ID, "question1")
        question_field.send_keys("What is the capital of France?")

        option_a_field = driver.find_element(By.ID, "option1-1")
        option_a_field.send_keys("Paris")

        option_b_field = driver.find_element(By.ID, "option1-2")
        option_b_field.send_keys("Rome")

        option_c_field = driver.find_element(By.ID, "option1-3")
        option_c_field.send_keys("Berlin")

        # Enter 10 in the max grade section
        max_grade_field = driver.find_element(By.ID, "que-max-grade1")
        max_grade_field.send_keys("10")

        # Click the "Post Assignment" button
        post_assignment_button = driver.find_element(By.ID, "post-assignment-button")
        post_assignment_button.click()

        # Query the database to check if the assignment has been posted under quizzes section
        # Assuming you have a model named Assignment and the assignment appears under quizzes section
        posted_assignment = Quiz.query.filter_by(quiz_name='QUIZ 1').first()
        self.assertIsNotNone(posted_assignment, "Assignment should be posted under quizzes section")

    def test_create_assignment_essay(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000")  # Navigate to Login Page URL

        # Query the database to retrieve a random user of type "Teacher"
        random_teacher = User.query.filter_by(user_type='teacher').order_by(func.random()).first()

        # Fill in the login fields with the username and password of the random teacher
        username_field = driver.find_element(By.ID, "username")
        username_field.send_keys(random_teacher.username)

        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(random_teacher.password)

        # Find the login button and click it
        login_button = driver.find_element(By.ID, "submit")
        login_button.click()  # Click the login button

        # Check if the home screen shows up after successful login
        self.assertNotEqual(driver.current_url, "http://127.0.0.1:5000", "Screen should change after successful login")

        # Find the first enrolled course and click on it
        enrolled_courses = driver.find_elements(By.CLASS_NAME, "card")
        enrolled_courses[0].click()

        # Find the "Create Assignment" button and click it
        create_assignment_button = driver.find_element(By.ID, "create_assignment_button")
        create_assignment_button.click()

        # Enter assignment details
        title_field = driver.find_element(By.ID, "title")
        title_field.send_keys("Sample Assignment Title")

        # Select the "Essay" assignment type radio button
        essay_radio_button = driver.find_element(By.ID, "essay")
        essay_radio_button.click()

        # Select "Enter Text" under content type
        text_content_radio = driver.find_element(By.ID, "textRadio")
        text_content_radio.click()

        # Enter a random question in the text entry box
        text_entry_field = driver.find_element(By.ID, "text-entry-essay")
        text_entry_field.send_keys("Write a short essay on the importance of education.")

        # Enter 10 in the max grade section
        max_grade_field = driver.find_element(By.ID, "essay-max-grade-input")
        max_grade_field.send_keys("10")

        # Click the "Post Assignment" button
        post_assignment_button = driver.find_element(By.ID, "post-assignment-button")
        post_assignment_button.click()

        # Query the database to check if the assignment has been posted under essays section
        # Assuming you have a model named Quiz and the quiz appears under essays section
        posted_assignment = Essay.query.filter_by(essay_name='Sample Assignment Title').first()
        self.assertIsNotNone(posted_assignment, "Assignment should be posted under essays section")


    def tearDown(self):
        self.driver.quit()
        self.app_context.pop()

if __name__ == "__main__":
    unittest.main()