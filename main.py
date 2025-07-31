import datetime
import requests
import smtplib
from email.message import EmailMessage

# CONFIG
TO_EMAIL = "your_email@example.com"
FROM_EMAIL = "your_bot_email@example.com"
APP_PASSWORD = "your_app_password"
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
    msg["To"] = TO_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(FROM_EMAIL, APP_PASSWORD)
        smtp.send_message(msg)

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
