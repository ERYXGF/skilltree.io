"""Phase 6 — Pydantic schema validation tests."""

import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.models.schemas import (  # noqa: E402
    AnalyzeRequest,
    AnalyzeResponse,
    ResumeBullet,
    SkillScore,
)


def test_analyze_request_accepts_valid_url():
    req = AnalyzeRequest(repo_url="https://github.com/octocat/Hello-World")
    assert req.repo_url == "https://github.com/octocat/Hello-World"


def test_analyze_request_rejects_invalid_url():
    with pytest.raises(ValidationError):
        AnalyzeRequest(repo_url="https://gitlab.com/user/repo")


def test_analyze_response_round_trip():
    payload = AnalyzeResponse(
        repo_url="https://github.com/octocat/Hello-World",
        resume_markdown="# Resume",
        bullets=[ResumeBullet(text="Built a REST API", category="backend")],
        skills=[SkillScore(skill="Python", score=75, rationale="Used in 12 files")],
    )
    data = payload.model_dump()
    restored = AnalyzeResponse.model_validate(data)
    assert restored == payload


def test_skill_score_rejects_out_of_range():
    with pytest.raises(ValidationError):
        SkillScore(skill="Python", score=101)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
