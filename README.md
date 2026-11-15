# `legaltech-innovation-lab` — Master LegalTech Engineering & Governance Monorepo

> **Disclaimer (Synthetic Portfolio / Lab Only):** `legaltech-innovation-lab` is a **synthetic portfolio/lab system** built for LegalTech engineering, AI governance, and UX research. It does **not** provide legal advice, does **not** store or process real client data, and maintains **zero live connections** to judicial, tax, or administrative portals. All external authority dispatches run exclusively through `MockAuthority` (`MOCK-` folio prefix).

---

## Overview & Repository Lineage

`legaltech-innovation-lab` is the master monorepo uniting the core Python legal workflow engine, automated privacy and AI governance guardrails, and the Editorial LegalTech Command Center interface under a strict Human-in-the-Loop (HITL) architecture.

### Relationship to `ponchogf88/legal-practice-agent`

This monorepo builds on and supersedes the structural foundation explored in [`ponchogf88/legal-practice-agent`](https://github.com/ponchogf88/legal-practice-agent):

- **`ponchogf88/legal-practice-agent`** is the focused, single-package CLI prototype that introduced and validated the mandatory Human-in-the-Loop submission state machine (`DRAFT -> IN_REVIEW -> APPROVED -> SUBMITTED -> RECEIPTED`).
- **`legaltech-innovation-lab`** scales that core pattern into a governed multi-workstream monorepo adding SQLite persistence, Jinja2 `StrictUndefined` document assembly, automated PII/secret guardrails, LFPDPPP and EU AI Act readiness scoring, a hash-chained JSONL audit log, an HTTP JSON API, and a React 18 Command Center UI.

### Quarantine Notice: Unversioned Legacy UI Demos

Any unversioned legacy UI demos, ad-hoc static HTML mockups, or early experimental notebooks from prior explorations are **formally quarantined** outside this repository. They must **not** be imported, served, or merged into `legaltech-innovation-lab`. All user-facing UI functionality in this lab is authored cleanly from first principles inside `apps/command-center/` against [`docs/DESIGN_SYSTEM.md`](docs/DESIGN_SYSTEM.md).

---

## Monorepo Architecture at a Glance

```text
legaltech-innovation-lab/
├── README.md                  # Repository overview, quickstart & disclaimers
├── AGENTS.md                  # Dual-tier orchestration & Domain Legal Agent Constellation
├── TASKS.md                   # Mission 001 workstream matrix & Mission 002 backlog
├── SECURITY.md                # Threat model, HITL gate, PII guardrails & audit integrity
├── docs/
│   ├── ARCHITECTURE.md        # End-to-end pipeline, state machine & module inventory
│   └── DESIGN_SYSTEM.md       # Editorial LegalTech tokens, typography & 3-column layout
├── packages/
│   └── legal_engine/          # Core Python workflow, security, API & CLI engine
├── apps/
│   └── command-center/        # React 18 + Vite Editorial LegalTech Command Center UI
├── templates/                 # Jinja2 StrictUndefined legal document templates
├── examples/                  # 100% synthetic sample matters and intake fixtures
├── tests/                     # Unit, HITL gate, security guardrail & API tests
├── pyproject.toml             # Python >=3.11 packaging & pytest configuration
├── requirements.txt           # Pinned base dependencies (jinja2, pytest)
├── .env.example               # Sanitized environment template (placeholders only)
└── LICENSE                    # MIT License
```

### Core Modules

#### 1. `packages/legal_engine/` (Python >=3.11 Core Engine)

| Module | Responsibility |
| :--- | :--- |
| `models.py` | Domain entities, `SubmissionState` enum, typed dossier/annex/deadline records |
| `intake.py` | Structured matter intake validation and synthetic record normalization |
| `documents.py` | Deterministic document assembly using `jinja2.StrictUndefined` templates |
| `review.py` | `ReviewQueue` orchestration for human inspection, approval, and rejection loops |
| `submissions.py` | Controlled dispatch gateway enforcing `SubmissionState.APPROVED` (`SubmissionBlockedError`) |
| `authorities.py` | Authority adapter boundary restricted to `MockAuthority` (`MOCK-` folio receipts) |
| `deadlines.py` | Procedural window and filing deadline calculation engine |
| `audit.py` | Append-only SHA-256 hash-chained JSONL `AuditLog` with `verify_integrity()` |
| `storage.py` | Local SQLite persistence for matters, drafts, review decisions, and deadlines |
| `security.py` | PII/secret guardrail scanning (`RFC`, `CURP`, `CLABE`, keys) and `evaluate_governance_readiness` |
| `api.py` | Local HTTP JSON API exposing matter state, review queue actions, audit trail, and security posture |
| `cli.py` | Developer & operator CLI (`demo`, `security-check`, API serving, audit verification) |

#### 2. `apps/command-center/` (React 18 + Vite Command Center UI)

- Built with **React 18** and **Vite** following the Editorial LegalTech aesthetic defined in [`docs/DESIGN_SYSTEM.md`](docs/DESIGN_SYSTEM.md).
- Consumes design tokens from `tokens.css` (Obsidian framing `#151917`, Archival Parchment `#f2ede2` / `#faf7f0`, Copper/Sage/Amber/Crimson semantic accents, `Instrument Serif`, `Plus Jakarta Sans`, and `DM Mono`).
- Implements the 3-column LegalTech workstation (**Agent Rail** | **Orchestration & Interactive HITL Approval Gate** | **Evidence & Audit Inspector**) with strict Fact-vs-Conclusion visual separation.

---

## Quickstart

### Prerequisites

- Python `>= 3.11` and [`uv`](https://docs.astral.sh/uv/)
- Node.js `>= 20` and `npm` (for `apps/command-center/`)

### 1. Create the Python Environment & Install in Editable Mode

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

Optional local environment configuration (uses sanitized defaults/placeholders only):

```bash
cp .env.example .env
```

### 2. Run Verification, Demo Pipeline & Security Guardrails

```bash
# Execute the Python test suite
pytest -v

# Run the end-to-end synthetic workflow demo (Intake -> Review Gate -> MockAuthority -> Audit)
python -m legal_engine.cli demo

# Run automated PII, secret, and governance readiness checks
python -m legal_engine.cli security-check
```

### 3. Build the Command Center Frontend

```bash
cd apps/command-center && npm install && npm run build
```

If dependencies are already installed:

```bash
cd apps/command-center && npm run build
```

---

## Governance & Reference Documentation

- **[AGENTS.md](AGENTS.md)** — Dual-tier agent operating model (Argon/Hydrogen engineering tier + 6-agent Domain Legal Constellation) and hard safety rules.
- **[TASKS.md](TASKS.md)** — Mission 001 workstream tracking matrix (Workstreams A–E) and Mission 002 backlog.
- **[SECURITY.md](SECURITY.md)** — Threat model, HITL enforcement, PII/secret scanning, LFPDPPP & EU AI Act controls, and hash-chained audit verification.
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — End-to-end pipeline flowchart, submission state machine, and full module inventory.
- **[docs/DESIGN_SYSTEM.md](docs/DESIGN_SYSTEM.md)** — Editorial LegalTech color tokens, typography scale, 3-column layout rules, and WCAG / Fact-vs-Conclusion standards.

---

## License

Released under the [MIT License](LICENSE).
