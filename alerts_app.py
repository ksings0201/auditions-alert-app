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
        "name": "Theatreworks",
        "url": "https://theatreworks.org/work-with-us/auditions/",
        "old_content_file": "old_content_auditions_theatreworks.txt"
    }
]

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
# For testing, you can also uncomment and set your API key directly:
# openai.api_key = "your_api_key_here"

# Email configuration (update with your details)
EMAIL_SMTP_SERVER = "smtp.gmail.com"
EMAIL_SMTP_PORT = 587
EMAIL_USERNAME = "therealmisterclip@gmail.com"  # Your Gmail address
EMAIL_PASSWORD = "chiu omsz uwfb juzg"           # Your Gmail app password
EMAIL_FROM = "therealmisterclip@gmail.com"       # Sender address (usually your Gmail)
EMAIL_TO = "ksings0201@gmail.com"                # Recipient address

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
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant summarizing webpage changes."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        temperature=0.5
    )
    summary = response.choices[0].message['content'].strip()
    return summary

def send_email(subject, body):
    # Create a MIMEText message with UTF-8 encoding
    msg = MIMEText(body, _charset="utf-8")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

def check_website(website):
    name = website["name"]
    url = website["url"]
    old_content_file = website["old_content_file"]

    new_content = fetch_page_content(url)
    old_content = load_old_content(old_content_file)

    # First run: save content if no previous data exists
    if not old_content:
        print(f"No previous content for {name}. Saving current content.")
        save_new_content(old_content_file, new_content)
        return

    # If no changes, do nothing
    if new_content == old_content:
        print(f"No changes detected for {name}.")
        return

    # Generate diff and summary
    diff_text = generate_diff(old_content, new_content)
    summary = get_summary_from_chatgpt(diff_text)

    # Send email notification
    email_subject = f"{name} Auditions Page Update Detected"
    email_body = f"Changes detected for {name}:\n\nSummary:\n{summary}\n\nFull diff:\n{diff_text}"
    send_email(email_subject, email_body)
    print(f"Change detected for {name} and email notification sent.")

    # Update stored content
    save_new_content(old_content_file, new_content)

def main():
    for website in websites:
        check_website(website)

if __name__ == "__main__":
    main()
