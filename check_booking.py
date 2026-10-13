import os
import requests
from playwright.sync_api import sync_playwright

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

TARGET_URL = (
    "https://www.bhagyalaxmitravels.com/search?"
    "mode=oneway&fromCity=14|Pune&toCity=197|Jalgaon&"
    "departDate=05-11-2026&returnDate=05-11-2026&"
    "hop=direct&pf=mobile&src=h&"
)

# Negative indicator phrases from the screen
NEGATIVE_INDICATORS = [
    "there were no results found",
    "request waitlist priority booking",
    "plese modify your search"
]

def send_alert(message: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram secrets not configured. Alert skipped.")
        return

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
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Emulate mobile screen matching the mobile site parameter
        context = browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            viewport={"width": 390, "height": 844}
        )
        page = context.new_page()

        print(f"Loading {TARGET_URL}...")
        page.goto(TARGET_URL, wait_until="networkidle", timeout=45000)

        # Wait an extra 3 seconds for client-side JavaScript templates to bind
        page.wait_for_timeout(3000)

        # Extract all rendered text from the document body
        rendered_text = page.inner_text("body").lower()
        browser.close()

        # Check if ANY negative indicator exists in the rendered text
        is_negative_found = any(phrase in rendered_text for phrase in NEGATIVE_INDICATORS)

        if is_negative_found:
            print("Status: Negative scenario detected ('no results found' / 'waitlist'). Booking is NOT open yet.")
        else:
            print("Status: Negative scenario NOT detected. Booking is OPEN!")
            alert_msg = (
                "🚨 <b>Bhagyalaxmi Travels Alert!</b>\n\n"
                "Booking is <b>OPEN</b> for Pune ➡️ Jalgaon on 05-Nov-2026!\n\n"
                f"<a href='{TARGET_URL}'>Book Now on Bhagyalaxmi Travels</a>"
            )
            send_alert(alert_msg)

if __name__ == "__main__":
    check_availability()
    
