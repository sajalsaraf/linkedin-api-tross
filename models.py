from pydantic import BaseModel
from typing import Optional


class Experience(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    started_on: Optional[str] = None
    ended_on: Optional[str] = None
    description: Optional[str] = None


class Education(BaseModel):
    school: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    started_on: Optional[str] = None
    ended_on: Optional[str] = None


class Skill(BaseModel):
    name: str


class Certification(BaseModel):
    name: Optional[str] = None
    authority: Optional[str] = None
    started_on: Optional[str] = None
    ended_on: Optional[str] = None
    url: Optional[str] = None


class Language(BaseModel):
    name: Optional[str] = None
    proficiency: Optional[str] = None


class ProfileResponse(BaseModel):
    vanity_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    headline: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    profile_picture_url: Optional[str] = None
    background_image_url: Optional[str] = None
    experience: list[Experience] = []
    education: list[Education] = []
    skills: list[Skill] = []
    certifications: list[Certification] = []
    languages: list[Language] = []
