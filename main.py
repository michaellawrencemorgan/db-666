import datetime
import requests
import smtplib
from email.message import EmailMessage
import os

# ✅ Load from environment variables (Render-safe)
TO_EMAILS = os.getenv("TO_EMAILS", "itsaboutgood@gmail.com").split(",")
FROM_EMAIL = os.getenv("FROM_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

BIBLE_API_URL = "https://bible-api.com/"

# 📖 Bible chapter lists
OT_BOOKS = {
    "Genesis": 50, "Exodus": 40, "Leviticus": 27, "Numbers": 36, "Deuteronomy": 34,
    "Joshua": 24, "Judges": 21, "Ruth": 4, "1 Samuel": 31, "2 Samuel": 24,
    "1 Kings": 22, "2 Kings": 25, "1 Chronicles": 29, "2 Chronicles": 36,
    "Ezra": 10, "Nehemiah": 13, "Esther": 10, "Job": 42, "Psalms": 150,
    "Proverbs": 31, "Ecclesiastes": 12, "Song of Solomon": 8, "Isaiah": 66,
    "Jeremiah": 52, "Lamentations": 5, "Ezekiel": 48, "Daniel": 12,
    "Hosea": 14, "Joel": 3, "Amos": 9, "Obadiah": 1, "Jonah": 4, "Micah": 7,
    "Nahum": 3, "Habakkuk": 3, "Zephaniah": 3, "Haggai": 2, "Zechariah": 14, "Malachi": 4
}

NT_BOOKS = {
    "Matthew": 28, "Mark": 16, "Luke": 24, "John": 21, "Acts": 28,
    "Romans": 16, "1 Corinthians": 16, "2 Corinthians": 13, "Galatians": 6,
    "Ephesians": 6, "Philippians": 4, "Colossians": 4, "1 Thessalonians": 5,
    "2 Thessalonians": 3, "1 Timothy": 6, "2 Timothy": 4, "Titus": 3, "Philemon": 1,
    "Hebrews": 13, "James": 5, "1 Peter": 5, "2 Peter": 3, "1 John": 5, "2 John": 1,
    "3 John": 1, "Jude": 1, "Revelation": 22
}

def generate_chapter_list(book_dict):
    chapters = []
    for book, count in book_dict.items():
        chapters.extend([f"{book} {i}" for i in range(1, count + 1)])
    return chapters

OT_CHAPTERS = generate_chapter_list(OT_BOOKS)
NT_CHAPTERS = generate_chapter_list(NT_BOOKS)

def get_today_readings():
    start_date = datetime.datetime(2025, 8, 1)
    today = datetime.datetime.now()
    days_elapsed = (today - start_date).days
    ot_chapter = OT_CHAPTERS[days_elapsed % len(OT_CHAPTERS)]
    nt_chapter = NT_CHAPTERS[days_elapsed % len(NT_CHAPTERS)]
    return ot_chapter, nt_chapter

def get_bible_text(passage):
    try:
        response = requests.get(BIBLE_API_URL + passage.replace(" ", "%20"))
        data = response.json()
        return data["text"], data.get("verses", [])
    except Exception as e:
        return f"Error retrieving passage: {e}", []

def get_one_verse(verses):
    if verses and isinstance(verses, list):
        for v in verses:
            if v.get("text"):
                return f"{v.get('book_name')} {v.get('chapter')}:{v.get('verse')} – \"{v.get('text').strip()}\""
    return "⚠️ No verse found."

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
            del msg["To"]
    print(f"✅ {subject} email sent to {len(TO_EMAILS)} recipients: {TO_EMAILS}")

def run_schedule():
    now = datetime.datetime.now()
    hour = now.hour

    ot, nt = get_today_readings()

    if hour == 6:
        text_ot, verses_ot = get_bible_text(ot)
        text_nt, verses_nt = get_bible_text(nt)
        quote_ot = get_one_verse(verses_ot)
        quote_nt = get_one_verse(verses_nt)

        body = (
            f"📖 Daily Bread Reminder\n\n"
            f"Today's Readings:\n- OT: {ot}\n- NT: {nt}\n\n"
            f"🌟 OT Highlight: {quote_ot}\n"
            f"🌟 NT Highlight: {quote_nt}"
        )
        send_email("6AM: Daily Bread Reminder", body)

    elif hour == 12:
        text, verses = get_bible_text(ot)
        verse_quote = get_one_verse(verses)
        body = f"{text}\n\n🌟 Highlight: {verse_quote}"
        send_email(f"12PM: Old Testament Reading – {ot}", body)

    elif hour == 18:
        text, verses = get_bible_text(nt)
        verse_quote = get_one_verse(verses)
        body = f"{text}\n\n🌟 Highlight: {verse_quote}"
        send_email(f"6PM: New Testament Reading – {nt}", body)

if __name__ == "__main__":
    run_schedule()

