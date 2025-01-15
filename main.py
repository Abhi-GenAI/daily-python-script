from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import smtplib
import time
import csv
import os
from dotenv import load_dotenv
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager


chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")  # Disable sandboxing for security
chrome_options.add_argument("--disable-dev-shm-usage")  # Disable /dev/shm usage


# Automatically download and use the correct version of ChromeDriver
service = Service(ChromeDriverManager().install())

driver=webdriver.Chrome(service=service,options=chrome_options)

url="https://www.chittorgarh.com/report/ipo-subscription-status-live-bidding-data-bse-nse/21/"

driver.get(url)

time.sleep(5)

page=driver.page_source

soup=BeautifulSoup(page,'lxml')

mytable=soup.find('table',{'id':"report_table"})

if mytable:
    # If the table is found, prettify it and save it to a file
    final_output = mytable.prettify()

    with open("ipo_data.csv", "w", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Extract and write the table headers (column names)
        headers = [header.text.strip() for header in mytable.find_all('th')]
        writer.writerow(headers)  # Write headers to CSV

        # Extract and write the table rows
        rows = mytable.find_all('tr')[1:]  # Skip the header row
        for row in rows:
            cols = row.find_all('td')  # Get all columns in the row
            data = [col.text.strip() for col in cols]  # Extract the text and remove extra spaces
            writer.writerow(data)    

    print("Table has been written to ipo_data.html")
else:
    print("Table not found. Please check the class name or inspect the page.")    

driver.quit()

file_ipo="ipo_data.csv"
df=pd.read_csv(file_ipo)
html_table=df.to_html(index=False)


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
    {html_table}
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