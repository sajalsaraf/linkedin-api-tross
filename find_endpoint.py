"""Test which LinkedIn endpoints work with current cookies."""
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

li_at = os.environ["LINKEDIN_LI_AT"]
jsessionid = os.environ["LINKEDIN_JSESSIONID"].strip('"')

client = httpx.Client(
    headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/vnd.linkedin.normalized+json+2.1",
        "csrf-token": jsessionid,
        "x-restli-protocol-version": "2.0.0",
        "x-li-lang": "en_US",
    },
    cookies={"li_at": li_at, "JSESSIONID": f'"{jsessionid}"'},
    follow_redirects=False,
    timeout=10,
)

import sys
USERNAME = sys.argv[1] if len(sys.argv) > 1 else "sajal-saraf-222486224"
BASE = "https://www.linkedin.com/voyager/api"

endpoints = [
    f"/identity/dash/profiles?q=memberIdentity&memberIdentity={USERNAME}",
    f"/identity/dash/profiles?q=memberIdentity&memberIdentity={USERNAME}&decorationId=com.linkedin.voyager.dash.deco.identity.profile.FullProfileWithEntities-91",
    f"/identity/profiles/{USERNAME}/profileView",
    f"/identity/profiles/{USERNAME}",
]

for ep in endpoints:
    r = client.get(f"{BASE}{ep}")
    print(f"[{r.status_code}] {ep[:80]}")
    if r.status_code == 200:
        print(f"  -> keys: {list(r.json().keys())}")
    elif r.status_code in (301, 302, 307):
        print(f"  -> redirect: {r.headers.get('location', '')[:80]}")
    elif r.status_code != 200:
        print(f"  -> body: {r.text[:100]}")
