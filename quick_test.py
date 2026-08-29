"""Quick raw test — bypasses server entirely."""
import httpx
import os
import json
from dotenv import load_dotenv

load_dotenv()

raw = os.environ["LINKEDIN_COOKIES"]
exclude = {"__cf_bm", "__cfruid", "fptctx2", "dfpfpt", "_pxvid", "g_state"}
cookies = {}
for part in raw.split(";"):
    part = part.strip()
    if "=" in part:
        k, _, v = part.partition("=")
        k = k.strip()
        if k not in exclude:
            cookies[k] = v.strip()

jsessionid = cookies.get("JSESSIONID", "").strip('"')
li_at = cookies.get("li_at", "")

print(f"li_at: {li_at[:20]}...")
print(f"jsessionid: {jsessionid[:20]}...")
print(f"cookies sent: {list(cookies.keys())}")

# Test 1: minimal cookies
print("\n--- Test 1: li_at + JSESSIONID only ---")
r = httpx.get(
    "https://www.linkedin.com/voyager/api/identity/dash/profiles",
    params={"q": "memberIdentity", "memberIdentity": "sajal-saraf-222486224",
            "decorationId": "com.linkedin.voyager.dash.deco.identity.profile.FullProfileWithEntities-91"},
    headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/vnd.linkedin.normalized+json+2.1",
        "csrf-token": jsessionid,
        "x-restli-protocol-version": "2.0.0",
        "Referer": "https://www.linkedin.com/",
    },
    cookies={"li_at": li_at, "JSESSIONID": f'"{jsessionid}"'},
    follow_redirects=False,
    timeout=10,
)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    print("✅ Works with minimal cookies!")
    data = r.json()
    included = data.get("included", [])
    profile = next((i for i in included if i.get("$type") == "com.linkedin.voyager.dash.identity.profile.Profile"), None)
    if profile:
        print(f"Name: {profile.get('firstName')} {profile.get('lastName')}")

# Test 2: all cookies
print("\n--- Test 2: all cookies ---")
r2 = httpx.get(
    "https://www.linkedin.com/voyager/api/identity/dash/profiles",
    params={"q": "memberIdentity", "memberIdentity": "sajal-saraf-222486224",
            "decorationId": "com.linkedin.voyager.dash.deco.identity.profile.FullProfileWithEntities-91"},
    headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/vnd.linkedin.normalized+json+2.1",
        "csrf-token": jsessionid,
        "x-restli-protocol-version": "2.0.0",
        "Referer": "https://www.linkedin.com/",
    },
    cookies=cookies,
    follow_redirects=False,
    timeout=10,
)
print(f"Status: {r2.status_code}")
if r2.status_code == 200:
    print("✅ Works with all cookies!")
