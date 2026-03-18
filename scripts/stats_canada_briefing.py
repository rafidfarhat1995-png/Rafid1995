import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ============================================================
# CONFIGURATION - Fill these in before running
# ============================================================
GMAIL_ADDRESS = "your_email@gmail.com"       # Your Gmail address
GMAIL_APP_PASSWORD = "your_app_password"     # Gmail App Password (not your real password)
SEND_TO = "your_email@gmail.com"             # Where to send the briefing

# ============================================================
# STATS CANADA DATA
# We are pulling 3 key indicators:
# - CPI (Inflation)
# - Unemployment Rate
# - GDP
# ============================================================

INDICATORS = {
    "Inflation (CPI)": "18-10-0004-01",
    "Unemployment Rate": "14-10-0287-01",
    "GDP (Monthly)": "36-10-0434-01",
}

def fetch_stats_canada(table_id):
    """
    Fetches the latest data from a Stats Canada table.
    table_id = the Stats Canada table number
    """
    # Remove dashes to format the table ID correctly for the API
    clean_id = table_id.replace("-", "")

    url = f"https://www150.statcan.gc.ca/t1/tbl1/en/dtbl!downloadTbl/csvDownload/{clean_id}-eng.zip"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return f"Data fetched successfully for table {table_id}"
        else:
            return f"Could not fetch data for table {table_id}"
    except Exception as e:
        return f"Error: {str(e)}"


def fetch_key_stats():
    """
    Pulls the latest key economic stats from Stats Canada API.
    Returns a formatted summary string.
    """
    summary = []

    for indicator_name, table_id in INDICATORS.items():
        result = fetch_stats_canada(table_id)
        summary.append(f"- {indicator_name}: {result}")

    return "\n".join(summary)


def build_email_body():
    """
    Builds the full email content you will receive every morning.
    """
    today = datetime.today().strftime("%A, %B %d, %Y")

    stats_summary = fetch_key_stats()

    body = f"""
Good morning Rafid!

Here is your Stats Canada briefing for {today}.

==========================================
KEY ECONOMIC INDICATORS
==========================================
{stats_summary}

==========================================
NEWSLETTER IDEAS FOR TODAY
==========================================
Based on today's data, consider writing about:
- How current inflation affects everyday Canadians
- What the unemployment rate means for job seekers
- How GDP trends impact personal finance decisions

==========================================
Data sourced from Statistics Canada
https://www.statcan.gc.ca
==========================================
    """
    return body


def send_email(body):
    """
    Sends the briefing to your Gmail.
    Uses Gmail's SMTP server.
    """
    # Set up the email
    msg = MIMEMultipart()
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = SEND_TO
    msg["Subject"] = f"Stats Canada Morning Briefing - {datetime.today().strftime('%B %d, %Y')}"

    msg.attach(MIMEText(body, "plain"))

    # Connect to Gmail and send
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Encrypts the connection
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, SEND_TO, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")


# ============================================================
# MAIN - This is what runs when you execute the script
# ============================================================
if __name__ == "__main__":
    print("Fetching Stats Canada data...")
    email_body = build_email_body()

    print("Sending email...")
    send_email(email_body)

    print("Done! Check your inbox.")
