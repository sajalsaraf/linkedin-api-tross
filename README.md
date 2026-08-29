# LinkedIn Profile API

A REST API that accepts a LinkedIn username and returns structured JSON profile data. Built by reverse-engineering LinkedIn's internal Voyager API — no browser automation, direct HTTP calls only.

## Approach

LinkedIn's own frontend communicates with internal Voyager API endpoints to load profile data. These endpoints return clean structured JSON. This API:

1. Authenticates using your LinkedIn session cookies (`li_at` + `JSESSIONID`)
2. Calls Voyager endpoints directly via HTTP
3. Parses and returns structured JSON

No Selenium. No Playwright. Pure HTTP.

## Setup

### Prerequisites

- Python 3.11+
- A LinkedIn account (session cookies used server-side)

### Installation

```bash
git clone <repo-url>
cd linkedin-api
pip install -r requirements.txt
cp .env.example .env
```

### Getting LinkedIn Cookies

1. Log into LinkedIn in Chrome
2. Open DevTools → Application → Cookies → `www.linkedin.com`
3. Copy the value of `li_at`
4. Copy the value of `JSESSIONID` (without the outer quotes)
5. Add both to `.env`:

```
LINKEDIN_LI_AT=your_li_at_value
LINKEDIN_JSESSIONID=ajax:your_jsessionid_value
```

> **Note:** Keep the LinkedIn tab closed while the API is running. Opening LinkedIn in the browser alongside the API causes LinkedIn to rotate the session cookie, invalidating the API's session.

### Run the server

```bash
uvicorn main:app --reload
```

Server starts at `http://localhost:8000`

---

## Quick Demo (from terminal)

Use the included `test.py` script to start the server, fetch a profile, and shut down — all in one command:

```bash
python3 test.py https://www.linkedin.com/in/sajal-saraf-222486224
```

**Sample output:**

```json
{
  "vanity_id": "sajal-saraf-222486224",
  "first_name": "Sajal",
  "last_name": "Saraf",
  "headline": "Application Developer @Oracle | IIIT Surat'25 | Expert @Codeforces | Full Stack Developer",
  "location": null,
  "summary": null,
  "profile_picture_url": "https://media.licdn.com/dms/image/v2/D4D03AQFUw2L1-09rHg/profile-displayphoto-scale_400_400/B4DZhQZP.tG8Ag-/0/1753695455823?e=1789603200&v=beta&t=mPy7iVw9yuR6Ht25qhuute8RhCqfXxhX2HY3rzl_wAI",
  "background_image_url": null,
  "experience": [
    {
      "title": "Application Developer-1",
      "company": "Oracle",
      "location": "Gandhinagar, Gujarat, India",
      "started_on": "2025-07",
      "ended_on": null,
      "description": null
    },
    {
      "title": "Back End Developer",
      "company": "Wicktronix",
      "location": "Vadodara, Gujarat, India",
      "started_on": "2024-12",
      "ended_on": "2025-05",
      "description": null
    }
  ],
  "education": [
    {
      "school": "Indian Institute of Information Technology Surat",
      "degree": "Bachelor of Technology - BTech",
      "field_of_study": "Electrical and Electronics Engineering",
      "started_on": "2021-12",
      "ended_on": "2025-05"
    }
  ],
  "skills": [
    {"name": "JavaScript"}, {"name": "Go (Programming Language)"},
    {"name": "GraphQL"}, {"name": "SQL"}, {"name": "C++"}, {"name": "Java"}
  ],
  "certifications": [],
  "languages": []
}
```

---

## API Reference

### `GET /profile`

Returns structured profile data for a LinkedIn username.

| Parameter  | Type   | Required | Description              |
|------------|--------|----------|--------------------------|
| `url` | string | Yes      | Full LinkedIn profile URL |

**Request:**
```
GET /profile?url=https://www.linkedin.com/in/sajal-saraf-222486224
```

**Response schema:**
```json
{
  "vanity_id": "string",
  "first_name": "string | null",
  "last_name": "string | null",
  "headline": "string | null",
  "location": "string | null",
  "summary": "string | null",
  "profile_picture_url": "string | null",
  "background_image_url": "string | null",
  "experience": [
    {
      "title": "string | null",
      "company": "string | null",
      "location": "string | null",
      "started_on": "YYYY-MM | null",
      "ended_on": "YYYY-MM | null",
      "description": "string | null"
    }
  ],
  "education": [
    {
      "school": "string | null",
      "degree": "string | null",
      "field_of_study": "string | null",
      "started_on": "string | null",
      "ended_on": "string | null"
    }
  ],
  "skills": [{ "name": "string" }],
  "certifications": [
    {
      "name": "string | null",
      "authority": "string | null",
      "started_on": "string | null",
      "ended_on": "string | null",
      "url": "string | null"
    }
  ],
  "languages": [
    {
      "name": "string | null",
      "proficiency": "string | null"
    }
  ]
}
```

### `GET /health`

```json
{"status": "ok"}
```

### Interactive docs

```
http://localhost:8000/docs
```

---

## Deployment (Render)

1. Push this repo to GitHub (public)
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Set environment variables in the Render dashboard:
   - `LINKEDIN_LI_AT` — your LinkedIn `li_at` cookie value
   - `LINKEDIN_JSESSIONID` — your `JSESSIONID` cookie value
5. Render auto-detects the Dockerfile and deploys

---

## Known Limitations

- **Session expiry:** LinkedIn session cookies typically last days to weeks. Refresh `LINKEDIN_LI_AT` in the env vars when requests start failing with 401.
- **Rate limiting:** LinkedIn rate-limits Voyager API calls. High request volume may result in 429 errors — add delays between requests.
- **Private profiles:** Only returns data visible to the authenticated account.
- **ToS:** Direct Voyager API usage violates LinkedIn's Terms of Service. This project is for educational/demonstration purposes only.
