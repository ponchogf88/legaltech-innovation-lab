# `TASKS.md` — Persistent Task Queue & Mission Tracking

> Governed by `PROJECT_STATE.json` and the immutable 72-Hour Project Clock (`72H_CLOCK.json`: `2026-11-15T14:03:47-06:00` $\rightarrow$ `2026-11-18T14:03:47-06:00`).  
> Every task specifies: **Task ID**, **Description**, **Priority**, **Dependencies**, **Assigned Agent**, **Status**, **Acceptance Criteria**, and **Evidence of Completion**.

---

## Mission 002 — Continuous Engineering Protocol, E2E & CI Gates

| Task ID | Description | Priority | Dependencies | Assigned Agent | Status | Acceptance Criteria | Evidence of Completion |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`M2-00`** | Initialize Continuous Engineering Protocol, immutable 72-hour project clock (`2026-11-15T14:03:47-06:00`), continuity Python engine, CLI commands (`clock`, `state`, `checkpoint`), and reporting artifacts. | `P0` | `M1-E3` | `Hydrogen-Continuity + Argon` | **`DONE`** | `continuity.py` + `tests/test_continuity_clock.py` pass; `72H_CLOCK.json`, `PROJECT_STATE.json`, `MILESTONES.md`, `EXECUTION_LOG.md`, `CHECKPOINT.json`, and updated `TASKS.md` pass `security-check`. | `tests/test_continuity_clock.py` (`8/8 passed`), `72H_CLOCK.json` verified immutable |
| **`M2-01`** | Automated Playwright headless Chromium E2E suite verifying Command Center synthetic intake, Fact-vs-Conclusion separation, `SubmissionBlockedError` HITL lock, rejection loop (`IN_REVIEW -> DRAFT`), nominal lawyer approval (`APPROVED`), `MockAuthority` (`MOCK-`) folio receipt, and SHA-256 audit timeline integrity. | `P0` | `M2-00` | `Hydrogen-E2E` | **`READY`** | `tests/e2e/command_center_e2e.mjs` passes all 6 DOM/state checks against built `dist/`; `tests/test_e2e_playwright.py` passes inside `pytest`. | Pending isolated worktree `feat/m2-playwright-e2e` |
| **`M2-04`** | Automated GitHub Actions CI Quality & Security Gate (`.github/workflows/ci-quality-security.yml`) enforcing `security-check`, `pytest`, CLI `demo`/`clock`/`state`, Vite build, and Playwright E2E, plus contract tests (`tests/test_ci_workflow.py`). | `P0` | `M2-00` | `Hydrogen-CI` | **`READY`** | `.github/workflows/ci-quality-security.yml` uses least-privilege `contents: read`, triggers on `main` & `dev/**`, and runs all quality/security/E2E gates; `tests/test_ci_workflow.py` passes. | Pending isolated worktree `feat/m2-ci-gate` |
| **`M2-02`** | Structured OpenTelemetry span instrumentation across `intake`, `documents`, `review`, `submissions`, `security`, and `api.py` endpoints. | `P1` | `M2-01`, `M2-04` | `Hydrogen-Telemetry` | **`BACKLOG`** | Span attributes trace workflow stages with zero PII leakage. | Scheduled after `M2-01` & `M2-04` |
| **`M2-03`** | Real-time Server-Sent Events (SSE) bridge from `api.py` to React Command Center UI for live `ReviewQueue` and `AuditLog` updates. | `P1` | `M2-01` | `Hydrogen-SSE` | **`BACKLOG`** | Command Center receives live SSE events with automatic local sandbox fallback. | Scheduled after `M2-01` |
| **`M2-05`** | Additional 100% synthetic domain packs (corporate governance & regulatory compliance) with strict schema contracts and Jinja2 templates. | `P2` | `M2-01` | `Hydrogen-Templates` | **`BACKLOG`** | Synthetic domain fixtures & templates pass `security-check` and unit tests. | Scheduled after `M2-01` |

---

## Mission 001 — Completed Archive (`dev/mission-001` @ `8d3ad92`)

| Task ID | Description | Priority | Dependencies | Assigned Agent | Status | Acceptance Criteria | Evidence of Completion |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`M1-A1`** | Repository governance, architecture docs, dual-tier agent operating model, and editorial design system (`README.md`, `AGENTS.md`, `TASKS.md`, `SECURITY.md`, `docs/ARCHITECTURE.md`, `docs/DESIGN_SYSTEM.md`). | `P0` | — | `Hydrogen-Docs + Argon` | **`DONE`** | All 6 governance/architecture docs committed cleanly on `feat/docs-governance`. | Merged at `ddda412` (`a1afe48`) |
| **`M1-B1`** | Core Python `legal_engine` package (`models`, `intake`, `documents`, `review`, `submissions`, `authorities`, `deadlines`, `storage`, `api`, `cli`), Jinja2 templates, synthetic examples. | `P0` | `M1-A1` | `Hydrogen-Backend` | **`DONE`** | `StrictUndefined` templates, `SubmissionBlockedError` before `APPROVED`, `MockAuthority` `MOCK-` folios only, `cli demo` passing. | Merged at `8c46f7d` (`3b88834`) |
| **`M1-C1`** | Security/PII/real-case guardrails (`security.py`), EU AI Act + LFPDPPP governance evaluator, and SHA-256 `AuditLog`. | `P0` | `M1-A1` | `Hydrogen-Security` | **`DONE`** | Zero PII/secret findings on repo scan; `evaluate_governance_readiness` 6/6; hash-chain tamper detection verified. | Merged at `920aa5b` (`3ec6edd`) |
| **`M1-D1`** | Editorial LegalTech Command Center UI (`apps/command-center/`: React 18 + Vite, `tokens.css`, Agent Rail, HITL gate panel, Fact-vs-Conclusion inspector, Audit timeline). | `P0` | `M1-A1` | `Hydrogen-Frontend` | **`DONE`** | UI builds cleanly (`vite build`) and enforces client-side HITL lock & synthetic watermark. | Merged at `d8f4e87` (`281e359`) |
| **`M1-E1`** | Integration test suite (`tests/test_engine_core.py`, `tests/test_storage_sqlite.py`, `tests/test_api_endpoints.py`). | `P0` | `M1-B1`, `M1-C1`, `M1-D1` | `Hydrogen-Integration` | **`DONE`** | `50/50` pytest tests passing with zero skipped assertions. | Commit `8ff5bb0` on `dev/mission-001` |
| **`M1-E2`** | Cross-verification of repository security scan (`security-check`), SAT generic RFC placeholders, and CLI entrypoint parity. | `P0` | `M1-E1` | `Argon + Hydrogen` | **`DONE`** | `python -m legal_engine.cli security-check` clean (`scan_clean: true`, `governance_ready: true`). | Commits `8ff5bb0`, `8d3ad92` |
| **`M1-E3`** | Mission 001 engineering deployment and security verification report (`docs/MISSION_001_REPORT.md`). | `P0` | `M1-E2` | `Argon` | **`DONE`** | Comprehensive accuracy-checked Mission 001 report committed and passing `security-check`. | Commits `2219551`, `8d3ad92` |
| **`M1-MAIN-MERGE`** | Owner review and authorization to merge verified `dev/*` deliverables into `main` (`119c13d`). | `P1` | `M1-E3` | `Project Owner + Argon` | **`BLOCKED`** | Explicit owner authorization granted for `main` fast-forward/merge. | Pending Owner Approval (Blocker `B-02`; `main` untouched at `119c13d`) |
