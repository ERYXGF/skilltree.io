"""FastAPI application entry point and routes."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import get_settings
from backend.core.github_client import GitHubClient
from backend.core.logging_config import get_logger
from backend.core.repo_analyzer import (
    build_repo_summary,
    language_breakdown,
    parse_js_deps,
    parse_python_deps,
)
from backend.core.url_parser import parse_github_url
from backend.models.database import cache_get, cache_set
from backend.models.schemas import AnalyzeRequest, RepoSummary

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

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(exc)},
        )

    return app


app = create_app()
