#from selenium.webdriver import Firefox, FirefoxOptions
#from selenium.webdriver.firefox.service import Service as FirefoxService
#from webdriver_manager.firefox import GeckoDriverManager

#options = FirefoxOptions()
#options.binary ='C:/Program Files/Mozilla Firefox/firefox.exe' # on Windows

#driver = Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
#driver.get('https://www.google.com')


import unittest
import pytest



from selenium import webdriver



from unittest.mock import MagicMock



from selenium.webdriver.chrome.service import Service
#from webdriver_manager.chrome import ChromeDriverManager
#from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.firefox import GeckoDriverManager
#from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from flask import Flask
#from webdriver_manager.chrome import ChromeDriverManager

#driver = webdriver.Chrome(ChromeDriverManager().install())

app = Flask(__name__)

class LoginTestCase(unittest.TestCase):
    def setUp(self):
        options = ChromeOptions()
        options.add_argument("--headless=new")
        #options.headless = True
        #self.driver = webdriver.Firefox(options=options)  # Initialize WebDriver
        # Mocking the WebDriver
        # driver = MagicMock()
        self.driver = webdriver.Chrome(options=options)  # Initialize WebDriver

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
