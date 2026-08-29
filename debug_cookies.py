"""Run this to verify your cookies are working: python3 debug_cookies.py"""
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

li_at = os.environ["LINKEDIN_LI_AT"]
jsessionid = os.environ["LINKEDIN_JSESSIONID"].strip('"')

print(f"li_at starts with: {li_at[:20]}...")
print(f"jsessionid starts with: {jsessionid[:20]}...")

resp = httpx.get(
    "https://www.linkedin.com/voyager/api/me",
    headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/vnd.linkedin.normalized+json+2.1",
        "csrf-token": jsessionid,
        "x-restli-protocol-version": "2.0.0",
        "Referer": "https://www.linkedin.com/",
    },
    cookies={"li_at": li_at, "JSESSIONID": f'"{jsessionid}"'},
    follow_redirects=False,
)

print(f"\nStatus: {resp.status_code}")
if resp.status_code in (301, 302, 307):
    print("❌ Cookies invalid — re-copy li_at and JSESSIONID from browser DevTools")
elif resp.status_code == 200:
    print("✅ Cookies valid!")
else:
    print(f"Body: {resp.text[:300]}")
