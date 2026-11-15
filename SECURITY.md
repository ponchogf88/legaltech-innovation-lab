# `SECURITY.md` — Threat Model, Privacy Guardrails & Governance Posture

> **Security Baseline:** `legaltech-innovation-lab` is engineered as a **zero-PII, offline-isolated, Human-in-the-Loop (HITL) legal workflow lab**. No live judicial portal credentials, real client dossiers, or unapproved autonomous filings are permitted anywhere in the repository or runtime.

---

## 1. Threat Model & Control Matrix

| Threat / Risk Vector | Impact if Unmitigated | Primary Control | Verification Anchor |
| :--- | :--- | :--- | :--- |
| **Autonomous / Unapproved Legal Filing** | Agent dispatches an unreviewed or hallucinated legal document to an authority interface. | Mandatory HITL gate: `submissions.submit()` enforces `SubmissionState.APPROVED` and raises `SubmissionBlockedError` on all other states. | `packages/legal_engine/submissions.py`, `review.py`, HITL tests |
| **Real PII or Credential Leakage** | Personal data (`RFC`, `CURP`, `CLABE`), client names, court dockets, or `e.firma`/FIEL private keys enter git history or logs. | Synthetic-only policy + automated PII/secret guardrail scanning via `security.py` and strict `.gitignore` rules. | `python -m legal_engine.cli security-check`, `.gitignore` |
| **Live Authority Side-Effects** | Test or demo workflow accidentally contacts a live court, tax (SAT), or registry portal. | Strict adapter isolation: `authorities.py` only implements `MockAuthority`, issuing `MOCK-` prefixed folios. | `packages/legal_engine/authorities.py`, `.env.example` |
| **Audit Trail Tampering** | Post-hoc modification, deletion, or reordering of review approvals or submission records. | Append-only JSONL log where each record links to the prior SHA-256 hash, validated via `AuditLog.verify_integrity()`. | `packages/legal_engine/audit.py` |
| **Silent Template Corruption** | Missing matter variables render empty gaps in formal legal text. | `documents.py` compiles Jinja2 templates using `StrictUndefined`, failing fast on any undefined placeholder. | `packages/legal_engine/documents.py` |
| **AI Governance Non-Compliance** | Opaque automated decisions, lack of human oversight, or unmarked synthetic/AI outputs. | `evaluate_governance_readiness` checks EU AI Act & LFPDPPP alignment; UI enforces Fact-vs-Conclusion separation. | `packages/legal_engine/security.py`, `docs/DESIGN_SYSTEM.md` |

---

## 2. Mandatory Human-in-the-Loop (HITL) Enforcement

Human oversight is enforced both programmatically in the workflow engine and visually in the Command Center:

1. **State Gate (`submissions.submit()`):**
   - Only drafts explicitly promoted by a human reviewer to `SubmissionState.APPROVED` can cross the dispatch boundary.
   - Calling `submissions.submit()` for any item in `DRAFT`, `IN_REVIEW`, `SUBMITTED`, or `RECEIPTED` immediately raises `SubmissionBlockedError` and logs the blocked attempt.
2. **Explicit Rejection Loop (`IN_REVIEW -> DRAFT`):**
   - When a reviewer rejects a draft in `ReviewQueue` or the Command Center HITL gate, the state returns to `DRAFT` with reviewer notes attached in SQLite and recorded in the audit chain.
3. **Separation of Duties Across Agents:**
   - `Apollō` assembles drafts and routes them to `ReviewQueue`; `Themis` frames legal arguments separately from `Dike` factual citations; **no agent possesses permission to self-approve**.

---

## 3. Synthetic-Only Data Policy & Automated PII / Secret Guardrails

All fixtures, templates, tests, examples, and documentation in `legaltech-innovation-lab` must contain **100% synthetic data only**.

### Automated Guardrail Categories (`security.py` & `security-check`)

Running `python -m legal_engine.cli security-check` scans workspace payloads and artifacts against guardrail rules covering:

- **Mexican Financial & Identity Identifiers:** Detection patterns for `RFC` (tax IDs), `CURP` (population registry codes), and 18-digit `CLABE` interbank account numbers.
- **Cryptographic & Digital Signature Secrets:** Detection of PEM-encoded private key headers, X.509 / SAT `e.firma` (FIEL) `.key` and `.cer` credential material, bearer tokens, and populated portal passwords.
- **Real-Case Quarantines:** Quarantine checks flagging disallowed real-client markers, non-synthetic court docket patterns, and unversioned legacy UI demo artifacts.

### Repository Hygiene (`.gitignore` & `.env.example`)

- `.gitignore` blocks local artifacts that could accumulate state or secrets: `.env`, `.env.*` (except `.env.example`), `*.pem`, `*.key`, `*.cer`, `*.db`, `*.sqlite`, `*.sqlite3`, and `*.jsonl`.
- `.env.example` provides **empty placeholder variables only** (`TRIBUNAL_VIRTUAL_USER=`, `TRIBUNAL_VIRTUAL_PASSWORD=`, `SAT_EFIRMA_KEY_PATH=`, `SAT_EFIRMA_CERT_PATH=`, `RPP_USER=`, `RPP_PASSWORD=`) alongside local paths (`LEGAL_LAB_DB_PATH`, `LEGAL_LAB_AUDIT_PATH`, `LEGAL_LAB_API_HOST`, `LEGAL_LAB_API_PORT`). Real credentials must never be committed.

---

## 4. EU AI Act & Mexican LFPDPPP Alignment (`evaluate_governance_readiness`)

The engine includes `evaluate_governance_readiness` in `packages/legal_engine/security.py` to evaluate operational compliance across two primary governance frameworks:

- **EU AI Act (High-Risk / Legal Assistance Controls):**
  - **Human Oversight (Art. 14):** Verifies that mandatory HITL approval gates are active and unbypassable prior to dispatch.
  - **Transparency & Traceability:** Confirms synthetic/AI provenance disclosures, explicit separation of extracted facts vs. legal conclusions, and deterministic `StrictUndefined` template rendering.
  - **Record-Keeping / Logging:** Verifies active hash-chained audit logging (`AuditLog`) for every state transition and review decision.
- **LFPDPPP (Ley Federal de Protección de Datos Personales en Posesión de los Particulares):**
  - **Data Minimization & Purpose Limitation:** Enforces synthetic-only inputs in non-production environments and flags personal/sensitive identifiers (`RFC`, `CURP`, `CLABE`) before persistence.
  - **Security Measures:** Ensures local SQLite and audit logs remain outside version control and free of live credentials.

---

## 5. Authority Isolation (`MockAuthority`)

`packages/legal_engine/authorities.py` provides strict transport isolation:

- The sole implemented authority target is **`MockAuthority`**.
- Every simulated filing response returns a synthetic receipt whose folio begins with the **`MOCK-`** prefix (for example, `MOCK-...`), ensuring unambiguous distinction from official judicial or administrative receipts.
- No live judicial accounts, court scraping clients, or external filing webhooks exist in `legaltech-innovation-lab`.

---

## 6. Hash-Chained Append-Only JSONL Audit Log

Every critical lifecycle event—intake normalization, guardrail scan outcome, draft assembly, review approval/rejection, blocked submission attempt, and `MockAuthority` receipt—is appended to a JSONL audit log (`packages/legal_engine/audit.py`):

- **Append-Only Chaining:** Each entry records a timestamp, actor/agent identifier, event type, payload digest, `prev_hash`, and computed SHA-256 `entry_hash`.
- **Tamper Detection (`AuditLog.verify_integrity()`):** Replays the entire JSONL file from genesis, recomputing each entry's SHA-256 digest and verifying `entry.prev_hash == prior.entry_hash`. Any line deletion, insertion, reordering, or field mutation causes `verify_integrity()` to return a failure immediately.

---

## 7. Quarantine & Incident Protocol

If real PII, a live credential, or an unapproved legacy artifact is ever discovered in a worktree or branch:

1. **Halt & Quarantine:** Stop merges immediately and isolate the offending branch or payload.
2. **Purge & Rotate:** Remove the artifact from working files (and rewrite unmerged local commits if not yet pushed; rotate any exposed secret immediately).
3. **Re-Verify:** Run `python -m legal_engine.cli security-check` and `pytest -v` cleanly before resuming workstream integration.
