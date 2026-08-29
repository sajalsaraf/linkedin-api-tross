import httpx
import os
from typing import Optional
from models import (
    ProfileResponse, Experience, Education, Skill, Certification, Language
)


VOYAGER_BASE = "https://www.linkedin.com/voyager/api"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/vnd.linkedin.normalized+json+2.1",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.linkedin.com/",
    "Origin": "https://www.linkedin.com",
    "x-li-lang": "en_US",
    "x-restli-protocol-version": "2.0.0",
    "x-li-track": '{"clientVersion":"1.13.9064","osName":"web","timezoneOffset":5.5,"deviceFormFactor":"DESKTOP","mpName":"voyager-web"}',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
}


def _fmt_date(date_obj) -> Optional[str]:
    if not date_obj or not isinstance(date_obj, dict):
        return None
    year = date_obj.get("year")
    month = date_obj.get("month")
    if year and month:
        return f"{year}-{month:02d}"
    if year:
        return str(year)
    return None


class LinkedInClient:
    def __init__(self):
        li_at = os.environ["LINKEDIN_LI_AT"]
        jsessionid = os.environ["LINKEDIN_JSESSIONID"].strip('"')
        cookies = {"li_at": li_at, "JSESSIONID": f'"{jsessionid}"'}

        self.client = httpx.Client(
            headers={**HEADERS, "csrf-token": jsessionid},
            cookies=cookies,
            follow_redirects=True,
            timeout=30,
        )
        self._log_session_status()

    def _log_session_status(self):
        try:
            resp = self.client.get(
                "https://www.linkedin.com/voyager/api/me",
                follow_redirects=False,
            )
            if resp.status_code == 200:
                print("✅ LinkedIn session valid")
            else:
                print(f"⚠️  LinkedIn session may be expired (status {resp.status_code}) — update LINKEDIN_COOKIES in .env if requests fail")
        except Exception as e:
            print(f"⚠️  Could not verify session: {e}")

    def _get(self, path: str, params: dict = None) -> dict:
        resp = self.client.get(f"{VOYAGER_BASE}{path}", params=params)

        if "login" in str(resp.url) or "authwall" in str(resp.url):
            raise RuntimeError(
                "LinkedIn session expired — refresh LINKEDIN_LI_AT and "
                "LINKEDIN_JSESSIONID env vars and restart the server"
            )

        # Keep csrf-token in sync if LinkedIn rotated JSESSIONID
        new_jsessionid = self.client.cookies.get("JSESSIONID", "").strip('"')
        if new_jsessionid:
            self.client.headers["csrf-token"] = new_jsessionid

        resp.raise_for_status()
        return resp.json()

    def get_profile(self, username: str) -> ProfileResponse:
        vanity_id = username.strip().lower()

        data = self._get(
            "/identity/dash/profiles",
            params={
                "q": "memberIdentity",
                "memberIdentity": vanity_id,
                "decorationId": "com.linkedin.voyager.dash.deco.identity.profile.FullProfileWithEntities-91",
            },
        )

        included = data.get("included", [])
        profile = next(
            (
                i for i in included
                if i.get("$type") == "com.linkedin.voyager.dash.identity.profile.Profile"
            ),
            None,
        )
        if not profile:
            raise ValueError(f"Profile not found: {vanity_id}")

        return ProfileResponse(
            vanity_id=vanity_id,
            **self._parse_basic(profile, included),
            experience=self._parse_positions(included),
            education=self._parse_educations(included),
            skills=self._parse_skills(included),
            certifications=self._parse_certifications(included),
            languages=self._parse_languages(included),
        )

    def _parse_basic(self, profile: dict, included: list) -> dict:
        picture_url = None
        bg_url = None

        pic = profile.get("profilePicture") or {}
        pic_ref = pic.get("displayImageReference") or {}
        pic_root = pic_ref.get("vectorImage") or pic.get("com.linkedin.common.VectorImage") or {}
        pic_artifacts = pic_root.get("artifacts") or []
        pic_base = pic_root.get("rootUrl") or ""
        if pic_artifacts and pic_base:
            picture_url = pic_base + (pic_artifacts[-1].get("fileIdentifyingUrlPathSegment") or "")

        bg = profile.get("backgroundImage") or {}
        bg_ref = bg.get("displayImageReference") or {}
        bg_root = bg_ref.get("vectorImage") or bg.get("com.linkedin.common.VectorImage") or {}
        bg_artifacts = bg_root.get("artifacts") or []
        bg_base = bg_root.get("rootUrl") or ""
        if bg_artifacts and bg_base:
            bg_url = bg_base + (bg_artifacts[-1].get("fileIdentifyingUrlPathSegment") or "")

        location = profile.get("locationName") or profile.get("geoLocationName")

        return {
            "first_name": profile.get("firstName"),
            "last_name": profile.get("lastName"),
            "headline": profile.get("headline"),
            "location": location,
            "summary": profile.get("summary"),
            "profile_picture_url": picture_url,
            "background_image_url": bg_url,
        }

    def _parse_positions(self, included: list) -> list[Experience]:
        results = []
        for item in included:
            if item.get("$type") == "com.linkedin.voyager.dash.identity.profile.Position":
                date_range = item.get("dateRange") or {}
                results.append(Experience(
                    title=item.get("title"),
                    company=item.get("companyName"),
                    location=item.get("locationName"),
                    started_on=_fmt_date(date_range.get("start")),
                    ended_on=_fmt_date(date_range.get("end")),
                    description=item.get("description"),
                ))
        return results

    def _parse_educations(self, included: list) -> list[Education]:
        results = []
        for item in included:
            if item.get("$type") == "com.linkedin.voyager.dash.identity.profile.Education":
                date_range = item.get("dateRange") or {}
                results.append(Education(
                    school=item.get("schoolName"),
                    degree=item.get("degreeName"),
                    field_of_study=item.get("fieldOfStudy"),
                    started_on=_fmt_date(date_range.get("start")),
                    ended_on=_fmt_date(date_range.get("end")),
                ))
        return results

    def _parse_skills(self, included: list) -> list[Skill]:
        results = []
        for item in included:
            if item.get("$type") == "com.linkedin.voyager.dash.identity.profile.Skill":
                name = item.get("name")
                if name:
                    results.append(Skill(name=name))
        return results

    def _parse_certifications(self, included: list) -> list[Certification]:
        results = []
        for item in included:
            if item.get("$type") == "com.linkedin.voyager.dash.identity.profile.Certification":
                date_range = item.get("dateRange") or {}
                results.append(Certification(
                    name=item.get("name"),
                    authority=item.get("authority"),
                    started_on=_fmt_date(date_range.get("start")),
                    ended_on=_fmt_date(date_range.get("end")),
                    url=item.get("url"),
                ))
        return results

    def _parse_languages(self, included: list) -> list[Language]:
        results = []
        for item in included:
            if item.get("$type") == "com.linkedin.voyager.dash.identity.profile.Language":
                results.append(Language(
                    name=item.get("name"),
                    proficiency=item.get("proficiency"),
                ))
        return results
