from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import smtplib
import time
import csv
import os 
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3" 
from dotenv import load_dotenv
import pandas as pd
import google.generativeai as genai


service=Service(executable_path="chromedriver.exe")
driver=webdriver.Chrome(service=service)

url="https://www.chittorgarh.com/report/ipo-subscription-status-live-bidding-data-bse-nse/21/"

driver.get(url)

time.sleep(5)

page=driver.page_source

soup=BeautifulSoup(page,'lxml')

html_content=str(soup)

load_dotenv()

#demo

API_key=os.getenv("GEMINI_API_KEY")
if not API_key:
    print("API Key not found. Check your .env file or environment variables.")
else:
    print("API Key loaded successfully.")


genai.configure(api_key=API_key)


table = soup.find("table", id="report_table") 

model = genai.GenerativeModel("gemini-pro")

prompt = f"""
Extract the following HTML table data into a clear, structured CSV format with proper headers:

{table}
"""

# Generate the formatted table using Gemini

try:
    response = genai.GenerativeModel("gemini-pro").generate_content(prompt)
    if response and response.candidates:
        # Extract the table content
        content = response.candidates[0].content.parts[0].text

        # Save to a CSV file
        with open("ipo_subscription_data.csv", "w", encoding="utf-8") as file:
            file.write(content)

        print("Table data saved to ipo_subscription_data.csv")
    else:
        print("No response candidates received from Gemini API.")
except Exception as e:
    print(f"An error occurred: {e}")


load_dotenv()
my_email=os.getenv("myemail")
password=os.getenv("mypassword")

connection=smtplib.SMTP("smtp.gmail.com")
connection.starttls()
connection.login(user=my_email, password=password)
subject = "IPO Data"
body = f"""
<html>
  <body>
    <p>Dear Abhishek,</p>
    <p>Please find the IPO data below:</p>
    {table}
    <p>Best regards,</p>
    <p>Abhishek</p>
  </body>
</html>
"""

connection.sendmail(
    from_addr=my_email,
    to_addrs="abhishekbikumalla1@gmail.com",
    msg=f"Subject: {subject}\nContent-Type: text/html\n\n{body}"
)
connection.close()