import datetime
import requests
import smtplib
from email.message import EmailMessage
import os

# ✅ LOAD FROM ENV VARIABLES (Render-safe)
TO_EMAILS = os.getenv("TO_EMAILS", "itsaboutgood@gmail.com").split(",")
FROM_EMAIL = os.getenv("FROM_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

BIBLE_API_URL = "https://bible-api.com/"

PLAN = {
    "07-31": ("1 Chronicles 7", "Romans 13"),
    "08-01": ("1 Chronicles 8", "Romans 14"),
    # Add more days here
}

def get_bible_text(passage):
    try:
        response = requests.get(BIBLE_API_URL + passage.replace(" ", "%20"))
        data = response.json()
        return data["text"]
    except Exception as e:
        return f"Error retrieving passage: {e}"

def get_today_readings():
    today = datetime.datetime.now().strftime("%m-%d")
    return PLAN.get(today, ("Genesis 1", "Matthew 1"))

def send_email(subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(FROM_EMAIL, APP_PASSWORD)
        for recipient in TO_EMAILS:
            msg["To"] = recipient
            smtp.send_message(msg)
            del msg["To"]  # Reset header for next recipient

def run_schedule():
    now = datetime.datetime.now()
    hour = now.hour

    ot, nt = get_today_readings()

    if hour == 6:
        body = f"📖 Daily Bread Reminder\n\nToday's Readings:\n- OT: {ot}\n- NT: {nt}"
        send_email("6AM: Daily Bread Reminder", body)

    elif hour == 12:
        text = get_bible_text(ot)
        send_email(f"12PM: Old Testament Reading – {ot}", text)

    elif hour == 18:
        text = get_bible_text(nt)
        send_email(f"6PM: New Testament Reading – {nt}", text)

if __name__ == "__main__":
    run_schedule()

