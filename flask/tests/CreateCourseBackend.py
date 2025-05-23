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
    username = db.Column(db.String(150), unique=True)  # Email for username
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    DOB =  db.Column(db.String(150))
    user_type = db.Column(db.String(50))

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.Integer(), unique=True)
    course_name = db.Column(db.String(150))
    course_limit = db.Column(db.Integer)
    course_desc = db.Column(db.String(1000))
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))

# Other models definitions...

class AdminTestCase(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()  # Initialize WebDriver
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def test_create_course(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000")  # Navigate to Login Page URL
        # Query the database to retrieve a random user of type "Admin"
        random_user = User.query.filter_by(user_type='admin').order_by(func.random()).first()

        # Fill in the login fields with the username and password of the random user
        username_field = driver.find_element(By.ID, "username")
        username_field.send_keys(random_user.username)

        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(random_user.password)

        # Find the login button and click it
        login_button = driver.find_element(By.ID, "submit")
        login_button.click()  # Click the login button

        # Check if the home screen shows up after successful login
        self.assertNotEqual(driver.current_url, "http://127.0.0.1:5000", "Screen should change after successful login")

        # Click on the "Create Course" link
        create_course_link = driver.find_element(By.ID, "create_course_link")
        create_course_link.click()

        # Enter details in the create course page
        course_code_field = driver.find_element(By.ID, "course_code")
        course_code_field.send_keys("COURSE106")

        course_name_field = driver.find_element(By.ID, "course_name")
        course_name_field.send_keys("Introduction to Python")

        course_desc_field = driver.find_element(By.ID, "course_desc")
        course_desc_field.send_keys("A beginner's guide to Python programming.")

        course_limit_field = driver.find_element(By.ID, "course_limit")
        course_limit_field.send_keys("30")

        teacher_id_field = driver.find_element(By.ID, "teacher_id")
        teacher_id_field.send_keys("1")  # Assuming teacher ID is 1

        # Find and click on the "Create Course" button
        create_course_button = driver.find_element(By.ID, "create_course_button")
        create_course_button.click()


        # Query the database to check if the course appears in the request section
        x = Course.query.with_entities(Course.course_code=="110").all()
        #print(x)
        for i in x :
          if i[0]:
            self.assertIsNotNone(i[0], "Course Code //")  
          

   
        #user = User.query.filter(User.username=="student@student.com")   
        #print('x')
        #print(user)
        #print('x')
        #user = User.query.filter_by(username="student@student.com")
        #print('x')
        #print(user)
        #print(user.username)
        #print('x')
        #if user:
        #    requested_course = Request.query.filter_by(user_id=users.id).first()
        #    self.assertIsNotNone(requested_course, "Course should appear in the request section")
        #user = User.query.filter_by(User.username=="student@student.com").first()
        #print(user)



        #user = User.query.filter_by(username="valid_student_email@example.com").first()
        
        # Query the database to check if the course is added
        #if user:
        #    created_course = Request.query.filter_by(course_id=course.id).first()
        #    self.assertIsNotNone(created_course, "Course should appear in the course section")
        
        #course = Course.query.filter_by(course_code="COURSE101").first()
        #print(course)
        #self.assertIsNotNone(course, "Course should be added to the database")

    def tearDown(self):
        self.driver.quit()
        self.app_context.pop()

if __name__ == "__main__":
    unittest.main()