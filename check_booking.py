import os
import requests

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

TARGET_URL = (
    "https://www.bhagyalaxmitravels.com/search?"
    "mode=oneway&fromCity=14|Pune&toCity=197|Jalgaon&"
    "departDate=05-11-2026&returnDate=05-11-2026&"
    "hop=direct&pf=mobile&src=h&"
)

NO_RESULT_TEXT = "There were no results found"

def send_alert(message: str):
    telegram_api = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        res = requests.post(telegram_api, json=payload, timeout=10)
        res.raise_for_status()
        print("Telegram alert sent successfully.")
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

def check_availability():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.bhagyalaxmitravels.com/",
    }

    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=20)
        response.raise_for_status()
        page_html = response.text

        # If the failure text is NOT found, bookings have opened
        if NO_RESULT_TEXT not in page_html:
            alert_msg = (
                "🚨 <b>Bhagyalaxmi Travels Alert!</b>\n\n"
                "Booking is <b>OPEN</b> for Pune ➡️ Jalgaon on 05-Nov-2026!\n\n"
                f"<a href='{TARGET_URL}'>Book Now on Bhagyalaxmi Travels</a>"
            )
            print("Status: Booking OPEN! Sending alert...")
            send_alert(alert_msg)
        else:
            print("Status: 'There were no results found' present. Booking not open yet.")

    except requests.RequestException as e:
        print(f"HTTP request error: {e}")

if __name__ == "__main__":
    check_availability()
