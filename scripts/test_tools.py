"""
Test suite for backend/agent/tools.py

Validates the detect_stack tool schema and handler function.
Tests that the handler accurately detects technologies from repository
summaries without hallucinating.
"""

import sys
from pathlib import Path

# Add backend to path BEFORE importing
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from agent.tools import (
    DETECT_STACK_TOOL,
    MAP_TO_JOBS_TOOL,
    SCORE_SKILLS_TOOL,
    TOOL_SCHEMAS,
    TOOLS,
    detect_stack_handler,
    map_to_jobs_handler,
    score_skills_handler,
    dispatch,
    handle_tool_use,
    load_tech_taxonomy,
)

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def test_tech_taxonomy_loads():
    """Test that tech_taxonomy.json can be loaded."""
    taxonomy = load_tech_taxonomy()
    assert isinstance(taxonomy, dict), "Taxonomy must be a dictionary"
    assert len(taxonomy) > 0, "Taxonomy must not be empty"
    assert "fastapi" in taxonomy, "Taxonomy must contain 'fastapi'"
    assert "react" in taxonomy, "Taxonomy must contain 'react'"
    print("✓ Tech taxonomy loads successfully")


def test_detect_stack_tool_schema_exists():
    """Test that DETECT_STACK_TOOL schema is properly defined."""
    assert DETECT_STACK_TOOL is not None, "DETECT_STACK_TOOL must be defined"
    assert isinstance(DETECT_STACK_TOOL, dict), "DETECT_STACK_TOOL must be a dict"
    assert "name" in DETECT_STACK_TOOL, "Tool must have a name"
    assert "description" in DETECT_STACK_TOOL, "Tool must have a description"
    assert "input_schema" in DETECT_STACK_TOOL, "Tool must have an input_schema"
    print("✓ DETECT_STACK_TOOL schema exists")


def test_detect_stack_tool_name():
    """Test that the tool has the correct name."""
    assert DETECT_STACK_TOOL["name"] == "detect_stack", "Tool name must be 'detect_stack'"
    print("✓ Tool has correct name")


def test_detect_stack_tool_schema_structure():
    """Test that the tool schema follows Anthropic's format."""
    schema = DETECT_STACK_TOOL["input_schema"]
    assert schema["type"] == "object", "Input schema must be of type 'object'"
    assert "properties" in schema, "Input schema must have properties"
    assert "repo_summary" in schema["properties"], "Input schema must have 'repo_summary' property"
    print("✓ Tool schema follows Anthropic format")


def test_tools_list_contains_detect_stack():
    """Test that TOOLS list includes the detect_stack tool."""
    assert isinstance(TOOLS, list), "TOOLS must be a list"
    assert len(TOOLS) > 0, "TOOLS must not be empty"
    assert DETECT_STACK_TOOL in TOOLS, "TOOLS must contain DETECT_STACK_TOOL"
    print("✓ TOOLS list contains detect_stack")


def test_detect_stack_handler_with_python_deps():
    """Test detect_stack_handler with Python dependencies."""
    mock_summary = {
        "dependencies": {
            "python": ["fastapi", "pytest", "sqlalchemy"]
        }
    }

    result = detect_stack_handler(mock_summary)

    assert isinstance(result, list), "Handler must return a list"
    assert "fastapi" in result, "Must detect 'fastapi'"
    assert "pytest" in result, "Must detect 'pytest'"
    assert "sqlalchemy" in result, "Must detect 'sqlalchemy'"
    print("✓ Handler detects Python dependencies")


def test_detect_stack_handler_with_javascript_deps():
    """Test detect_stack_handler with JavaScript dependencies."""
    mock_summary = {
        "dependencies": {
            "javascript": ["react", "vite", "tailwind"]
        }
    }

    result = detect_stack_handler(mock_summary)

    assert isinstance(result, list), "Handler must return a list"
    assert "react" in result, "Must detect 'react'"
    assert "vite" in result, "Must detect 'vite'"
    assert "tailwind" in result, "Must detect 'tailwind'"
    print("✓ Handler detects JavaScript dependencies")


def test_detect_stack_handler_with_mixed_deps():
    """Test detect_stack_handler with mixed Python and JavaScript dependencies."""
    mock_summary = {
        "dependencies": {
            "python": ["fastapi", "pandas"],
            "javascript": ["react", "redux"]
        }
    }

    result = detect_stack_handler(mock_summary)

    assert isinstance(result, list), "Handler must return a list"
    assert "fastapi" in result, "Must detect 'fastapi'"
    assert "pandas" in result, "Must detect 'pandas'"
    assert "react" in result, "Must detect 'react'"
    assert "redux" in result, "Must detect 'redux'"
    assert len(result) == 4, "Must detect exactly 4 technologies"
    print("✓ Handler detects mixed dependencies")


def test_detect_stack_handler_filters_unknown_packages():
    """Test that handler only returns technologies in tech_taxonomy."""
    mock_summary = {
        "dependencies": {
            "python": ["fastapi", "unknown-package-xyz", "pytest"],
            "javascript": ["react", "fake-library-123"]
        }
    }

    result = detect_stack_handler(mock_summary)

    assert "fastapi" in result, "Must detect known 'fastapi'"
    assert "pytest" in result, "Must detect known 'pytest'"
    assert "react" in result, "Must detect known 'react'"
    assert "unknown-package-xyz" not in result, "Must NOT include unknown packages"
    assert "fake-library-123" not in result, "Must NOT include fake packages"
    print("✓ Handler filters out unknown packages (no hallucinations)")


def test_detect_stack_handler_case_insensitive():
    """Test that handler matches packages case-insensitively."""
    mock_summary = {
        "dependencies": {
            "python": ["FastAPI", "PYTEST"],
            "javascript": ["React", "VITE"]
        }
    }

    result = detect_stack_handler(mock_summary)

    # Should match regardless of case
    assert len(result) > 0, "Must detect technologies despite case differences"
    print("✓ Handler performs case-insensitive matching")


def test_detect_stack_handler_returns_sorted_list():
    """Test that handler returns a sorted list for consistency."""
    mock_summary = {
        "dependencies": {
            "python": ["pytest", "fastapi", "pandas"]
        }
    }

    result = detect_stack_handler(mock_summary)

    assert result == sorted(result), "Result must be sorted alphabetically"
    print("✓ Handler returns sorted list")


def test_detect_stack_handler_empty_dependencies():
    """Test handler with empty dependencies."""
    mock_summary = {
        "dependencies": {}
    }

    result = detect_stack_handler(mock_summary)

    assert isinstance(result, list), "Handler must return a list"
    assert len(result) == 0, "Must return empty list for empty dependencies"
    print("✓ Handler handles empty dependencies")


def test_handle_tool_use_routes_correctly():
    """Test that handle_tool_use routes to the correct handler."""
    mock_summary = {
        "dependencies": {
            "python": ["fastapi"]
        }
    }

    result = handle_tool_use("detect_stack", {"repo_summary": mock_summary})

    assert isinstance(result, list), "Must return a list"
    assert "fastapi" in result, "Must detect 'fastapi'"
    print("✓ handle_tool_use routes correctly")


def test_handle_tool_use_raises_on_unknown_tool():
    """Test that handle_tool_use raises error for unknown tools."""
    try:
        handle_tool_use("unknown_tool", {})
        assert False, "Should raise ValueError for unknown tool"
    except ValueError as e:
        assert "Unknown tool" in str(e), "Error message must mention 'Unknown tool'"
        print("✓ handle_tool_use raises error for unknown tools")


# ============================================================================
# Phase 26: map_to_jobs Tests
# ============================================================================

def test_map_to_jobs_tool_schema_exists():
    """Test that MAP_TO_JOBS_TOOL schema is properly defined."""
    assert MAP_TO_JOBS_TOOL is not None, "MAP_TO_JOBS_TOOL must be defined"
    assert isinstance(MAP_TO_JOBS_TOOL, dict), "MAP_TO_JOBS_TOOL must be a dict"
    assert MAP_TO_JOBS_TOOL["name"] == "map_to_jobs", "Tool name must be 'map_to_jobs'"
    assert "description" in MAP_TO_JOBS_TOOL, "Tool must have a description"
    assert "input_schema" in MAP_TO_JOBS_TOOL, "Tool must have an input_schema"
    print("✓ MAP_TO_JOBS_TOOL schema exists")


def test_map_to_jobs_handler_basic():
    """Test map_to_jobs_handler with basic technologies."""
    technologies = ["fastapi", "scikit-learn"]
    result = map_to_jobs_handler(technologies)

    assert isinstance(result, list), "Handler must return a list"
    assert "Backend Engineer" in result, "Must map fastapi to Backend Engineer"
    assert "Data Scientist" in result, "Must map scikit-learn to Data Scientist"
    assert len(result) == 2, "Must return exactly 2 job families"
    print("✓ map_to_jobs_handler maps technologies correctly")


def test_map_to_jobs_handler_deduplication():
    """Test that map_to_jobs_handler deduplicates job families."""
    # fastapi, pytest, and sqlalchemy all map to Backend Engineer
    technologies = ["fastapi", "pytest", "sqlalchemy"]
    result = map_to_jobs_handler(technologies)

    assert isinstance(result, list), "Handler must return a list"
    assert "Backend Engineer" in result, "Must include Backend Engineer"
    assert result.count("Backend Engineer") == 1, "Must deduplicate Backend Engineer"
    assert len(result) == 1, "Must return exactly 1 deduplicated job family"
    print("✓ map_to_jobs_handler deduplicates job families")


def test_map_to_jobs_handler_mixed_families():
    """Test map_to_jobs_handler with technologies from different job families."""
    technologies = ["react", "fastapi", "docker", "pandas"]
    result = map_to_jobs_handler(technologies)

    assert isinstance(result, list), "Handler must return a list"
    assert "Frontend Engineer" in result, "Must include Frontend Engineer (react)"
    assert "Backend Engineer" in result, "Must include Backend Engineer (fastapi)"
    assert "DevOps Engineer" in result, "Must include DevOps Engineer (docker)"
    assert "Data Scientist" in result, "Must include Data Scientist (pandas)"
    assert len(result) == 4, "Must return exactly 4 job families"
    print("✓ map_to_jobs_handler handles mixed job families")


def test_map_to_jobs_handler_sorted():
    """Test that map_to_jobs_handler returns sorted results."""
    technologies = ["docker", "react", "fastapi"]
    result = map_to_jobs_handler(technologies)

    assert result == sorted(result), "Result must be sorted alphabetically"
    print("✓ map_to_jobs_handler returns sorted list")


def test_map_to_jobs_handler_empty_list():
    """Test map_to_jobs_handler with empty technology list."""
    result = map_to_jobs_handler([])

    assert isinstance(result, list), "Handler must return a list"
    assert len(result) == 0, "Must return empty list for empty input"
    print("✓ map_to_jobs_handler handles empty list")


def test_map_to_jobs_handler_unknown_tech():
    """Test that map_to_jobs_handler ignores unknown technologies."""
    technologies = ["fastapi", "unknown-tech-xyz", "react"]
    result = map_to_jobs_handler(technologies)

    assert "Backend Engineer" in result, "Must include Backend Engineer (fastapi)"
    assert "Frontend Engineer" in result, "Must include Frontend Engineer (react)"
    assert len(result) == 2, "Must ignore unknown technologies"
    print("✓ map_to_jobs_handler ignores unknown technologies")


# ============================================================================
# Phase 27: score_skills Tests
# ============================================================================

def test_score_skills_tool_schema_exists():
    """Test that SCORE_SKILLS_TOOL schema is properly defined."""
    assert SCORE_SKILLS_TOOL is not None, "SCORE_SKILLS_TOOL must be defined"
    assert isinstance(SCORE_SKILLS_TOOL, dict), "SCORE_SKILLS_TOOL must be a dict"
    assert SCORE_SKILLS_TOOL["name"] == "score_skills", "Tool name must be 'score_skills'"
    assert "description" in SCORE_SKILLS_TOOL, "Tool must have a description"
    assert "input_schema" in SCORE_SKILLS_TOOL, "Tool must have an input_schema"
    print("✓ SCORE_SKILLS_TOOL schema exists")


def test_score_skills_handler_basic():
    """Test score_skills_handler with basic input."""
    technologies = ["fastapi", "react"]
    repo_summary = {
        "dependencies": {
            "python": ["fastapi"],
            "javascript": ["react"]
        },
        "languages": {"Python": 60, "JavaScript": 40},
        "file_count": 75
    }

    result = score_skills_handler(technologies, repo_summary)

    assert isinstance(result, list), "Handler must return a list"
    assert len(result) == 2, "Must return 2 scored skills"

    for skill in result:
        assert "technology" in skill, "Each skill must have 'technology'"
        assert "score" in skill, "Each skill must have 'score'"
        assert "rationale" in skill, "Each skill must have 'rationale'"
    print("✓ score_skills_handler returns properly structured results")


def test_score_skills_handler_score_boundaries():
    """Test that scores are within 0-100 boundaries."""
    technologies = ["fastapi", "react", "pandas", "docker"]
    repo_summary = {
        "dependencies": {
            "python": ["fastapi", "pandas"],
            "javascript": ["react"]
        },
        "languages": {"Python": 70, "JavaScript": 30},
        "file_count": 150
    }

    result = score_skills_handler(technologies, repo_summary)

    for skill in result:
        score = skill["score"]
        assert isinstance(score, int), "Score must be an integer"
        assert 0 <= score <= 100, f"Score must be between 0-100, got {score}"
    print("✓ score_skills_handler enforces 0-100 score boundaries")


def test_score_skills_handler_sorted_descending():
    """Test that results are sorted by score (highest first)."""
    technologies = ["fastapi", "react", "pandas"]
    repo_summary = {
        "dependencies": {
            "python": ["fastapi", "pandas"],
            "javascript": ["react"]
        },
        "languages": {"Python": 80, "JavaScript": 20},
        "file_count": 100
    }

    result = score_skills_handler(technologies, repo_summary)

    # Verify descending order
    scores = [skill["score"] for skill in result]
    assert scores == sorted(scores, reverse=True), "Results must be sorted by score (highest first)"
    print("✓ score_skills_handler returns results in descending score order")


def test_score_skills_handler_rationale_present():
    """Test that each skill has a non-empty rationale."""
    technologies = ["fastapi"]
    repo_summary = {
        "dependencies": {"python": ["fastapi"]},
        "languages": {"Python": 100},
        "file_count": 50
    }

    result = score_skills_handler(technologies, repo_summary)

    assert len(result) > 0, "Must return at least one result"
    for skill in result:
        rationale = skill["rationale"]
        assert isinstance(rationale, str), "Rationale must be a string"
        assert len(rationale) > 0, "Rationale must not be empty"
    print("✓ score_skills_handler provides rationale for each skill")


def test_score_skills_handler_empty_technologies():
    """Test score_skills_handler with empty technology list."""
    result = score_skills_handler([], {"dependencies": {}})

    assert isinstance(result, list), "Handler must return a list"
    assert len(result) == 0, "Must return empty list for empty input"
    print("✓ score_skills_handler handles empty technology list")


# ============================================================================
# Phase 28: Tool Dispatch Registry Tests
# ============================================================================

def test_tool_schemas_registry_exists():
    """Test that TOOL_SCHEMAS registry is properly defined."""
    assert TOOL_SCHEMAS is not None, "TOOL_SCHEMAS must be defined"
    assert isinstance(TOOL_SCHEMAS, list), "TOOL_SCHEMAS must be a list"
    assert len(TOOL_SCHEMAS) >= 3, "TOOL_SCHEMAS must contain at least 3 tools"
    print("✓ TOOL_SCHEMAS registry exists")


def test_tool_schemas_contains_all_tools():
    """Test that TOOL_SCHEMAS contains all three tools."""
    assert DETECT_STACK_TOOL in TOOL_SCHEMAS, "TOOL_SCHEMAS must contain DETECT_STACK_TOOL"
    assert MAP_TO_JOBS_TOOL in TOOL_SCHEMAS, "TOOL_SCHEMAS must contain MAP_TO_JOBS_TOOL"
    assert SCORE_SKILLS_TOOL in TOOL_SCHEMAS, "TOOL_SCHEMAS must contain SCORE_SKILLS_TOOL"
    print("✓ TOOL_SCHEMAS contains all three tools")


def test_dispatch_detect_stack():
    """Test dispatch function with detect_stack tool."""
    mock_summary = {
        "dependencies": {
            "python": ["fastapi", "pytest"]
        }
    }

    result = dispatch("detect_stack", {"repo_summary": mock_summary})

    assert isinstance(result, list), "Must return a list"
    assert "fastapi" in result, "Must detect fastapi"
    assert "pytest" in result, "Must detect pytest"
    print("✓ dispatch successfully executes detect_stack")


def test_dispatch_map_to_jobs():
    """Test dispatch function with map_to_jobs tool."""
    result = dispatch("map_to_jobs", {"technologies": ["fastapi", "scikit-learn"]})

    assert isinstance(result, list), "Must return a list"
    assert "Backend Engineer" in result, "Must include Backend Engineer"
    assert "Data Scientist" in result, "Must include Data Scientist"
    print("✓ dispatch successfully executes map_to_jobs")


def test_dispatch_score_skills():
    """Test dispatch function with score_skills tool."""
    technologies = ["fastapi"]
    repo_summary = {
        "dependencies": {"python": ["fastapi"]},
        "languages": {"Python": 100},
        "file_count": 50
    }

    result = dispatch("score_skills", {
        "technologies": technologies,
        "repo_summary": repo_summary
    })

    assert isinstance(result, list), "Must return a list"
    assert len(result) > 0, "Must return at least one scored skill"
    assert "score" in result[0], "Result must contain score"
    print("✓ dispatch successfully executes score_skills")


def test_dispatch_unknown_tool_raises_error():
    """Test that dispatch raises ValueError for unknown tool names."""
    try:
        dispatch("fake_tool_xyz", {})
        assert False, "Should raise ValueError for unknown tool"
    except ValueError as e:
        assert "Unknown tool" in str(e), "Error message must mention 'Unknown tool'"
        print("✓ dispatch raises ValueError for unknown tools")


def test_dispatch_all_tools_integration():
    """Integration test: dispatch all three tools in sequence."""
    # Step 1: Detect stack
    repo_summary = {
        "dependencies": {
            "python": ["fastapi", "scikit-learn"],
            "javascript": ["react"]
        },
        "languages": {"Python": 70, "JavaScript": 30},
        "file_count": 100
    }

    technologies = dispatch("detect_stack", {"repo_summary": repo_summary})
    assert len(technologies) > 0, "Must detect technologies"

    # Step 2: Map to jobs
    job_families = dispatch("map_to_jobs", {"technologies": technologies})
    assert len(job_families) > 0, "Must map to job families"

    # Step 3: Score skills
    scored_skills = dispatch("score_skills", {
        "technologies": technologies,
        "repo_summary": repo_summary
    })
    assert len(scored_skills) > 0, "Must score skills"

    print("✓ dispatch successfully executes all tools in sequence")


def main():
    """Run all tool tests."""
    print("\n" + "="*60)
    print("Testing Phases 25-28: Complete Tool Suite")
    print("="*60 + "\n")

    tests = [
        # Phase 25: detect_stack
        test_tech_taxonomy_loads,
        test_detect_stack_tool_schema_exists,
        test_detect_stack_tool_name,
        test_detect_stack_tool_schema_structure,
        test_tools_list_contains_detect_stack,
        test_detect_stack_handler_with_python_deps,
        test_detect_stack_handler_with_javascript_deps,
        test_detect_stack_handler_with_mixed_deps,
        test_detect_stack_handler_filters_unknown_packages,
        test_detect_stack_handler_case_insensitive,
        test_detect_stack_handler_returns_sorted_list,
        test_detect_stack_handler_empty_dependencies,
        test_handle_tool_use_routes_correctly,
        test_handle_tool_use_raises_on_unknown_tool,

        # Phase 26: map_to_jobs
        test_map_to_jobs_tool_schema_exists,
        test_map_to_jobs_handler_basic,
        test_map_to_jobs_handler_deduplication,
        test_map_to_jobs_handler_mixed_families,
        test_map_to_jobs_handler_sorted,
        test_map_to_jobs_handler_empty_list,
        test_map_to_jobs_handler_unknown_tech,

        # Phase 27: score_skills
        test_score_skills_tool_schema_exists,
        test_score_skills_handler_basic,
        test_score_skills_handler_score_boundaries,
        test_score_skills_handler_sorted_descending,
        test_score_skills_handler_rationale_present,
        test_score_skills_handler_empty_technologies,

        # Phase 28: dispatch registry
        test_tool_schemas_registry_exists,
        test_tool_schemas_contains_all_tools,
        test_dispatch_detect_stack,
        test_dispatch_map_to_jobs,
        test_dispatch_score_skills,
        test_dispatch_unknown_tool_raises_error,
        test_dispatch_all_tools_integration,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1

    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
