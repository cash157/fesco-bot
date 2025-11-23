from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

from webdriver_manager.chrome import ChromeDriverManager

# ----------------- Chrome options -----------------
chrome_options = Options()
chrome_options.add_argument("--headless=new")  # Headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
wait = WebDriverWait(driver, 15)  # 15 seconds timeout

# ----------------- Step 1: Open FESCO bill website -----------------
driver.get("https://bill.pitc.com.pk/fescobill")

# ----------------- Step 2: Enter reference number -----------------
ref_number = "12132450516000"
try:
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="searchTextBox"]'))).send_keys(ref_number)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btnSearch"]'))).click()
except Exception as e:
    print("Error entering reference number or clicking search:", e)

# ----------------- Step 3: Helper function -----------------
def get_text(xpath):
    try:
        return wait.until(EC.presence_of_element_located((By.XPATH, xpath))).text.strip()
    except:
        return ""

# ----------------- Step 4: Scrape data -----------------
data = {
    "reference_number": get_text('/html/body/div[3]/div[2]/div[2]/table/tbody/tr[4]/td[1]'),
    "customer_name": get_text('/html/body/div[3]/div[2]/table[2]/tbody/tr/td[1]/table/tbody/tr[2]/td[1]/p/span[2]'),
    "bill_month": get_text('/html/body/div[3]/div[2]/table[1]/tbody/tr[2]/td[4]'),
    "reading_date": get_text('/html/body/div[3]/div[2]/table[1]/tbody/tr[2]/td[5]'),
    "issue_date": get_text('/html/body/div[3]/div[2]/table[1]/tbody/tr[2]/td[6]'),
    "due_date": get_text('/html/body/div[3]/div[2]/table[1]/tbody/tr[2]/td[7]'),
    "previous_reading": get_text('/html/body/div[3]/div[2]/table[2]/tbody/tr/td[1]/table/tbody/tr[5]/td[2]'),
    "present_reading": get_text('/html/body/div[3]/div[2]/table[2]/tbody/tr/td[1]/table/tbody/tr[5]/td[3]'),
    "units": get_text('/html/body/div[3]/div[2]/table[2]/tbody/tr/td[1]/table/tbody/tr[5]/td[5]'),
    "payable_within_due": get_text('/html/body/div[3]/div[2]/div[6]/div[3]/table/tbody/tr[1]/td[5]')
}

# ----------------- Step 5: Payable after due -----------------
full_text = wait.until(EC.presence_of_element_located(
    (By.XPATH, '/html/body/div[3]/div[2]/div[6]/div[3]/table/tbody/tr[2]/td[5]/div/div[1]')
)).text
lines = full_text.split("\n")
data["payable_after_due"] = lines[1].strip() if len(lines) >= 2 else lines[0].strip()

# ----------------- Step 6: Arrears -----------------
full_arrears = wait.until(EC.presence_of_element_located(
    (By.XPATH, '/html/body/div[3]/div[2]/div[4]/table[2]/tbody/tr[2]/td[2]')
)).text
data["arrears"] = full_arrears.split('/')[0].strip()

# ----------------- Step 7: Post to your API -----------------
payload = {
    "reference_no": data["reference_number"],
    "customer_name": data["customer_name"],
    "bill_month": data["bill_month"],
    "reading_date": data["reading_date"],
    "issue_date": data["issue_date"],
    "due_date": data["due_date"],
    "previous_reading": data["previous_reading"],
    "present_reading": data["present_reading"],
    "units": data["units"],
    "arrears": data["arrears"],
    "payable_within_due_date": data["payable_within_due"],
    "payable_after_due_date": data["payable_after_due"]
}

response = requests.post("https://muhammad33434.pythonanywhere.com/api/save_bill", json=payload)
print("STATUS:", response.status_code)
print("TEXT:", response.text)

driver.quit()
