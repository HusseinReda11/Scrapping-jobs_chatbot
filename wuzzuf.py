import sqlite3
import pandas as pd
from W_db import store_jobs_in_db
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlencode
from datetime import datetime, timedelta
import re
import time

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def generate_url(query):
    params = {'q': query}
    return f"https://wuzzuf.net/search/jobs/?{urlencode(params)}"

def get_posted_date(time_posted):
    match = re.search(r'(\d+)', time_posted)
    if match:
        number = int(match.group(1))
        if "day" in time_posted:
            return (datetime.now() - timedelta(days=number)).strftime('%d-%m-%Y')
        elif "hour" in time_posted:
            return (datetime.now() - timedelta(hours=number)).strftime('%d-%m-%Y')
        elif "minute" in time_posted:
            return (datetime.now() - timedelta(minutes=number)).strftime('%d-%m-%Y')
        elif "month" in time_posted:
            return (datetime.now() - timedelta(days=number*30)).strftime('%d-%m-%Y')
    return "غير مذكور"

def W_scrape_jobs(job_titles, max_pages=1):
    driver = setup_driver()
    wait = WebDriverWait(driver, 10)
    jobs_data = []

    try:
        for job_title in job_titles:
            url = generate_url(job_title)
            driver.get(url)
            current_page = 1

            while current_page <= max_pages:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.css-1gatmva.e1v1l3u10")))
                job_cards = driver.find_elements(By.CSS_SELECTOR, "div.css-1gatmva.e1v1l3u10")

                for card in job_cards:
                    try:
                        job_link = card.find_element(By.CSS_SELECTOR, "a.css-o171kl").get_attribute("href")
                        job_id = job_link.split('/')[-1]

                        try:
                            time_posted = card.find_element(By.CSS_SELECTOR, "div.css-d7j1kk div.css-4c4ojb").text
                        except:
                            try:
                                time_posted = card.find_element(By.CSS_SELECTOR, "div.css-d7j1kk div.css-do6t5g").text
                            except:
                                time_posted = "Time not found"

                        posted_date = get_posted_date(time_posted)

                        job_info = {
                            "ID": job_id,
                            "Title": card.find_element(By.CSS_SELECTOR, "a.css-o171kl").text,
                            "Company": card.find_element(By.CSS_SELECTOR, "a.css-17s97q8").text,
                            "Location": card.find_element(By.CSS_SELECTOR, "span.css-5wys0k").text,
                            "Posted_Date": posted_date,
                            "Job_Type": card.find_element(By.CSS_SELECTOR, "span.css-1ve4b75.eoyjyou0").text,
                            "Search_Query": job_title,
                            "Page": current_page,
                            "Job_Link": job_link,
                            "Description": "وصف الوظيفة غير متوفر",
                            "Skills": "غير مذكورة",
                            "Experience_Needed": "غير مذكور"
                        }

                        jobs_data.append(job_info)
                    except Exception as e:
                        print("تخطي كارد بسبب خطأ:", e)
                        continue

                try:
                    next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.css-zye1os.ezfki8j0")))
                    driver.execute_script("arguments[0].click();", next_button)
                    current_page += 1
                    time.sleep(1)
                except:
                    break
    finally:
        driver.quit()

    jobs_df = pd.DataFrame(jobs_data)
    store_jobs_in_db(jobs_df)
    return jobs_df

# الاستخدام
job_titles = ["Flutter", "software engineer"]
jobs_df = W_scrape_jobs(job_titles, 1)

# عرض عدد الوصفوص (اختياري)
conn = sqlite3.connect("job.db")
query = "SELECT description FROM jobs"
db_data = pd.read_sql_query(query, conn)
conn.close()

for line in range(len(db_data)):
    _ = len(db_data['description'][line])



