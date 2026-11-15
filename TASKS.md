# `TASKS.md` — Mission Tracking & Engineering Backlog

## Mission 001 — Governed Monorepo & Editorial Command Center

Mission 001 establishes the complete `legaltech-innovation-lab` monorepo across five isolated workstreams before merging into `dev/mission-001` and undergoing **Gemini 4 Argon** merge-gate review for `main`.

### Workstream Tracking Matrix (Workstreams A–E)

| Workstream | Scope & Title | Owner | Branch & Worktree | Primary Deliverables | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A** | Repository & Engineering Documentation | Gemini 4 Hydrogen (Docs) + Gemini 4 Argon (Review) | `feat/docs-governance`<br>`wt-docs` | `README.md`, `AGENTS.md`, `TASKS.md`, `SECURITY.md`, `docs/ARCHITECTURE.md`, `docs/DESIGN_SYSTEM.md` | **Completed (Pending Merge to `dev/mission-001`)** |
| **B** | Core Python Legal Engine, Persistence & API | Gemini 4 Hydrogen (Backend) | `feat/backend-core`<br>`wt-backend` | `packages/legal_engine/` (`models.py`, `intake.py`, `documents.py`, `review.py`, `submissions.py`, `authorities.py`, `deadlines.py`, `storage.py`, `api.py`, `cli.py`), `templates/`, `examples/`, backend tests | **Active (Parallel Worktree)** |
| **C** | Security, Privacy, AI Governance & Audit Chain | Gemini 4 Hydrogen (Security) | `feat/security-privacy`<br>`wt-security` | `packages/legal_engine/security.py`, `packages/legal_engine/audit.py`, `security-check` CLI command, PII/secret guardrails, LFPDPPP & EU AI Act readiness checks, security tests | **Active (Parallel Worktree)** |
| **D** | Editorial LegalTech Command Center UI | Gemini 4 Hydrogen (Frontend) | `feat/frontend-ui`<br>`wt-frontend` | `apps/command-center/` (React 18 + Vite, `tokens.css`, 3-column workstation, Agent Rail, interactive HITL Review Gate, Evidence & Audit Inspector) | **Active (Parallel Worktree)** |
| **E** | Integration, End-to-End Verification & Merge Gate | Gemini 4 Argon (Gate) + Gemini 4 Hydrogen (Integration) | `dev/mission-001`<br>`legaltech-innovation-lab` | Merge A–D into `dev/mission-001`, resolve any interface contracts, run full `pytest -v`, `demo`, `security-check`, `npm run build`, audit synthetic-only compliance before `main` | **Pending A–D Completion** |

---

### Mission 001 Acceptance Criteria Checklists

#### Workstream A — Repository & Engineering Documentation (`feat/docs-governance`)
- [x] `README.md` distinguishes `legaltech-innovation-lab` from `ponchogf88/legal-practice-agent` and states legacy UI demo quarantine.
- [x] `AGENTS.md` defines the dual-tier operating model (Argon/Hydrogen + Hermes/Themis/Dike/Nomos/Chronos/Apollō) and hard safety rules.
- [x] `TASKS.md` documents Mission 001 Workstreams A–E and Mission 002 backlog.
- [x] `SECURITY.md` specifies HITL gate enforcement, PII/secret guardrails, AI Act & LFPDPPP alignment, `MockAuthority` isolation, and hash-chained audit verification.
- [x] `docs/ARCHITECTURE.md` includes Mermaid pipeline flowchart, submission state machine diagram, and module inventory table.
- [x] `docs/DESIGN_SYSTEM.md` defines `--bg-obsidian`, `--bg-parchment`, `--bg-parchment-elevated`, semantic accents, typography scale, 3-column workstation layout, WCAG contrast, and Fact-vs-Conclusion separation rules.
- [x] All 6 files audited and committed cleanly on `feat/docs-governance` with zero files outside owned paths.

#### Workstream B — Core Python Legal Engine (`feat/backend-core`)
- [ ] `packages/legal_engine/` implements `models.py`, `intake.py`, `documents.py`, `review.py`, `submissions.py`, `authorities.py`, `deadlines.py`, `storage.py`, `api.py`, and `cli.py`.
- [ ] `documents.py` enforces `jinja2.StrictUndefined` rendering against `templates/`.
- [ ] `submissions.submit()` blocks any non-approved submission with `SubmissionBlockedError`.
- [ ] `authorities.py` exposes only `MockAuthority` issuing `MOCK-` prefixed folios.
- [ ] `python -m legal_engine.cli demo` completes end-to-end with 100% synthetic fixtures from `examples/`.
- [ ] Unit and integration tests pass via `pytest -v`.

#### Workstream C — Security, Privacy & AI Governance (`feat/security-privacy`)
- [ ] `security.py` detects and flags synthetic-policy violations (`RFC`, `CURP`, `CLABE`, PEM/FIEL keys, real-case quarantine markers).
- [ ] `evaluate_governance_readiness` scores EU AI Act and LFPDPPP controls cleanly.
- [ ] `audit.py` implements append-only SHA-256 hash-chained JSONL logging and `AuditLog.verify_integrity()`.
- [ ] `python -m legal_engine.cli security-check` executes cleanly and passes on repository artifacts.
- [ ] Security and tamper-detection tests pass via `pytest -v`.

#### Workstream D — Editorial LegalTech Command Center (`feat/frontend-ui`)
- [ ] `apps/command-center/` scaffolds React 18 + Vite application consuming `tokens.css` per `docs/DESIGN_SYSTEM.md`.
- [ ] 3-column workstation implements Left Agent Rail, Center Orchestration & HITL Review Gate, and Right Evidence & Audit Inspector.
- [ ] Interactive HITL gate triggers `approve` (`IN_REVIEW -> APPROVED`) and `reject` (`IN_REVIEW -> DRAFT`) API transitions and reflects Fact-vs-Conclusion visual separation.
- [ ] `cd apps/command-center && npm run build` succeeds with zero build errors.

#### Workstream E — Integration & Merge Gate (`dev/mission-001` -> `main`)
- [ ] Branches `feat/docs-governance`, `feat/backend-core`, `feat/security-privacy`, and `feat/frontend-ui` merged cleanly into `dev/mission-001`.
- [ ] Full `pytest -v` suite passes post-merge with zero skipped/relaxed assertions.
- [ ] `python -m legal_engine.cli demo` and `python -m legal_engine.cli security-check` pass post-merge.
- [ ] `cd apps/command-center && npm run build` succeeds post-merge.
- [ ] **Gemini 4 Argon** completes final security, synthetic-data, and diff review prior to merging `dev/mission-001` into `main`.

---

## Mission 002 Backlog (Planned Enhancements)

| ID | Initiative | Summary | Target Area |
| :--- | :--- | :--- | :--- |
| **M2-01** | **Playwright E2E Verification** | Automated headless browser suite driving the full React Command Center against live local `api.py` (intake selection, HITL rejection back to `DRAFT`, approval to `APPROVED`, `MockAuthority` `MOCK-` dispatch, and audit log verification). | `apps/command-center/`, `tests/e2e/` |
| **M2-02** | **OpenTelemetry Tracing** | Structured OTel spans and trace context propagation across `intake`, `documents`, `review`, `submissions`, `security`, and `api.py` endpoints for latency and decision-path observability. | `packages/legal_engine/` |
| **M2-03** | **Real-Time SSE Bridge** | Server-Sent Events endpoint in `api.py` pushing live `ReviewQueue` transitions, `Chronos` deadline alerts, and `AuditLog` hash entries directly to the Command Center without manual polling. | `packages/legal_engine/api.py`, `apps/command-center/` |
| **M2-04** | **Automated CI Quality & Security Gate** | GitHub Actions workflow running `pytest -v`, `security-check`, `npm run build`, WCAG contrast/axe checks, and Mermaid syntax linting on every PR targeting `dev/*` or `main`. | `.github/workflows/` |
| **M2-05** | **Synthetic Domain Expansion Packs** | Additional synthetic procedural templates (e.g., administrative notices, synthetic contract review checklists) with strict schema contracts and OCR human-validation fixtures. | `templates/`, `examples/` |
