# Phase F Implementation Prompt - SkillTree.io Stretch Features

## Overview
Implement **Part F — Fun, visually attractive stretch features (Phases 53–80)** from the skilltree_roadmap.md. These are the "wow" features that make the product stand out in demos. Each phase is independent and can be cherry-picked based on priority and time available.

## Current Project State
- ✅ Parts A-E are complete (Foundation, Repo ingestion, AI agent, Scoring/resume, Frontend)
- ✅ MVP is functional with split-screen resume + chart view
- ✅ Core backend modules exist: [`backend/core/proficiency_scorer.py`](backend/core/proficiency_scorer.py), [`backend/core/resume_builder.py`](backend/core/resume_builder.py), [`backend/agent/tools.py`](backend/agent/tools.py)
- ✅ Frontend components exist: [`frontend/src/components/SkillTreeView.jsx`](frontend/src/components/SkillTreeView.jsx) (currently empty)

## Priority Order for Implementation

### 🔥 HIGH PRIORITY (Maximum Demo Impact)

#### Phase 53 — Animated skill-tree view ⭐ SIGNATURE FEATURE
**Files to create/modify:**
- [`frontend/src/components/SkillTreeView.jsx`](frontend/src/components/SkillTreeView.jsx) - RPG-style tech tree with unlockable nodes
- [`scripts/test_skilltree_data.py`](scripts/test_skilltree_data.py) - Validate DAG structure (no cycles)

**Requirements:**
- Use `react-flow` or `d3` for node/edge visualization
- Skills appear as nodes with connecting lines showing prerequisites
- Visual hierarchy: foundational skills → advanced skills
- Interactive: hover for details, click to highlight path
- Animated unlock effects when skills appear
- Color-code by proficiency level (0-100 score → visual intensity)

**Test criteria:** Node/edge payload is a valid DAG with no cycles

---

#### Phase 55 — "Next skill to unlock" recommender ⭐ ON-THEME
**Files to create/modify:**
- [`backend/core/recommender.py`](backend/core/recommender.py) - NEW FILE
- [`scripts/test_recommender.py`](scripts/test_recommender.py) - NEW FILE

**Requirements:**
- Function: `suggest_next(detected_skills: List[str], target_role: str) -> List[Dict]`
- Gap analysis: compare detected skills vs job family requirements
- Use existing [`backend/data/tech_taxonomy.json`](backend/data/tech_taxonomy.json) and [`backend/data/job_descriptions.json`](backend/data/job_descriptions.json)
- Return: skill name, why it's recommended, estimated learning path
- Prioritize by: relevance to target role, prerequisite completion, market demand

**Test criteria:** Given a stack + target role, returns sensible skill gaps

---

#### Phase 60 — Shareable result link ⭐ VIRALITY
**Files to create/modify:**
- [`backend/main.py`](backend/main.py) - Add `GET /r/{id}` endpoint
- [`backend/models/database.py`](backend/models/database.py) - Add share link storage
- [`frontend/src/components/ExportBar.jsx`](frontend/src/components/ExportBar.jsx) - Add share button
- [`scripts/test_share.py`](scripts/test_share.py) - NEW FILE

**Requirements:**
- Generate short unique ID (8 chars) for each analysis
- Store analysis result with ID in database
- `GET /r/{id}` returns full analysis JSON
- Frontend: "Share" button copies link to clipboard
- Link format: `https://skilltree.io/r/abc12345`
- Optional: Add view counter

**Test criteria:** Save → fetch by ID round-trips correctly

---

### 🎯 MEDIUM PRIORITY (Strong Enhancement)

#### Phase 54 — XP & levels per skill
**Files to modify:**
- [`backend/core/proficiency_scorer.py`](backend/core/proficiency_scorer.py) - Add `to_xp_level(score: int) -> Dict`
- [`scripts/test_proficiency_scorer.py`](scripts/test_proficiency_scorer.py) - Extend tests

**Requirements:**
- Convert 0-100 score to level 1-10 + XP progress bar
- Formula: `level = floor(score / 10) + 1`, `xp_progress = score % 10 * 10`
- Return: `{"level": 7, "xp": 450, "xp_to_next": 100, "progress_pct": 45}`
- Monotonic mapping (higher score = higher level)

**Test criteria:** Monotonic mapping, edge cases (0, 100)

---

#### Phase 56 — Target-role selector
**Files to modify:**
- [`frontend/src/components/RepoInput.jsx`](frontend/src/components/RepoInput.jsx) - Add role dropdown
- [`backend/main.py`](backend/main.py) - Accept optional `target_role` param
- [`scripts/test_api_contract.py`](scripts/test_api_contract.py) - Extend

**Requirements:**
- Dropdown with roles from taxonomy: "Data Scientist", "Frontend Developer", "Backend Engineer", "Full-Stack", "ML Engineer", "DevOps"
- Pass role to `/analyze` endpoint
- Backend uses role to tune recommendations (Phase 55)
- Resume bullets emphasize skills relevant to chosen role

**Test criteria:** Role param flows through API correctly

---

#### Phase 57 — Resume "strength score"
**Files to modify:**
- [`backend/core/resume_builder.py`](backend/core/resume_builder.py) - Add `resume_strength(bullets, skills) -> Dict`
- [`scripts/test_resume_builder.py`](scripts/test_resume_builder.py) - Extend

**Requirements:**
- Score 0-100 based on:
  - Quantified bullets (with numbers) = +10 each
  - Action verb starts = +5 each
  - Skill diversity = +20
  - Bullet length (optimal 60-120 chars) = +5 each
  - Technical depth (advanced skills) = +15
- Return: `{"score": 85, "tips": ["Add more quantified results", "Include 2 more skills"]}`

**Test criteria:** More quantified bullets → higher score

---

#### Phase 59 — Confetti on first analysis
**Files to modify:**
- [`frontend/src/App.jsx`](frontend/src/App.jsx) - Add confetti trigger
- [`frontend/package.json`](frontend/package.json) - Add `canvas-confetti` dependency

**Requirements:**
- Trigger confetti when analysis results first appear
- Use `canvas-confetti` library
- 2-second burst, then stop
- Only on first analysis (not on cached results)

**Test criteria:** Visual confirmation

---

#### Phase 62 — Multi-repo aggregation
**Files to modify:**
- [`backend/core/repo_analyzer.py`](backend/core/repo_analyzer.py) - Add `merge_summaries(summaries: List) -> Dict`
- [`backend/main.py`](backend/main.py) - Accept array of URLs
- [`scripts/test_multi_repo.py`](scripts/test_multi_repo.py) - NEW FILE

**Requirements:**
- Accept 2-3 repo URLs in request
- Merge detected skills (dedupe, sum evidence)
- Aggregate file counts, language percentages
- Combined resume shows breadth across projects

**Test criteria:** Merged skills dedupe and sum correctly

---

### 💡 NICE-TO-HAVE (Polish & Delight)

#### Phase 58 — Animated number counters
**Files to modify:**
- [`frontend/src/components/ProficiencyChart.jsx`](frontend/src/components/ProficiencyChart.jsx)
- [`frontend/package.json`](frontend/package.json) - Add `framer-motion`

**Requirements:**
- Count-up animation for skill scores (0 → final value)
- Smooth easing, 1-second duration
- Stagger animations (each bar animates slightly after previous)

---

#### Phase 64 — Language radar chart
**Files to create:**
- [`frontend/src/components/LanguageRadar.jsx`](frontend/src/components/LanguageRadar.jsx) - NEW FILE

**Requirements:**
- Radar/spider chart showing language proficiency
- Axes: Python, JavaScript, TypeScript, Go, Rust, etc.
- Use Plotly radar chart type
- Toggle between bar chart and radar view

---

#### Phase 66 — Resume templates (3 styles)
**Files to modify:**
- [`backend/core/resume_builder.py`](backend/core/resume_builder.py) - Add `render(style: str)` param

**Requirements:**
- Three styles: "minimal", "modern", "academic"
- Minimal: clean, no icons, monospace headers
- Modern: emojis, bold colors, compact
- Academic: formal, detailed, publications-ready
- Frontend dropdown to select style

---

#### Phase 67 — PDF resume export
**Files to create:**
- [`backend/core/pdf_export.py`](backend/core/pdf_export.py) - NEW FILE
- [`scripts/test_pdf_export.py`](scripts/test_pdf_export.py) - NEW FILE

**Requirements:**
- Convert markdown resume to PDF
- Use `reportlab` or `weasyprint`
- Preserve formatting, proper page breaks
- Download as `resume_[repo_name].pdf`

**Test criteria:** Valid PDF byte stream produced

---

#### Phase 70 — Skill comparison ("vs a junior dev")
**Files to create:**
- [`backend/core/benchmark.py`](backend/core/benchmark.py) - NEW FILE
- [`scripts/test_benchmark.py`](scripts/test_benchmark.py) - NEW FILE

**Requirements:**
- Define baseline scores for: Junior, Mid, Senior, Staff levels
- Compare user's scores to role baseline
- Return: `{"vs_junior": "+45%", "vs_mid": "+12%", "vs_senior": "-23%"}`
- Visual: show user's position on a spectrum

**Test criteria:** Sensible delta vs baseline

---

#### Phase 71 — Achievement badges
**Files to create:**
- [`backend/core/badges.py`](backend/core/badges.py) - NEW FILE
- [`scripts/test_badges.py`](scripts/test_badges.py) - NEW FILE

**Requirements:**
- Award badges based on detected skills:
  - "Full-Stack Warrior" (frontend + backend)
  - "Data Wrangler" (pandas, numpy, SQL)
  - "Cloud Native" (Docker, K8s, AWS/GCP)
  - "Test Champion" (pytest, jest, >80% coverage)
  - "Performance Optimizer" (profiling, caching)
- Display as collectible icons in UI

**Test criteria:** Correct badges for fixture stacks

---

## Implementation Guidelines

### For Each Phase:
1. **Create the test file FIRST** (TDD approach)
2. **Implement the feature** to pass the test
3. **Run the test** to verify: `python scripts/test_[feature].py`
4. **Update [`scripts/run_all.py`](scripts/run_all.py)** to include new test
5. **Verify integration** with existing features

### Code Quality Standards:
- ✅ Type hints on all functions
- ✅ Docstrings with examples
- ✅ Error handling for edge cases
- ✅ Logging for debugging
- ✅ No hardcoded values (use config)
- ✅ Consistent naming conventions

### Testing Requirements:
- ✅ Unit tests for all new functions
- ✅ Mock external dependencies (GitHub, Anthropic)
- ✅ Test happy path + error cases
- ✅ Assert specific values, not just "truthy"
- ✅ Use fixtures for test data

### Frontend Guidelines:
- ✅ Responsive design (mobile-first)
- ✅ Loading states for async operations
- ✅ Error boundaries for graceful failures
- ✅ Accessibility (ARIA labels, keyboard nav)
- ✅ Consistent with existing Tailwind theme

## Suggested Implementation Order

**If you have 4-6 hours:**
1. Phase 53 (Skill tree view) - 2 hrs - SIGNATURE FEATURE
2. Phase 55 (Recommender) - 1 hr - ON-THEME
3. Phase 60 (Shareable links) - 1 hr - VIRALITY
4. Phase 54 (XP/levels) - 30 min - GAMIFICATION
5. Phase 59 (Confetti) - 15 min - DELIGHT
6. Phase 57 (Resume strength) - 45 min - VALUE-ADD

**If you have 2-3 hours:**
1. Phase 53 (Skill tree view) - 1.5 hrs
2. Phase 55 (Recommender) - 45 min
3. Phase 59 (Confetti) - 15 min
4. Phase 54 (XP/levels) - 30 min

**If you have 1 hour:**
1. Phase 54 (XP/levels) - 30 min
2. Phase 59 (Confetti) - 15 min
3. Phase 57 (Resume strength) - 15 min

## Dependencies to Add

Add to [`requirements.txt`](requirements.txt):
```
# Phase F stretch features
reportlab>=4.0.0  # PDF export (Phase 67)
```

Add to [`frontend/package.json`](frontend/package.json):
```json
{
  "dependencies": {
    "react-flow-renderer": "^10.3.17",  // Phase 53
    "canvas-confetti": "^1.9.2",        // Phase 59
    "framer-motion": "^11.0.0",         // Phase 58
    "html-to-image": "^1.11.11"         // Phase 79
  }
}
```

## Success Criteria

After implementing Phase F features, you should have:
- ✅ An interactive, animated skill tree visualization (the product's namesake!)
- ✅ Personalized "next skill to learn" recommendations
- ✅ Shareable result links for virality
- ✅ Gamified XP/level system
- ✅ Delightful micro-interactions (confetti, animations)
- ✅ All new tests passing in [`scripts/run_all.py`](scripts/run_all.py)
- ✅ Features integrated into main UI flow

## Notes

- **Don't break existing functionality** - all Part A-E tests must still pass
- **Each phase is independent** - implement in any order based on priority
- **Test as you go** - don't accumulate technical debt
- **Focus on demo impact** - prioritize features judges will see in 3 minutes
- **The skill tree view (Phase 53) is the signature feature** - it makes the product name make sense

## Questions to Consider

Before starting implementation:
1. Which phases align best with the judging criteria?
2. Do we have time for the full skill tree, or should we do simpler features first?
3. Should we implement the recommender before or after the skill tree?
4. Do we need PDF export, or is markdown sufficient for MVP?

---

**Ready to implement? Start with Phase 53 (skill tree) or Phase 54 (XP/levels) depending on your time budget. Good luck! 🚀**
