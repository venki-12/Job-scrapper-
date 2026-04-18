import time
import json
import os
import smtplib
from email.mime.text import MIMEText

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

URL = "https://jobs.fidelity.com/in/jobs/?search=&origin=global&lat=&lng="

KEYWORDS = [
    "senior data analyst",
    "lead data analyst"
    "lead IT data analyst",
    "analytics lead",
    "senior analyst",
    "data analyst"
]


EMAIL = os.environ["EMAIL"]
PASSWORD = os.environ["PASSWORD"]
TO_EMAIL = os.environ["TO_EMAIL"]

SEEN_FILE = "seen_jobs.json"


def load_seen_jobs():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_seen_jobs(seen_jobs):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen_jobs), f)


def fetch_jobs():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.get(URL)
    time.sleep(5)

    job_elements = driver.find_elements(By.TAG_NAME, "a")

    print("TOTAL LINKS FOUND:", len(job_elements))  # ✅ correct place

    jobs = []

    for job in job_elements:
        title = job.text.strip().lower()
        link = job.get_attribute("href")

        if not title or not link:
            continue

        print("FOUND:", title)  # debug

        if any(keyword in title for keyword in KEYWORDS):
            jobs.append((title, link))

    driver.quit()
    return jobs


def send_email(new_jobs):
    body = "\n\n".join([f"{title}\n{link}" for title, link in new_jobs])

    msg = MIMEText(body)
    msg["Subject"] = "New Data Analyst Jobs Found"
    msg["From"] = EMAIL
    msg["To"] = TO_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)


def main():
    seen_jobs = load_seen_jobs()
    jobs = fetch_jobs()

    new_jobs = [job for job in jobs if job[1] not in seen_jobs]

    if new_jobs:
        send_email(new_jobs)
        seen_jobs.update([job[1] for job in new_jobs])
        save_seen_jobs(seen_jobs)
        print("New jobs found and emailed!")
    else:
        print("No new jobs today.")


if __name__ == "__main__":
    main()