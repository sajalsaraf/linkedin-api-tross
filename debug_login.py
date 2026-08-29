"""Debug login flow: python3 debug_login.py"""
import re
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

email = os.environ["LINKEDIN_EMAIL"]
password = os.environ["LINKEDIN_PASSWORD"]

client = httpx.Client(
    headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    },
    follow_redirects=True,
    timeout=30,
)

print("Step 1: Loading login page...")
resp = client.get("https://www.linkedin.com/login")
print(f"  Status: {resp.status_code}, URL: {resp.url}")

login_csrf = client.cookies.get("JSESSIONID", "").strip('"')
print(f"  CSRF token (JSESSIONID): {login_csrf[:20] if login_csrf else 'NOT FOUND'}")
print(f"  Cookies set: {list(dict(client.cookies).keys())}")

print("\nStep 2: Submitting credentials...")
resp2 = client.post(
    "https://www.linkedin.com/checkpoint/lg/login-submit",
    data={
        "session_key": email,
        "session_password": password,
        "loginCsrfParam": login_csrf,
        "trk": "guest_homepage-basic_nav-header-signin",
    },
    headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://www.linkedin.com/login",
    },
)
print(f"  Final URL: {resp2.url}")
print(f"  Status: {resp2.status_code}")

li_at = client.cookies.get("li_at")
print(f"\nli_at present: {bool(li_at)}")
if li_at:
    print("✅ Login successful!")
else:
    print("❌ Login failed")
    print(f"  Page title hint: {resp2.text[resp2.text.find('<title>'):resp2.text.find('</title>')+8]}")
