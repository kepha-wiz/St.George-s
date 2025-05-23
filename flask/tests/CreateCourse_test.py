import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By

class LoginTestCase(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()  # Initialize WebDriver

    def test_blank_course_code(self): # Test scenario: Create account with blank course code
        driver = self.driver
        driver.get("http://127.0.0.1:5000/create-course")  # Navigate to Create Account URL

        # Find the create account button and click it without entering the email
        create_course_button = driver.find_element(By.ID, "create_course_button")
        create_course_button.click()  # Click the create account button

        # Check if the screen remains on the same page
        self.assertEqual(driver.current_url, "http://127.0.0.1:5000/create-course", "Screen should remain on the same page")

    def test_blank_course_name(self): # Test scenario: Create account with blank course name
        driver = self.driver
        driver.get("http://127.0.0.1:5000/create-course")  # Navigate to Create Account URL

	  # Enter an email without entering the password
        courseCode_field = driver.find_element(By.ID, "course_code")
        courseCode_field.send_keys("COSC 310")

        # Find the create account button and click it without entering the email
        create_course_button = driver.find_element(By.ID, "create_course_button")
        create_course_button.click()  # Click the create account button

        # Check if the screen remains on the same page
        self.assertEqual(driver.current_url, "http://127.0.0.1:5000/create-course", "Screen should remain on the same page")
    def test_cancel_button(self):# Test scenario: Clicking cancel button redirects to previous page
        driver = self.driver
        driver.get("http://127.0.0.1:5000/create-course")  # Navigate to Create Account URL

        # Find the cancel account button and click it without entering the email
        cancel_button = driver.find_element(By.ID, "cancel_button")
        cancel_button.click()  # Click the cancel account button

        # Check if the screen remains on the same page
        self.assertNotEqual(driver.current_url, "http://127.0.0.1:5000/create-course", "Screen should remain on the same page")
    
    def tearDown(self):
        self.driver.quit()  # Clean up after the test

if __name__ == "__main__":
    unittest.main()
