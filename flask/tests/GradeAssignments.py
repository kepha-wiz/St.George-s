import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By 
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import os

basename = os.getcwd()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + basename + '/../instance/database.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Admin/amey3/EduPool/flask/instance/database.db'
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    DOB = db.Column(db.String(150))
    user_type = db.Column(db.String(50))

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.Integer(), unique=True)
    course_name = db.Column(db.String(150))
    course_limit = db.Column(db.Integer)
    course_desc = db.Column(db.String(1000))
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key=True)
    quiz_name = db.Column(db.String(150))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

class QuizQuestion(db.Model):
    __tablename__ = 'quizQuestions'
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(150))
    max_grade = db.Column(db.Integer)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'))

class QuizSubmission(db.Model):
    __tablename__ = 'quizSubmissions'
    id = db.Column(db.Integer, primary_key=True)
    given_grade = db.Column(db.Integer)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'))
    quizQuestion_id = db.Column(db.Integer, db.ForeignKey('quizQuestions.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class LoginTestCase(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()  # Initialize WebDriver
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def test_submit_grade_quiz(self):
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

        # Check if the screen changes after successful login
        self.assertNotEqual(driver.current_url, "http://127.0.0.1:5000", "Screen should change after successful login")

        # Click on the first course button under enrolled courses
        course_button = driver.find_element(By.ID, "course")
        course_button.click()
        #return
        # Click on the first grade quiz button under grade assignments section
        grade_quiz_button = driver.find_element(By.ID, "grade_quiz_button")
        grade_quiz_button.click()

        # Enter number 1 in all the grade question boxes
        grade_question_inputs = driver.find_elements(By.CLASS_NAME, "grade_question_input")
        for input_box in grade_question_inputs:
            input_box.send_keys("1")

        # Click on the submit grade button
        submit_grade_button = driver.find_element(By.ID, "submit_grade_button")
        submit_grade_button.click()

        # Check that the screen changes
        self.assertNotEqual(driver.current_url, "http://127.0.0.1:5000", "Screen should change after submitting grade")

    def tearDown(self):
        self.driver.quit()
        self.app_context.pop()

if __name__ == "__main__":
    unittest.main()
