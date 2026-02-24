# Friday Morning "Hi" SMS Automation

Sends a text message "hi" every Friday at 7:00 AM using Twilio.

## Setup

### 1. Install dependencies
```bash
pip install twilio python-dotenv
```

### 2. Create your .env file
```bash
cp .env.example .env
```
Then fill in your credentials in `.env`:
- `TWILIO_ACCOUNT_SID` — from your Twilio dashboard
- `TWILIO_AUTH_TOKEN`  — from your Twilio dashboard
- `TWILIO_FROM_NUMBER` — your Twilio phone number (e.g. +12025551234)
- `RECIPIENT_NUMBER`   — the number to send to (e.g. +12025559999)

### 3. Test it manually
```bash
python send_hi.py
```

### 4. Schedule with cron (Linux/Mac)
Open crontab:
```bash
crontab -e
```

Add this line to run every Friday at 7:00 AM:
```
0 7 * * 5 /usr/bin/python3 /home/user/Rafid1995/send_hi.py >> /home/user/Rafid1995/sms.log 2>&1
```

> **Note:** Replace `/usr/bin/python3` with the output of `which python3`
> and update the path to `send_hi.py` if needed.

## How it works
- `send_hi.py` — loads credentials from `.env` and sends the SMS via Twilio API
- Cron runs it every Friday (`5` = Friday) at `7:00 AM`
- Output is logged to `sms.log`
