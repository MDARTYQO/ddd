from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# הגדר את פרטי ההתחברות שלך
USERNAME = "your_email@example.com"
PASSWORD = "your_password"

# כתובת האתר
LOGIN_URL = "https://aistodyo.com/login"
API_KEYS_URL = "https://aistodyo.com/account/api-keys"

driver = webdriver.Chrome()
driver.get(LOGIN_URL)

# הכנס שם משתמש
driver.find_element(By.ID, "email").send_keys(USERNAME)
# הכנס סיסמה
driver.find_element(By.ID, "password").send_keys(PASSWORD)
# לחץ על כפתור התחברות
driver.find_element(By.ID, "login-button").click()

time.sleep(5)  # המתן לטעינה

# נווט לאזור המפתחות
driver.get(API_KEYS_URL)
time.sleep(2)

# לחץ על כפתור יצירת מפתח חדש
driver.find_element(By.ID, "create-api-key").click()
time.sleep(2)

# שלוף את המפתח שנוצר
api_key = driver.find_element(By.CLASS_NAME, "api-key-value").text
print("API Key:", api_key)

driver.quit()
