import os
import requests
import difflib
from bs4 import BeautifulSoup
import openai
import smtplib
from email.mime.text import MIMEText

# ---------- CONFIGURATION ----------

# List of websites to monitor. For each, define a name, URL, and a file to store the previous content.
websites = [
    {
        "name": "Shotgun Players",
        "url": "https://shotgunplayers.org/get-involved/audition/",
        "old_content_file": "old_content_auditions_shotgun.txt"
    },
    {
        "name": "Marin Shakespeare Company",
        "url": "https://www.marinshakespeare.org/audition-information/",
        "old_content_file": "old_content_auditions_marinshakes.txt"
    },
    {
        "name": "Hillbarn Theatre",
        "url": "https://www.hillbarntheatre.org/work-with-us/",
        "old_content_file": "old_content_auditions_hillbarn.txt"
    },
     {
        "name": "Center Repertory Theatre",
        "url": "https://www.centerrep.org/get-involved/audition",
        "old_content_file": "old_content_auditions_centerrep.txt"
    },
    {
        "name": "Theatreworks",
        "url": "https://theatreworks.org/work-with-us/auditions/",
        "old_content_file": "old_content_auditions_theatreworks.txt"
    },
    {
        "name": "SF Playhouse",
        "url": "https://www.sfplayhouse.org/sfph/get-involved/casting/",
        "old_content_file": "old_content_auditions_sfplayhouse.txt"
    },
    {
        "name": "Aurora",
        "url": "https://www.auroratheatre.org/auditions-submissions",
        "old_content_file": "old_content_auditions_aurora.txt"
    }
]

# Set your OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
# For testing locally, you might uncomment and set your API key directly:
# openai.api_key = "your_api_key_here"

# Email configuration pulled from environment variables
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", 587))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")

# ---------- FUNCTION DEFINITIONS ----------

def fetch_page_content(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    content = soup.get_text(separator="\n", strip=True)
    return content

def load_old_content(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def save_new_content(filepath, content):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

def generate_diff(old, new):
    diff = difflib.unified_diff(
        old.splitlines(),
        new.splitlines(),
        fromfile="old_content",
        tofile="new_content",
        lineterm=""
    )
    return "\n".join(diff)

def get_summary_from_chatgpt(diff_text):
    prompt = f"Summarize the following changes to an auditions page:\n\n{diff_text}\n\nSummary:"
  
