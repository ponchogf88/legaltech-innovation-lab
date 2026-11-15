# `DESIGN_SYSTEM.md` — Editorial LegalTech Design System

The `apps/command-center/` interface embodies an **Editorial LegalTech** aesthetic: authoritative archival reading surfaces framed by quiet obsidian operational telemetry. Every visual decision reinforces epistemic clarity—distinguishing verified record facts from legal conclusions—and elevates the Human-in-the-Loop (HITL) approval gate into an unmistakable point of accountability.

---

## 1. Surface & Semantic Color Tokens (`tokens.css`)

All UI components in `apps/command-center/` must consume CSS custom properties from `tokens.css` rather than hardcoding hex values.

### Core Surface Tokens

| Token | Hex | Role & Surface Usage |
| :--- | :--- | :--- |
| `--bg-obsidian` | `#151917` | Primary nocturnal workstation frame, Left Agent Rail, top telemetry bar, and dark badge ink on light surfaces. |
| `--bg-parchment` | `#f2ede2` | Primary editorial reading canvas for the Center Orchestration pane and Right Evidence & Audit Inspector. |
| `--bg-parchment-elevated` | `#faf7f0` | Elevated archival cards, active Jinja2 draft sheet, interactive HITL Review Gate panel, and modal surfaces. |

### Semantic Accent Tokens

| Token | Hex | Semantic Meaning & Usage |
| :--- | :--- | :--- |
| `--accent-copper` | `#b8643f` | Editorial focus, active legal norm attribution (`Themis`), primary section rules, and active matter focus indicators. |
| `--accent-sage` | `#4a6b5b` | Verified states (`SubmissionState.APPROVED`, `RECEIPTED`), `AuditLog.verify_integrity()` pass, and cleared `Nomos` compliance checks. |
| `--accent-amber` | `#c4883a` | Pending human review (`IN_REVIEW`), `Chronos` deadline warnings, and `Dike` OCR human-validation flags. |
| `--danger-crimson` | `#9e3b33` | Critical blocks (`SubmissionBlockedError`), HITL rejection (`IN_REVIEW -> DRAFT`), PII/secret guardrail hits, and audit integrity failures. |

---

## 2. Typography Scale

The Command Center pairs an authoritative serif display voice with clean humanist UI sans-serif and tabular monospace metadata.

| Role | Font Family | Scale & Weight Guidance | Usage Context |
| :--- | :--- | :--- | :--- |
| **Display / Editorial Headings** | `Instrument Serif` | `1.75rem–2.25rem` (`28px–36px`), regular (`400`), line-height `1.15` | Matter titles, formal draft headings, HITL Gate confirmation titles, editorial callouts. |
| **Section / Card Headings** | `Plus Jakarta Sans` | `1rem–1.125rem` (`16px–18px`), semibold (`600`), line-height `1.3` | Pane headers (`Agent Rail`, `Review Gate`, `Evidence & Audit`), annex titles, dialog titles. |
| **UI & Analytical Body** | `Plus Jakarta Sans` | `0.875rem–0.9375rem` (`14px–15px`), regular/medium (`400–500`), line-height `1.6` | Extracted fact summaries, `Themis` legal analysis prose, reviewer notes, form controls, buttons. |
| **Metadata / Folios / Timestamps** | `DM Mono` | `0.75rem–0.8125rem` (`12px–13px`), regular/medium (`400–500`), `font-variant-numeric: tabular-nums` | `MOCK-*` folios, SHA-256 hash chain prefixes, `SubmissionState` badges, `Chronos` deadlines, page/annex citations, ISO timestamps. |

---

## 3. Layout Rules — 3-Column LegalTech Workstation

On desktop viewports (`>= 1200px`), the Command Center renders a fixed-chrome **3-column workstation** optimized for side-by-side verification without burying evidence behind tabs:

```text
┌──────────────────────┬──────────────────────────────────────────┬─────────────────────────────┐
│  1. LEFT COLUMN      │  2. CENTER COLUMN                        │  3. RIGHT COLUMN            │
│  AGENT RAIL          │  ORCHESTRATION & HITL REVIEW GATE        │  EVIDENCE & AUDIT INSPECTOR │
│  (--bg-obsidian)     │  (--bg-parchment / --bg-parchment-elev.) │  (--bg-parchment)           │
│                      │                                          │                             │
│  • Hermes (Coord.)   │  • Matter Brief & Synthetic Disclaimer   │  • Dike Documentary Annexes │
│  • Nomos (Guard)     │  • Fact-vs-Conclusion Analytical Split   │  • Page Citations & OCR     │
│  • Dike (Record)     │  • StrictUndefined Draft Sheet           │    Human-Validation Flags   │
│  • Chronos (Time)    │  • Interactive HITL Gate:                │  • Chronos Deadlines Window │
│  • Themis (Analysis) │    [ Approve Submission ] (Sage)         │  • Nomos PII / AI Act Score │
│  • Apollō (Assembly) │    [ Reject to Draft ]    (Crimson)      │  • Hash-Chained AuditLog    │
│                      │  • MockAuthority MOCK-* Receipt Banner   │    (DM Mono SHA-256 chain)  │
└──────────────────────┴──────────────────────────────────────────┴─────────────────────────────┘
```

### Column Rules

1. **Left Column — Agent Rail (`260px–280px`, `--bg-obsidian`):**
   - Houses the six-agent Domain Legal Constellation (`Hermes`, `Themis`, `Dike`, `Nomos`, `Chronos`, `Apollō`) with live status tags and synthetic matter selector.
   - Displays persistent synthetic-lab notice and `Nomos` governance readiness summary.
2. **Center Column — Orchestration & HITL Review Gate (`minmax(520px, 1fr)`, `--bg-parchment` + `--bg-parchment-elevated`):**
   - Hosts the active draft document sheet, structured Fact-vs-Conclusion blocks, and the **HITL Approval Gate** anchored visibly at the bottom/header of the review workflow.
   - `Approve Submission` (`IN_REVIEW -> APPROVED`) and `Reject to Draft` (`IN_REVIEW -> DRAFT`) actions require explicit reviewer confirmation and capture optional reviewer notes; `Dispatch to MockAuthority` becomes interactive **only** after `SubmissionState.APPROVED` is reached.
3. **Right Column — Evidence & Audit Inspector (`340px–380px`, `--bg-parchment`):**
   - Displays `Dike` documentary annexes with inline page citations and explicit OCR human-validation badges (`--accent-amber` chip).
   - Displays `Chronos` procedural deadline countdowns (`DM Mono`), `Nomos` PII/secret scan results, and the append-only SHA-256 `AuditLog` feed with integrity badge (`AuditLog.verify_integrity()`).

### Responsive Collapsing (`< 1200px`)

- Below `1200px`, the workstation collapses gracefully: the Agent Rail condenses into a top obsidian switcher bar, while the **Center HITL Review Gate** remains the primary visible flow and the **Evidence & Audit Inspector** stacks beneath or opens via an explicit side drawer—never hiding `SubmissionState` or the synthetic-data banner.

---

## 4. WCAG 2.1 AA Contrast & Non-Color-Only Encoding

All foreground/background pairings must meet **WCAG 2.1 AA** (`>= 4.5:1` for normal body text; `>= 3.0:1` for large headings `>= 24px` / `>= 18.66px` bold and UI focus/border components):

### Verified Token Pairings

| Pairing | Computed Contrast Ratio | Permitted Usage |
| :--- | :--- | :--- |
| `--bg-parchment` (`#f2ede2`) <-> `--bg-obsidian` (`#151917`) | **15.20 : 1** | Primary prose, headings, obsidian rail text in `#f2ede2` (WCAG AAA). |
| `--bg-parchment-elevated` (`#faf7f0`) <-> `--bg-obsidian` (`#151917`) | **16.59 : 1** | Active draft sheet copy, modal/gate labels, rail headings in `#faf7f0` (WCAG AAA). |
| `--accent-sage` (`#4a6b5b`) on `--bg-parchment` / `--bg-parchment-elevated` | **5.07 : 1** / **5.54 : 1** | Positive status text, `APPROVED` badges, integrity pass text (WCAG AA normal text). |
| `--danger-crimson` (`#9e3b33`) on `--bg-parchment` / `--bg-parchment-elevated` | **5.75 : 1** / **6.28 : 1** | Error alerts, blocked submission banners, reject labels (WCAG AA normal text) and solid crimson pill with `#faf7f0` text (**6.28 : 1**). |
| `--accent-amber` (`#c4883a`) on `--bg-obsidian` (`#151917`) | **5.86 : 1** | Warning indicators on dark rail, and `#151917` text inside amber warning chips on parchment (**5.86 : 1**; do **not** put `--accent-amber` text directly on parchment, where contrast is `2.60:1`–`2.83:1`). |
| `--accent-copper` (`#b8643f`) on `--bg-obsidian` / `--bg-parchment-elevated` | **4.17 : 1** / **3.98 : 1** | UI borders, left accent rules, icons, and large `Instrument Serif` headings (`>= 3.0:1`); pair small body text on parchment with `--bg-obsidian` (`#151917`). |

### Non-Color-Only Rule

Every state badge (`DRAFT`, `IN_REVIEW`, `APPROVED`, `SUBMITTED`, `RECEIPTED`), OCR warning, and guardrail alert **must** convey meaning through **text label + icon/border geometry** in addition to color.

---

## 5. Fact-vs-Conclusion Visual Separation Standard

To uphold `Themis` and `Dike` epistemic boundaries inside the Command Center, **extracted facts** and **legal conclusions** must never appear in indistinguishable prose blocks:

| Dimension | Extracted Record Facts (`Dike` / `Hermes`) | Legal Norms & Conclusions (`Themis` / `Apollō`) |
| :--- | :--- | :--- |
| **Surface & Border** | `--bg-parchment-elevated` (`#faf7f0`) with a neutral `2px` `--bg-obsidian` / muted border | `--bg-parchment` (`#f2ede2`) with a `3px` left accent border in `--accent-copper` (`#b8643f`) |
| **Header Badge** | `RECORD FACT · VERIFIED SOURCE` or `RECORD FACT · OCR UNVERIFIED` (`DM Mono`) | `LEGAL ANALYSIS · DRAFT INFERENCE (PRE-HITL)` (`DM Mono`) |
| **Mandatory Attribution** | Inline `DM Mono` annex & page citation chip (e.g., `Annex A-01 · p. 3`) | Explicit reference to cited statutory norm and dependent fact IDs |
| **Human Gate Affordance** | Reviewers verify OCR / documentary fidelity before approval | Reviewers sign off or reject analytical framing back to `DRAFT` |
