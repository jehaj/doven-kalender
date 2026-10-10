# AGENTS.md — Developer and AI Agent Guide

Welcome to **doven-kalender**! This document provides instructions, architectural context, development guidelines, and operational procedures for both automated AI agents and human contributors working on this repository.

---

## 1. Overview and Purpose

`doven-kalender` ("lazy calendar") automates the extraction of event calendars and the generation of announcements and visual calendar graphics for a local youth community (IMU / PU).

### Primary Goals
- **Extract** upcoming calendar events from Google Calendar (via API) or from a Google Docs planning table (exported as an OpenDocument ODT file).
- **Parse & Normalize** tabular and event data using rule-based heuristics and Large Language Models (LLMs) with structured schemas (Pydantic).
- **Enrich** calendar entries with relevant, creative emojis using LLMs.
- **Generate Announcements & Posters** for social media and member communication (Facebook announcements, Typst-rendered calendar graphics).

---

## 2. Architecture & Codebase Structure

The core pipeline follows a clear linear flow:

```
[ Extractor ] ──> [ Parser ] ──> [ Generator / Integrator ] ──> [ Poster / Output ]
```

### Directory Layout

```
.
├── doven_kalender/              # Primary Python package
│   ├── __init__.py              # High-level pipeline orchestration & helpers
│   ├── __main__.py              # Entry point for `python3 -m doven_kalender`
│   ├── extractor/               # Data extraction modules
│   │   ├── __init__.py
│   │   ├── kalender.py          # Google Calendar API event fetcher
│   │   └── pu.py                # ODT document parser extracting table rows to CSV
│   ├── parser/                  # Data transformation and parsing
│   │   ├── __init__.py
│   │   ├── convert_csv_to_json.py # Converts CSV rows into split two-month JSON structure
│   │   ├── get_emojis.py        # LLM-driven emoji assignment for calendar entries
│   │   └── parser.py            # Event parsing abstraction using LLM + Pydantic
│   └── generator/               # Generation layer and LLM abstraction
│       ├── __init__.py
│       ├── generator.py         # Shared GeneralLLM abstraction, Gemini & Mistral clients
│       ├── compile_typst.py     # Script/helper for compiling Typst documents
│       └── poster.py            # Placeholder namespace for posting integrations
├── scripts/
│   ├── __init__.py
│   └── pu_calendar_pipeline.py  # End-to-end CLI pipeline (`pu-pipeline`)
├── extractor/
│   └── information_from_PU.md   # Documentation on PU's Google Docs export format
├── generator/
│   ├── prepare_image.sh         # Image processing script using `vips` (blur & brightness)
│   └── typst_fb_template.typ    # Typst markup template for graphic calendar posters
├── docs/                        # Architecture documentation and D2 diagrams
│   ├── ARCHITECTURE.md          # Architectural notes
│   ├── architecture.d2 / .svg   # High-level system architecture diagram
│   ├── structure.d2 / .svg      # Component structure diagram
│   └── todo.md                  # Development backlog and task tracking
├── tests/                       # Test suite
│   ├── test_convert_csv_to_json.py
│   ├── test_environment.py
│   ├── test_extract_pu.py
│   ├── test_get_emojis.py
│   └── tests.py                 # LLM generation and parser tests
├── environment.py               # Lightweight .env parser and environment accessors
├── pyproject.toml               # Project metadata, dependencies, and CLI script entry points
├── uv.lock                      # uv dependency lockfile
├── Makefile                     # Build targets (compiles D2 diagrams to SVG)
└── README.md                    # User-facing project overview
```

### Key Modules

- **`doven_kalender.generator.generator`**:
  Centralizes the `GeneralLLM` abstract base class.
  - Subclasses: `GeminiLLM` (using `google-genai`), `MistralLLM` (using `mistralai`).
  - Supports unstructured string prompts as well as schema-validated Pydantic models via `response_model`.
  - Factory function: `create_llm(provider, model=None, temperature=None)`.
- **`doven_kalender.extractor.pu`**:
  Extracts tabular data from OpenDocument (`.odt`) files downloaded from Google Docs by inspecting `content.xml`. Handles repeated columns and cell normalization, exporting output to CSV.
- **`doven_kalender.parser.convert_csv_to_json`**:
  Classifies CSV rows into "left" and "right" target months, normalizes Danish date strings (e.g. `12. maj`), and outputs a structured JSON object.
- **`doven_kalender.parser.get_emojis`**:
  Feeds calendar entries into an LLM with strict JSON formatting to associate a unique, relevant emoji with every entry.
- **`scripts.pu_calendar_pipeline`**:
  Unified one-shot command that downloads/reads an ODT file, converts it to CSV, converts CSV to JSON for two specified months, and runs emoji enrichment.

---

## 3. Setup, Tooling, and Configuration

### Prerequisites
- **Python**: Version **>= 3.14** (as defined in `pyproject.toml`).
- **uv**: Recommended fast Python package manager and runner (`https://astral.sh/uv`).
- **Optional CLI tools**:
  - `typst`: For compiling `.typ` visual calendar layouts.
  - `vips` (`libvips-tools`): For running background image processing in `generator/prepare_image.sh`.
  - `d2`: For compiling diagrams in `docs/` (`make`).

### Dependency Management
Dependencies are managed via `pyproject.toml` and locked in `uv.lock`. Key packages:
- `google-genai>=1.73.1`: Official Google Gemini API client.
- `mistralai>=2.4.3`: Official Mistral AI client.
- `pydantic>=2.13.3`: Data validation and JSON schema generation.
- `pytest>=9.0.3`: Test runner.

### Environment Variables & Secrets
Secrets and configuration are loaded from the environment or a `.env` file (see `.env.example`).
Use `environment.py` (`load_dotenv()`) or `doven_kalender.parser.get_emojis.load_env_file()`.

| Variable | Description |
| :--- | :--- |
| `GOOGLE_API_KEY` | API key for Google Calendar API queries |
| `GOOGLE_CALENDAR_ID` | Google Calendar identifier (without `@group.calendar.google.com`) |
| `DOCS_DOCUMENT_URL` | Google Docs export URL (`https://docs.google.com/document/d/<ID>/export?format=odt`) |
| `DOCS_COOKIE` | Session cookie for authenticated downloads of protected Google Docs |
| `DOCS_ODT_FILE` | (Optional) Path to a local `.odt` file override |
| `GEMINI_KEY` | API key for Google Gemini LLM |
| `MISTRAL_KEY` | API key for Mistral LLM |
| `DOVEN_LLM_PROVIDER` | Default LLM provider (`gemini` or `mistral`, defaults to `gemini`) |
| `FACEBOOK_API_KEY` | API key for Facebook integrations |
| `EMAIL_USERNAME` | SMTP / IMAP username for email notifications |
| `EMAIL_PASSWORD` | SMTP / IMAP password for email notifications |
| `EMAIL_HOST` | Hostname of the email server |

> **Warning:** Never commit `.env` or any sensitive credentials to version control.

---

## 4. Running Tests and Pipelines

### Running Tests
The test suite utilizes Python's standard `unittest` framework and `pytest`.

```bash
# Run all tests using Python standard unittest (zero external setup required)
python3 -m unittest discover tests

# Or run via uv / pytest
uv run pytest
```

Always ensure `python3 -m unittest discover tests` runs cleanly before pushing changes.

### Running CLI Pipelines

#### 1. The PU Calendar Pipeline (`pu-pipeline`)
Converts a Google Docs ODT table into emoji-enriched JSON:

```bash
# Basic run specifying the two calendar months
uv run pu-pipeline maj juni

# Override options
uv run pu-pipeline maj juni \
  --odt assets/E26.docx.odt \
  --csv assets/output.csv \
  --json generator/data.json \
  --provider gemini \
  --temperature 1.3
```

#### 2. Doven Kalender Main Orchestration
Fetches upcoming events from Google Calendar and generates a Danish Facebook announcement:

```bash
uv run doven-kalender
# or
python3 -m doven_kalender
```

#### 3. Compiling Documentation Diagrams
Recompiles the D2 diagrams in `docs/`:

```bash
make
```

---

## 5. Contribution & GitHub Workflow

### Branch Protection Policy
> **Crucial Rule:** Direct pushes to the `main` branch are **prohibited** by GitHub repository rules. All changes must be delivered via Pull Requests and reviewed/approved by at least one other team member.

### Recommended Contribution Workflow

1. **Update Local `main`**:
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Create a Topic / Feature Branch**:
   Use meaningful branch names prefixed with `feature/`, `feat/`, `fix/`, or `docs/`:
   ```bash
   git checkout -b feat/add-email-verification
   ```

3. **Develop & Test Locally**:
   - Keep code idiomatic and typed (`from __future__ import annotations`).
   - Preserve existing comments and docstrings.
   - Run tests to confirm there are no regressions:
     ```bash
     python3 -m unittest discover tests
     ```

4. **Commit with Clear Messages**:
   Follow Conventional Commits where practical (e.g., `feat: ...`, `fix: ...`, `docs: ...`):
   ```bash
   git add .
   git commit -m "feat(poster): add draft email verification service"
   ```

5. **Push Branch to Remote**:
   ```bash
   git push -u origin feat/add-email-verification
   ```

6. **Open a Pull Request**:
   - Open a PR against `main` on GitHub: [jehaj/doven-kalender](https://github.com/jehaj/doven-kalender).
   - Describe what changed and include test verification details.
   - Request review from a teammate.

7. **Merge & Clean Up**:
   - Once approved and CI checks pass, merge the PR into `main`.
   - Delete the branch locally and remotely:
     ```bash
     git checkout main
     git pull origin main
     git branch -d feat/add-email-verification
     git push origin --delete feat/add-email-verification
     ```

---

## 6. Current State & Future Directions

### Current Status
- **Extraction & Parsing:** Fully functional for both Google Calendar and Google Docs ODT exports.
- **LLM Abstraction:** Shared `GeneralLLM` interface in place supporting Gemini and Mistral, with structured JSON schema validation.
- **Emoji Enrichment:** Fully functional in `scripts/pu_calendar_pipeline.py`.
- **Graphic Template:** Typst template exists (`generator/typst_fb_template.typ`), but automated invocation in `generator/compile_typst.py` is a work-in-progress.

### Social Media & Poster Status (Facebook vs. Email Verification)
- **Direct Facebook Posting is Paused:**
  Automated posting directly to a Facebook group via bot/API is currently paused. Graph API restrictions, authentication token lifecycle management, and bot limitations in Facebook groups present significant maintenance hurdles.
- **Planned Direction: Email Verification Flow:**
  Instead of posting blindly, the planned architecture sends the generated announcement (text + calendar graphic) via email to the assigned event/meeting leader. The leader can:
  1. Review and verify the information for accuracy.
  2. Copy/post directly to Facebook or click an approval link to publish.
- Relevant configuration placeholders (`EMAIL_USERNAME`, `EMAIL_PASSWORD`, `EMAIL_HOST`) are already reserved in `.env.example` and `doven_kalender/generator/poster.py`.

### Next Milestones
- [ ] Implement email dispatch service in `doven_kalender.generator.poster` using SMTP configuration.
- [ ] Implement Typst compilation automation in `doven_kalender.generator.compile_typst`.
- [ ] Consider containerization with Docker for reproducible deployment.
