# Owner Direction & Product Discovery Register

> Updated: 2026-11-15 16:53 (America/Monterrey, UTC-06:00)
> Status: working register; confirmed decisions are separated from open questions.
> Scope: capture owner direction discussed in ChatGPT conversations so the LegalTech lab remains the continuity source of truth.

## 1. Product intent

Build an independent LegalTech product for legal practitioners in Nuevo León, Mexico, with an architecture that can later support broader jurisdictions. The product direction discussed so far includes:

- A lawyer-facing digital workspace for managing matters and procedural work.
- A portal/workflow layer for court-related tasks, notices, submissions preparation, and case follow-up.
- Procedural calendar and deadline computation, including non-working days, court calendar exceptions, and service/outage incidents.
- AI-assisted matter intake, document preparation, evidence/record organization, and workflow coordination.
- Auditability, traceability, access control, and secure handling of legal information.
- Modular applications/agents rather than one undifferentiated application.

These are product goals and discovery inputs, not a claim that all capabilities are implemented or legally integrated.

## 2. Two parallel business tracks — preserve both

The owner has stated that these tracks are complementary and must remain active in parallel:

1. **Independent product / startup:** develop and validate a product that can be owned, operated, and commercialized independently.
2. **Institutional relationships / consulting / partnerships:** explore opportunities with institutions, providers, and other legal-sector organizations.

Do not recommend abandoning one track in favor of the other. Evaluate conflicts, dependencies, revenue, data access, procurement, and IP separately.

## 3. Product experience and design direction

Working direction captured from owner discussions:

- Premium, restrained, classical legal identity; references include marble, Themis/Justice, Zeus, and legal symbolism.
- Palette direction: black, white, greys, with orange as a controlled accent.
- Clean, modular, icon-forward interface; avoid a cluttered “everything in one screen” product.
- Keep the legal workflow and the technical orchestration understandable to practitioners.
- Preserve explicit human review and approval for consequential legal actions.

These are design principles, not a finalized brand system. Reconcile them with `docs/DESIGN_SYSTEM.md` before changing implementation tokens.

## 4. Startup tooling shortlist — preliminary, not yet approved

The owner raised a list described as “nine applications for the startup.” The following names have appeared in the conversation so far:

| Mentioned tool | Intended use stated or apparent in the discussion | Status |
| --- | --- | --- |
| “Cloud” (provider/product not yet identified) | Cloud work / development environment; exact product is ambiguous | OPEN — identify exact service |
| Excalidraw | Mind maps and visual architecture | CANDIDATE |
| Remotion | Programmatic video creation | CANDIDATE |
| Mercado Pago | Payments in Mexican pesos / local payment methods | CANDIDATE |
| Stripe | Payments and international / USD flows | CANDIDATE |
| Speakeasy (speakeasy.com) | Raised by owner for evaluation; intended role not yet confirmed | OPEN — evaluate fit |
| Application 7 | Not yet supplied | OPEN |
| Application 8 | Not yet supplied | OPEN |
| Application 9 | Not yet supplied | OPEN |

**Important:** this is not a finalized nine-tool stack. Do not invent the missing tools, assume “Cloud” means Cloudflare or Google Cloud, or integrate/payment-enable any provider until the exact product, account ownership, pricing, regional availability, data flow, and business need are confirmed.

Evaluate each candidate against: product capability, integration surface/API/SDK, security and privacy, Mexico availability, MXN/USD settlement, fees, operational burden, vendor lock-in, and whether an existing tool already covers the need.

## 5. Legal and safety boundaries

The repository's existing hard rules remain in force:

- Synthetic data only in this engineering lab; never add real client names, case numbers, evidence, identifiers, or credentials.
- MockAuthority only; no live court, SAT, Tribunal Virtual, RPP, or other authority submission.
- Mandatory human-in-the-loop approval before any consequential submission flow.
- Do not silently change `main`; owner review and explicit authorization are required.
- Product discovery and architecture planning do not authorize production integrations or processing of real legal matters.

The owner’s broader product ambition must not be confused with current implementation status or permission to connect to live institutional systems.

## 6. Repository identity and project boundaries

- This repository, `legaltech-innovation-lab`, is the active Antigravity engineering workspace located at `~/.gemini/antigravity/scratch/legaltech-innovation-lab` on the owner's MacBook.
- It is the intended continuity and engineering source of truth for this LegalTech initiative.
- `legal-practice-agent` is a separate, earlier focused prototype referenced by the current README; do not replace this monorepo with it.
- `IVAN-ROSALES` is a separate repository/project; do not merge its contents into this lab without a scoped decision.
- Do not include unrelated CAPTOORA, avatar, personal, or client-case material in this repository.

## 7. Current repository handoff observations (2026-11-15)

Observed directly in the MacBook working copy during the continuity review:

- Current branch: `dev/mission-002`.
- Current HEAD at review start: `f70670666b717d799636233e0c97c2c915d652b3`.
- Working tree was clean at review start.
- `main` remains at `119c13d`; owner merge approval remains a separate governance gate.
- Mission 002 has completed M2-00, M2-01, and M2-04 according to the project records. The next planned task is M2-02 (OpenTelemetry tracing); M2-03 (SSE) and M2-05 (synthetic domain packs) remain backlog.
- The immutable 72-hour clock is recorded as starting at `2026-11-15T14:03:47-06:00` and ending at `2026-11-18T14:03:47-06:00`. Do not reset it.
- Metadata drift was found: `PROJECT_STATE.json` still lists `2aaa64a` as head, while the current branch HEAD is newer; `CHECKPOINT.json` references `e70fa25` while the current HEAD is `f706706`. Reconcile these ledgers on the next continuity/checkpoint pass; do not rewrite the immutable clock.
- No Git remote was configured in the local repository at review start. A private GitHub repository with this exact name was not found in the connected account. Publish/sync only after the repository is created and the existing branch history is preserved.

## 8. Next discovery actions

1. Obtain the complete list of nine applications from the owner; resolve the exact identity of “Cloud.”
2. Build a capability matrix and map each tool to a specific product workflow.
3. Identify overlaps with existing integrations, especially payments, developer tooling, diagramming, and media generation.
4. Draft a modular product map (core platform, legal workflow modules, agent services, integrations, billing, analytics, and admin/security).
5. Keep all proposals marked as proposals until the owner confirms them.
6. Reconcile project state/checkpoint metadata before resuming implementation from M2-02.

## 9. GitHub synchronization status

- Private repository created: `https://github.com/ponchogf88/legaltech-innovation-lab`.
- Local `origin` is configured to that repository.
- Initial push is pending: GitHub rejected the push because the current GitHub CLI OAuth authorization does not include the `workflow` scope needed to publish the existing CI workflow file. The repository exists, but do not claim its branches are synchronized until a successful push and remote ref verification are recorded.
