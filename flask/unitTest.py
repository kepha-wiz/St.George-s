import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from flask import Flask

app = Flask(__name__)

class LoginTestCase(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()  # Initialize WebDriver

    def test_login_username_required(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000")  # Navigate to URL

        # Find the login button and click it without entering username/password
        login_button = driver.find_element(By.ID, "submit")
        login_button.click()  # Click the login button

        # Check if the login form is still visible
        login_form = driver.find_element(By.TAG_NAME, "form")
        self.assertTrue(login_form.is_displayed(), "Login form should still be visible")

    def test_login_password_required(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000")  # Navigate to URL

        # Find the username field and enter a username
        username_field = driver.find_element(By.ID, "username")
        username_field.send_keys("testuser")

        # Find the login button and click it without entering the password
        login_button = driver.find_element(By.ID, "submit")
        login_button.click()  # Click the login button

        # Check if the login form is still visible
        login_form = driver.find_element(By.TAG_NAME, "form")
        self.assertTrue(login_form.is_displayed(), "Login form should still be visible")

    def tearDown(self):
        self.driver.quit()  # Clean up after the test

if __name__ == "__main__":
    unittest.main()

