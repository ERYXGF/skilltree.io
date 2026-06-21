"""Pydantic request/response models."""

import re
from typing import List

from pydantic import BaseModel, Field, field_validator

_GITHUB_REPO_PATTERN = re.compile(
    r"^https?://(?:www\.)?github\.com/[\w.-]+/[\w.-]+/?(?:\.git)?(?:/.*)?$",
    re.IGNORECASE,
)


class AnalyzeRequest(BaseModel):
    repo_url: str = Field(..., description="Public GitHub repository URL")

    @field_validator("repo_url")
    @classmethod
    def validate_repo_url(cls, value: str) -> str:
        value = value.strip()
        if not _GITHUB_REPO_PATTERN.match(value):
            raise ValueError("repo_url must be a valid GitHub repository URL")
        return value


class ResumeBullet(BaseModel):
    text: str = Field(..., min_length=1)
    category: str = Field(default="general")


class SkillScore(BaseModel):
    skill: str = Field(..., min_length=1)
    score: int = Field(..., ge=0, le=100)
    rationale: str = Field(default="")


class AnalyzeResponse(BaseModel):
    repo_url: str
    resume_markdown: str
    bullets: List[ResumeBullet]
    skills: List[SkillScore]
