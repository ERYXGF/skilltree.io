"""Test suite for Phase 35 - Chart data shaper.

Validates that the chart data transformation:
1. Produces valid Plotly-compatible payloads
2. Sorts skills by score (highest first)
3. Limits to max_skills to avoid clutter
4. Includes all required keys for react-plotly.js
5. Handles edge cases gracefully
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from backend.core.chart_data import to_plotly_payload, to_simple_chart_data

# Use ASCII-compatible symbols for Windows compatibility
CHECK = "[PASS]"
CROSS = "[FAIL]"


def test_plotly_payload_structure():
    """Test that to_plotly_payload returns correct structure."""
    print("Testing Plotly payload structure...")

    skills = [
        {"technology": "fastapi", "score": 85, "rationale": "FastAPI - in dependencies (+30)"},
        {"technology": "react", "score": 72, "rationale": "React - in dependencies (+30)"},
        {"technology": "pytest", "score": 60, "rationale": "Pytest - detected"}
    ]

    result = to_plotly_payload(skills)

    # Verify top-level structure
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "data" in result, "Should have 'data' key"
    assert "layout" in result, "Should have 'layout' key"

    # Verify data array
    assert isinstance(result["data"], list), "data should be a list"
    assert len(result["data"]) > 0, "data should not be empty"

    # Verify first data trace
    trace = result["data"][0]
    assert trace["type"] == "bar", "Should be a bar chart"
    assert trace["orientation"] == "h", "Should be horizontal orientation"
    assert "x" in trace, "Should have x values (scores)"
    assert "y" in trace, "Should have y values (technologies)"
    assert "hovertext" in trace, "Should have hovertext (rationales)"

    # Verify layout
    assert isinstance(result["layout"], dict), "layout should be a dictionary"
    assert "title" in result["layout"], "Should have title"
    assert "xaxis" in result["layout"], "Should have xaxis config"
    assert "yaxis" in result["layout"], "Should have yaxis config"

    print(f"  {CHECK} Valid Plotly structure")
    print(f"  {CHECK} All required keys present")


def test_plotly_payload_sorting():
    """Test that skills are sorted by score (highest first)."""
    print("\nTesting skill sorting...")

    skills = [
        {"technology": "pytest", "score": 60, "rationale": "Pytest - detected"},
        {"technology": "fastapi", "score": 85, "rationale": "FastAPI - in dependencies"},
        {"technology": "react", "score": 72, "rationale": "React - in dependencies"}
    ]

    result = to_plotly_payload(skills)
    trace = result["data"][0]

    # Extract scores (should be in descending order after reversal for horizontal bar)
    scores = trace["x"]
    technologies = trace["y"]

    # Since we reverse for horizontal bars, highest should be at the end
    # But the important thing is they're sorted
    assert len(scores) == 3, f"Expected 3 scores, got {len(scores)}"

    # Verify the data is sorted (check original order before reversal)
    # The highest score should appear at the top of the chart (last in reversed array)
    assert scores[-1] == 85, f"Highest score should be 85, got {scores[-1]}"
    assert technologies[-1] == "Fastapi", f"Highest tech should be Fastapi, got {technologies[-1]}"

    print(f"  {CHECK} Skills sorted by score")
    print(f"  {CHECK} Highest score (85) at top position")


def test_plotly_payload_max_skills():
    """Test that max_skills parameter limits the output."""
    print("\nTesting max_skills limit...")

    # Create 15 skills
    skills = [
        {"technology": f"tech{i}", "score": 100 - i, "rationale": f"Tech {i}"}
        for i in range(15)
    ]

    # Limit to 10
    result = to_plotly_payload(skills, max_skills=10)
    trace = result["data"][0]

    assert len(trace["x"]) == 10, f"Expected 10 skills, got {len(trace['x'])}"
    assert len(trace["y"]) == 10, f"Expected 10 technologies, got {len(trace['y'])}"
    assert len(trace["hovertext"]) == 10, f"Expected 10 rationales, got {len(trace['hovertext'])}"

    # Verify we got the top 10 (scores 100 down to 91)
    scores = trace["x"]
    # After reversal, highest scores are at the end
    assert max(scores) == 100, "Should include highest score (100)"
    assert min(scores) == 91, "Should include 10th highest score (91)"

    print(f"  {CHECK} Limited to max_skills=10")
    print(f"  {CHECK} Top 10 skills selected")


def test_plotly_payload_data_arrays():
    """Test that x, y, and hovertext arrays are properly populated."""
    print("\nTesting data arrays...")

    skills = [
        {"technology": "fastapi", "score": 85, "rationale": "FastAPI - in dependencies (+30)"},
        {"technology": "react", "score": 72, "rationale": "React - in dependencies (+30)"}
    ]

    result = to_plotly_payload(skills)
    trace = result["data"][0]

    # Verify arrays have same length
    assert len(trace["x"]) == len(trace["y"]) == len(trace["hovertext"]), \
        "x, y, and hovertext should have same length"

    # Verify data types
    assert all(isinstance(score, int) for score in trace["x"]), "Scores should be integers"
    assert all(isinstance(tech, str) for tech in trace["y"]), "Technologies should be strings"
    assert all(isinstance(text, str) for text in trace["hovertext"]), "Hovertext should be strings"

    # Verify capitalization
    assert "Fastapi" in trace["y"] or "React" in trace["y"], "Technologies should be capitalized"

    # Verify rationales are included
    hovertext_combined = " ".join(trace["hovertext"])
    assert "dependencies" in hovertext_combined, "Rationales should be in hovertext"

    print(f"  {CHECK} Arrays properly populated")
    print(f"  {CHECK} Data types correct")
    print(f"  {CHECK} Technologies capitalized")


def test_plotly_payload_empty_input():
    """Test handling of empty skills array."""
    print("\nTesting empty input...")

    result = to_plotly_payload([])

    # Should still return valid structure
    assert isinstance(result, dict), "Should return dictionary"
    assert "data" in result, "Should have data key"
    assert "layout" in result, "Should have layout key"

    trace = result["data"][0]
    assert trace["type"] == "bar", "Should still be bar chart"
    assert trace["orientation"] == "h", "Should still be horizontal"
    assert len(trace["x"]) == 0, "x should be empty"
    assert len(trace["y"]) == 0, "y should be empty"
    assert len(trace["hovertext"]) == 0, "hovertext should be empty"

    print(f"  {CHECK} Handles empty input gracefully")
    print(f"  {CHECK} Returns valid structure")


def test_plotly_payload_layout_config():
    """Test that layout configuration is properly set."""
    print("\nTesting layout configuration...")

    skills = [
        {"technology": "python", "score": 90, "rationale": "Python - dominant language"}
    ]

    result = to_plotly_payload(skills)
    layout = result["layout"]

    # Verify title
    assert "title" in layout, "Should have title"
    assert "text" in layout["title"], "Title should have text"
    assert "Proficiency" in layout["title"]["text"], "Title should mention proficiency"

    # Verify xaxis
    assert "xaxis" in layout, "Should have xaxis"
    assert "title" in layout["xaxis"], "xaxis should have title"
    assert "range" in layout["xaxis"], "xaxis should have range"
    assert layout["xaxis"]["range"][1] >= 100, "xaxis range should accommodate scores up to 100"

    # Verify yaxis
    assert "yaxis" in layout, "Should have yaxis"

    # Verify margin
    assert "margin" in layout, "Should have margin"
    assert "height" in layout, "Should have height"

    print(f"  {CHECK} Layout properly configured")
    print(f"  {CHECK} Axis settings correct")


def test_simple_chart_data_structure():
    """Test to_simple_chart_data returns correct structure."""
    print("\nTesting simple chart data structure...")

    skills = [
        {"technology": "fastapi", "score": 85, "rationale": "FastAPI - in dependencies"},
        {"technology": "react", "score": 72, "rationale": "React - in dependencies"}
    ]

    result = to_simple_chart_data(skills)

    # Verify structure
    assert isinstance(result, dict), "Should return dictionary"
    assert "labels" in result, "Should have labels"
    assert "scores" in result, "Should have scores"
    assert "rationales" in result, "Should have rationales"

    # Verify arrays
    assert isinstance(result["labels"], list), "labels should be a list"
    assert isinstance(result["scores"], list), "scores should be a list"
    assert isinstance(result["rationales"], list), "rationales should be a list"

    # Verify lengths match
    assert len(result["labels"]) == len(result["scores"]) == len(result["rationales"]), \
        "All arrays should have same length"

    print(f"  {CHECK} Simple chart data structure valid")
    print(f"  {CHECK} All required keys present")


def test_simple_chart_data_sorting():
    """Test that simple chart data is sorted by score."""
    print("\nTesting simple chart data sorting...")

    skills = [
        {"technology": "pytest", "score": 60, "rationale": "Pytest"},
        {"technology": "fastapi", "score": 85, "rationale": "FastAPI"},
        {"technology": "react", "score": 72, "rationale": "React"}
    ]

    result = to_simple_chart_data(skills)

    # Verify sorted by score descending
    scores = result["scores"]
    assert scores == sorted(scores, reverse=True), "Scores should be in descending order"
    assert scores[0] == 85, "Highest score should be first"
    assert scores[-1] == 60, "Lowest score should be last"

    # Verify labels match score order
    labels = result["labels"]
    assert labels[0] == "Fastapi", "Highest scoring tech should be first"

    print(f"  {CHECK} Simple data sorted correctly")
    print(f"  {CHECK} Highest score first")


def test_simple_chart_data_empty():
    """Test simple chart data with empty input."""
    print("\nTesting simple chart data with empty input...")

    result = to_simple_chart_data([])

    assert result["labels"] == [], "labels should be empty"
    assert result["scores"] == [], "scores should be empty"
    assert result["rationales"] == [], "rationales should be empty"

    print(f"  {CHECK} Handles empty input")


def test_capitalization():
    """Test that technology names are properly capitalized."""
    print("\nTesting technology name capitalization...")

    skills = [
        {"technology": "fastapi", "score": 85, "rationale": "Test"},
        {"technology": "react", "score": 72, "rationale": "Test"},
        {"technology": "PYTHON", "score": 90, "rationale": "Test"}
    ]

    # Test Plotly payload
    plotly_result = to_plotly_payload(skills)
    technologies = plotly_result["data"][0]["y"]

    assert "Fastapi" in technologies, "fastapi should be capitalized to Fastapi"
    assert "React" in technologies, "react should be capitalized to React"
    assert "Python" in technologies, "PYTHON should be capitalized to Python"

    # Test simple chart data
    simple_result = to_simple_chart_data(skills)
    labels = simple_result["labels"]

    assert "Fastapi" in labels, "fastapi should be capitalized in simple data"
    assert "React" in labels, "react should be capitalized in simple data"
    assert "Python" in labels, "PYTHON should be capitalized in simple data"

    print(f"  {CHECK} Technology names properly capitalized")


def run_all_tests():
    """Run all test functions."""
    print("=" * 60)
    print("Phase 35 - Chart Data Shaper Test Suite")
    print("=" * 60)
    print()

    tests = [
        test_plotly_payload_structure,
        test_plotly_payload_sorting,
        test_plotly_payload_max_skills,
        test_plotly_payload_data_arrays,
        test_plotly_payload_empty_input,
        test_plotly_payload_layout_config,
        test_simple_chart_data_structure,
        test_simple_chart_data_sorting,
        test_simple_chart_data_empty,
        test_capitalization,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
            print()
        except AssertionError as e:
            failed += 1
            print(f"  {CROSS} FAILED: {e}")
            print()
        except Exception as e:
            failed += 1
            print(f"  {CROSS} ERROR: {e}")
            print()

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed == 0:
        print(f"{CHECK} All tests passed!")
        return 0
    else:
        print(f"{CROSS} Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
