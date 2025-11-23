from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time, requests

# Initialize the driver

chrome_options = Options()
chrome_options.add_argument("--headless")  
chrome_options.add_argument("--disable-gpu") 
chrome_options.add_argument("--no-sandbox") 
chrome_options.add_argument("--disable-dev-shm-usage") 
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=chrome_options)


# Step 1: Open FESCO bill website

driver.get("https://bill.pitc.com.pk/fescobill")

# Step 2: Enter reference number and click search

ref_number = "12132450516000"
try:
    driver.find_element(By.XPATH, '//*[@id="searchTextBox"]').send_keys(ref_number)
    driver.find_element(By.XPATH, '//*[@id="btnSearch"]').click()
except Exception as e:
    print("Error entering reference number or clicking search:", e)

# Step 3: Wait for bill data to load

time.sleep(8)

# Step 4: Helper function to safely get text

def get_text(xpath):
    try:
        return driver.find_element(By.XPATH, xpath).text.strip()
    except:
        return ""

# Step 5: Scrape data

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
"payable_within_due": get_text('/html/body/div[3]/div[2]/div[6]/div[3]/table/tbody/tr[1]/td[5]'),
}



# Grab the full text including line breaks
full_text = driver.find_element(
    By.XPATH,
    '/html/body/div[3]/div[2]/div[6]/div[3]/table/tbody/tr[2]/td[5]/div/div[1]'
).text
lines = full_text.split("\n")
if len(lines) >= 2:
    payable_after_due = lines[1].strip()
else:
    payable_after_due = lines[0].strip()  # fallback

data["payable_after_due"] = payable_after_due



# Grab the full text from the arrears cell
full_arrears = driver.find_element(
    By.XPATH, '/html/body/div[3]/div[2]/div[4]/table[2]/tbody/tr[2]/td[2]'
).text  # use .text for visible text

arrears_value = full_arrears.split('/')[0].strip()
data["arrears"] = arrears_value



# Step 6: Open target website

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

response = requests.post(
    "https://muhammad33434.pythonanywhere.com/api/save_bill",
    json=payload
)

print("STATUS:", response.status_code)
print("TEXT:", response.text)

