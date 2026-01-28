# Copilot / Agent Instructions — Capture Kit

Purpose: enable AI coding agents to be immediately productive in this repo.

- **Big picture:** `collector.py` is the orchestration point for social-data ingestion and analysis. It prefers official data exports (ZIPs) parsed by platform-specific parsers (`parse_twitter_export`, `parse_linkedin_export`, `parse_instagram_export`, `parse_facebook_export`) and then runs `extract_social_style` (see `style_extractor.py`) to produce a cross-platform style summary. `direct_scraper.py` contains an optional Playwright-based scraper that the code only uses when Playwright is available. See `social-media-collection-spec.md` for expected export formats.

- **Quick commands / workflows**
  - Run test suite and smoke checks: `python run_tests.py` (project expects a `test_data.sample_data` module).
  - CLI collection (from `collector.py`):
    - Export analysis: `python collector.py export --twitter /path/to/twitter.zip --output out.json`
    - Scrape (requires Playwright): run inside an async runner or use the `collector.py scrape` CLI to launch the browser.

- **Conventions & patterns to follow**
  - Parsers return dicts (NOT exceptions) with keys like `platform`, `profile`, `posts`, `total_posts`. If something goes wrong, return `{"error": "message"}` and let callers check `if "error" in result:` (see `collector.add_export`).
  - The analysis pipeline expects posts to include at least `content` and (when available) `timestamp`. `style_extractor.extract_social_style` expects a list of platform objects: each item has `platform`, `posts`, and optional `profile`.
  - Optional deps are feature-gated: code uses try/except ImportError and SCRAPER_AVAILABLE to decide whether to enable scraping. If you add new optional integrations, follow the same pattern.
  - Keep imports package-local (relative imports are used across modules). If you move files, add `__init__.py` and update imports accordingly (BUILD_PLAN.md documents a proposed package structure: `extractors/`, `social/`, `test_data/`).

- **Files to consult for examples**
  - `collector.py` — orchestration, CLI, `add_export`, `add_exports_from_folder`, `scrape`, `analyze`.
  - `direct_scraper.py` — transparent Playwright scraper (headless default commented; shows how login is detected and scraping flows are structured).
  - `style_extractor.py` — canonical analysis functions and expected post schema (emoji, hashtag, vocabulary, tone, posting patterns).
  - `social-media-collection-spec.md` — authoritative examples of export formats and parser implementations (e.g., Twitter export parsing logic).
  - `sample_data.py` and `run_tests.py` — test expectations and sample persona; `run_tests.py` imports helper functions from `test_data.sample_data` (note: currently `sample_data.py` is top-level; tests expect it under `test_data/` and to export helper getters).

- **When editing or adding parsers**
  - Mirror the shape of `parse_twitter_export` shown in `social-media-collection-spec.md`: return top-level `platform`, `profile`, `posts` (list of dicts with `content`/`timestamp`), and `total_posts`.
  - Include defensive handling for ZIPs and malformed JSON; return `{"error": "..."}` on parse failures.

- **Testing & iteration**
  - After changes, run `python run_tests.py`. If tests fail due to import errors, check package layout and `sys.path` manipulation in `run_tests.py` (it inserts parent directories).
  - For scraper work, ensure Playwright is installed and `playwright install chromium` has been run locally; otherwise code paths will return an `error` dict.

- **Non-goals / constraints**
  - This project intentionally prefers user-provided exports over scraping. Keep that preference: add scraping only as opt-in and transparent (user-visible browser), as implemented in `direct_scraper.py`.

If anything in this file is missing or unclear, tell me which areas you'd like expanded (examples, data shapes, or test-fixes) and I will update the instructions.
