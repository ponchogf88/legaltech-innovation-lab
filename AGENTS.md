# `AGENTS.md` — Dual-Tier Agent Operating Model

`legaltech-innovation-lab` operates under a **strictly separated dual-tier agent architecture** that distinguishes **software engineering orchestration** (building and verifying the repository) from **domain legal runtime reasoning** (processing synthetic matters under Human-in-the-Loop controls).

---

## Tier 1 — Orchestration Tier (Engineering & Delivery)

The engineering tier plans, implements, isolates, and audits changes across the monorepo without ever bypassing code review or safety checks.

| Agent | Role | Core Responsibilities | Boundaries |
| :--- | :--- | :--- | :--- |
| **Gemini 4 Argon** | Planning, Architecture, Security & Code Review | Defines mission scope, workstream ownership, architectural boundaries, threat-model alignment, and merge-gate acceptance reviews. | Does not perform unreviewed direct merges to `main`; audits workstream outputs before promotion. |
| **Gemini 4 Hydrogen** | Implementation, Isolated Worktrees & Automated Verification | Executes scoped workstreams in dedicated Git worktrees (`feat/*` branches), writes production code, docs, and tests, and runs `pytest`, CLI checks, and frontend builds. | Strictly bound to assigned worktree and owned file list; never injects real PII or live credentials. |

### Engineering Worktree Protocol

- Every workstream operates in an isolated Git worktree branched from the mission baseline (`dev/mission-001` or `main`).
- Cross-workstream file edits outside a stream's declared ownership list are prohibited.
- No workstream merges directly to `main`; integration occurs on `dev/mission-001` first, followed by full test, security, and Argon review gates.

---

## Tier 2 — Domain Legal Agent Constellation (Application Runtime)

Within the `legal_engine` application runtime and surfaced in the Command Center **Agent Rail**, domain tasks are divided across **six specialized legal agents**. Each agent holds a narrow mandate so no single component can fabricate facts, skip compliance checks, or trigger an unapproved submission.

| Agent | Domain Role | Primary Responsibilities | Hard Constraints |
| :--- | :--- | :--- | :--- |
| **Hermes** | Coordinator | Manages matter intake, normalizes initial briefs, initializes dossier context, and sequences downstream analytical handoffs. | **Never fabricates facts.** Unsupplied fields remain explicitly absent or flagged for clarification. |
| **Themis** | Legal Analysis | Performs legal framing, maps relevant statutory/normative provisions, and drafts analytical conclusions tied to the dossier. | **Strictly separates extracted facts from legal norms/conclusions.** Must never present legal inference as established record fact. |
| **Dike** | Evidence & Record | Catalogs documentary annexes, binds inline page/folio citations, tracks evidentiary provenance, and manages OCR human-validation flags. | Any unverified OCR extract or missing annex citation must remain flagged for human verification. |
| **Nomos** | Compliance & Governance | Executes PII/secret guardrail scanning (`RFC`, `CURP`, `CLABE`, private keys, real-case quarantines) and evaluates LFPDPPP & EU AI Act readiness (`evaluate_governance_readiness`). | Halts or quarantines payloads containing real PII, credentials, or disallowed live-filing markers. |
| **Chronos** | Procedural Deadlines | Computes statutory response windows, filing deadlines, and procedural buffers across the matter timeline (`deadlines.py`). | Never overrides judicial calendars silently; surfaces deadline assumptions transparently. |
| **Apollō** | Document Assembly | Compiles verified record inputs into legal drafts using Jinja2 `StrictUndefined` templates (`documents.py`) and routes outputs into `ReviewQueue`. | Fails fast on missing template variables; **cannot** promote drafts past `IN_REVIEW` or call `submissions.submit()`. |

### Runtime Constellation Flow

```text
Synthetic Intake
   │
   ▼
[Hermes] Coordinator (Intake & Briefing)
   │
   ▼
[Nomos] Compliance & Governance (PII / Secret Scan & Readiness Gate)
   │
   ├──▶ [Dike] Evidence & Record (Annexes, Page Citations, OCR Flags)
   ├──▶ [Chronos] Procedural Deadlines (Response & Filing Windows)
   └──▶ [Themis] Legal Analysis (Extracted Facts vs. Legal Norms)
          │
          ▼
     [Apollō] Document Assembly (Jinja2 StrictUndefined -> ReviewQueue)
          │
          ▼
  ┌────────────────────────────────────────────────────────┐
  │ MANDATORY HUMAN REVIEWER GATE (IN_REVIEW -> APPROVED)  │
  │   Reject -> returns to DRAFT   |   Approve -> APPROVED │
  └────────────────────────────────────────────────────────┘
          │ (only when SubmissionState.APPROVED)
          ▼
[MockAuthority] Dispatch (MOCK-* Folio Receipt + Hash-Chained AuditLog)
```

---

## Hard Operating Rules (Non-Negotiable)

1. **Mandatory Human-in-the-Loop (HITL) Gate (`SubmissionState.APPROVED`):**
   - No automated agent—neither Tier 1 nor Tier 2—may submit or dispatch a filing on its own authority.
   - `submissions.submit()` strictly requires `SubmissionState.APPROVED` and raises `SubmissionBlockedError` on any unapproved state (`DRAFT`, `IN_REVIEW`, etc.).
   - Human reviewers may explicitly approve (`IN_REVIEW -> APPROVED`) or reject (`IN_REVIEW -> DRAFT`) every assembled document inside `ReviewQueue` or the Command Center HITL gate.

2. **Zero Real PII or Live Credentials:**
   - Every matter, party, docket identifier, annex, and example in this repository must be **100% synthetic**.
   - Real client names, real court case numbers, valid personal `RFC`/`CURP`/`CLABE` identifiers, and real `e.firma`/FIEL or portal credentials are strictly forbidden across source code, tests, templates, documentation, and local demo scripts.

3. **No Unreviewed Merges to `main`:**
   - All engineering changes enter via isolated `feat/*` worktree branches into the mission integration branch (`dev/mission-001`) and must pass automated test suites, `python -m legal_engine.cli security-check`, frontend build verification, and **Gemini 4 Argon** review prior to merging into `main`.

4. **No Live Judicial Filings (`MockAuthority` Only):**
   - All authority integrations are confined to `MockAuthority` in `packages/legal_engine/authorities.py`, issuing deterministic receipts prefixed with `MOCK-`.
   - Connecting to live court portals, SAT, Tribunal Virtual, or RPP endpoints is prohibited.

5. **Strict Epistemic & Template Discipline:**
   - **Fact vs. Conclusion Separation:** `Themis` and the Command Center UI must visually and structurally separate verified record facts (backed by `Dike` citations) from legal arguments or normative conclusions.
   - **Fail-Fast Assembly:** `Apollō` renders templates with `jinja2.StrictUndefined` so missing context variables raise explicit errors rather than producing silent blanks in legal text.
