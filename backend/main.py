"""FastAPI application entry point and routes."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.agent.orchestrator import run_orchestrator
from backend.agent.tools import detect_stack_handler, score_skills_handler
from backend.config import get_settings
from backend.core.chart_data import to_plotly_payload
from backend.core.github_client import GitHubClient
from backend.core.logging_config import get_logger
from backend.core.repo_analyzer import (
    build_repo_summary,
    language_breakdown,
    parse_js_deps,
    parse_python_deps,
)
from backend.core.resume_builder import clean_bullets, verify_grounded, to_markdown
from backend.core.url_parser import parse_github_url
from backend.models.database import cache_get, cache_set
from backend.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    ResumeBullet,
    RepoSummary,
    SkillScore,
)

logger = get_logger("main")
settings = get_settings()

DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


def create_app() -> FastAPI:
    app = FastAPI(title="SkillTree.io", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=DEFAULT_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/analyze/ingest", response_model=RepoSummary)
    async def analyze_ingest(request: AnalyzeRequest) -> RepoSummary:
        """Ingest and analyze a GitHub repository, with caching."""
        repo_url = request.repo_url

        # Step 1: Check cache
        cached = cache_get(settings.db_path, repo_url)
        if cached is not None:
            logger.info("Cache hit for %s", repo_url)
            return RepoSummary(**cached)

        logger.info("Cache miss for %s, fetching from GitHub", repo_url)

        # Step 2: Parse URL
        owner, repo = parse_github_url(repo_url)

        # Step 3: Instantiate GitHub client and gather data
        client = GitHubClient(settings.github_token)
        meta = client.get_repo_meta(owner, repo)
        meta["repo_url"] = repo_url  # Add repo_url to meta

        tree = client.get_file_tree(owner, repo)

        # Step 4: Gather manifests and parse dependencies
        deps: dict[str, list[str]] = {}

        # Try to fetch Python dependencies
        for manifest in ["requirements.txt", "pyproject.toml"]:
            if manifest in tree:
                try:
                    content = client.get_file(owner, repo, manifest)
                    python_deps = parse_python_deps(content)
                    if python_deps:
                        deps["python"] = python_deps
                        break
                except Exception as e:
                    logger.warning("Failed to parse %s: %s", manifest, e)

        # Try to fetch JavaScript dependencies
        if "package.json" in tree:
            try:
                content = client.get_file(owner, repo, "package.json")
                js_deps = parse_js_deps(content)
                if js_deps:
                    deps["javascript"] = js_deps
            except Exception as e:
                logger.warning("Failed to parse package.json: %s", e)

        # Step 5: Calculate language breakdown
        langs = language_breakdown(tree)

        # Step 6: Build summary, cache it, and return
        summary_dict = build_repo_summary(meta, tree, deps, langs)
        cache_set(settings.db_path, repo_url, summary_dict)

        logger.info("Successfully analyzed and cached %s", repo_url)
        return RepoSummary(**summary_dict)

    @app.post("/analyze", response_model=AnalyzeResponse)
    async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
        """
        Full analysis endpoint: Ingest repository, run AI agent, generate resume.

        This endpoint orchestrates the complete pipeline:
        1. Check cache for existing analysis
        2. If uncached: Parse URL -> Fetch metadata & tree -> Analyze dependencies
        3. Build repo summary -> Run orchestrator -> Clean bullets -> Verify grounded
        4. Cache and return structured AnalyzeResponse

        Implements proper error handling to convert external failures into clean HTTP responses.
        """
        repo_url = request.repo_url

        try:
            # Step 1: Check cache
            cached = cache_get(settings.db_path, repo_url)
            if cached is not None:
                logger.info("Cache hit for %s (full analysis)", repo_url)
                return AnalyzeResponse(**cached)

            logger.info("Cache miss for %s, running full analysis pipeline", repo_url)

            # Step 2: Parse URL
            try:
                owner, repo = parse_github_url(repo_url)
            except ValueError as e:
                logger.warning("Invalid GitHub URL: %s", repo_url)
                raise HTTPException(status_code=400, detail=f"Invalid GitHub URL: {str(e)}")

            # Step 3: Fetch metadata and tree
            try:
                client = GitHubClient(settings.github_token)
                meta = client.get_repo_meta(owner, repo)
                meta["repo_url"] = repo_url
                tree = client.get_file_tree(owner, repo)
            except Exception as e:
                logger.error("GitHub API error for %s/%s: %s", owner, repo, e)
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to fetch repository data: {str(e)}"
                )

            # Step 4: Analyze dependencies
            deps: dict[str, list[str]] = {}

            # Try to fetch Python dependencies
            for manifest in ["requirements.txt", "pyproject.toml"]:
                if manifest in tree:
                    try:
                        content = client.get_file(owner, repo, manifest)
                        python_deps = parse_python_deps(content)
                        if python_deps:
                            deps["python"] = python_deps
                            break
                    except Exception as e:
                        logger.warning("Failed to parse %s: %s", manifest, e)

            # Try to fetch JavaScript dependencies
            if "package.json" in tree:
                try:
                    content = client.get_file(owner, repo, "package.json")
                    js_deps = parse_js_deps(content)
                    if js_deps:
                        deps["javascript"] = js_deps
                except Exception as e:
                    logger.warning("Failed to parse package.json: %s", e)

            # Step 5: Calculate language breakdown
            langs = language_breakdown(tree)

            # Step 6: Build repo summary
            summary_dict = build_repo_summary(meta, tree, deps, langs)

            # Step 7: Run orchestrator loop to generate resume bullets
            try:
                raw_bullets = run_orchestrator(summary_dict)
            except Exception as e:
                logger.error("Orchestrator failed for %s: %s", repo_url, e)
                raise HTTPException(
                    status_code=500,
                    detail=f"AI agent orchestration failed: {str(e)}"
                )

            # Step 8: Clean bullets
            cleaned_bullet_texts = clean_bullets(raw_bullets)

            # Step 9: Detect stack for verification
            detected_techs = detect_stack_handler(summary_dict)

            # Step 10: Verify bullets are grounded in detected technologies
            verified_bullet_texts = verify_grounded(cleaned_bullet_texts, detected_techs)

            # Step 11: Convert to ResumeBullet objects
            bullets = [
                ResumeBullet(text=text, category="general")
                for text in verified_bullet_texts
            ]

            # Step 12: Generate skill scores using production proficiency_scorer
            scored_skills = score_skills_handler(detected_techs, summary_dict)

            # Convert to SkillScore objects for response schema
            skills = [
                SkillScore(skill=s["technology"], score=s["score"], rationale=s["rationale"])
                for s in scored_skills
            ]

            # Step 13: Build professional resume markdown using to_markdown
            resume_markdown = to_markdown(
                bullets=verified_bullet_texts,
                skills=scored_skills,
                meta=meta
            )

            # Step 14: Generate chart data payload for frontend
            chart_data = to_plotly_payload(scored_skills, max_skills=10)

            # Step 15: Build response payload
            response_data = {
                "repo_url": repo_url,
                "resume_markdown": resume_markdown,
                "bullets": [bullet.model_dump() for bullet in bullets],
                "skills": [skill.model_dump() for skill in skills],
                "chart_data": chart_data,
            }

            # Step 16: Cache the result
            cache_set(settings.db_path, repo_url, response_data)

            logger.info("Successfully completed full analysis for %s", repo_url)
            return AnalyzeResponse(**response_data)

        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            # Catch any unexpected errors and return clean 500 response
            logger.exception("Unexpected error analyzing %s", repo_url)
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(exc)},
        )

    return app


app = create_app()
