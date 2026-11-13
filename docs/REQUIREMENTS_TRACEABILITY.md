# SETU — Requirements Traceability, Assumptions, Risks & Consistency Checklist

Version 0.1 DRAFT · 13 Nov 2026 · Companion to SETU_PRD.md, SETU_FRD.md, SETU_TRD.md, SETU_PROJECT_OVERVIEW.md

## 1. Numbering System

| Prefix | Meaning | Example |
|---|---|---|
| PRD-GOAL-nnn / PRD-AC-nnn | Product goals / acceptance criteria | PRD-GOAL-005 |
| FR-<MODULE>-nnn | Functional requirement (AUTH, PAR, STU, INST, PROV, DISR, LOC, RIDE, MATCH, CONS, TRIP, GPS, SAFE, NOTIF, ADM, AI, RPT) | FR-SAFE-003 |
| BR-nnn | Business rule | BR-005 |
| TR-DB / TR-API / TR-ALG / TR-SEC / TR-NFR | Technical requirement | TR-API-064 |
| TC-<AREA>-nnn | Test case | TC-TRIP-003 |
| A-nn / R-nn | Assumption / risk | A-07 |

Technical component IDs used below: TR-DB (schema), TR-API (endpoints in TRD §15), TR-ALG-1 eligibility, TR-ALG-2 matching, TR-ALG-3 shared rides, TR-ALG-4 deviation, TR-ALG-5 pickup validation, TR-ALG-6 drop-off validation, TR-ALG-7 severity, TR-SEC (security architecture §31), TR-OTP (§26), TR-MAIL (§27), TR-GEM (§28), TR-GPS (§21), TR-MAP (§22).

## 2. Traceability Matrix

| PRD Goal | FRD Requirement ID | TRD Component | Test Case ID | Priority |
|---|---|---|---|---|
| PRD-GOAL-001 Consent-based alternative rides | FR-RIDE-001..005, FR-CONS-001..005, FR-LOC-001..004 | TR-API-040..052; tables ride_requests, ride_request_students, allocations, guardian_consents | TC-RIDE-001, TC-RIDE-002, TC-CONS-001, TC-CONS-002 | P0 |
| PRD-GOAL-002 Verified-only providers | FR-PROV-001..006, FR-MATCH-001, FR-ADM-002 | TR-API-020..029; TR-ALG-1; tables drivers, vehicles, provider_documents | TC-PROV-001, TC-PROV-002, TC-MATCH-001, TC-MATCH-002 | P0 |
| PRD-GOAL-003 Never exceed capacity | FR-MATCH-002, FR-MATCH-003, FR-MATCH-006 | TR-ALG-2 (row lock + recheck at consent); CHECK constraint on vehicles | TC-MATCH-003, TC-MATCH-004 | P0 |
| PRD-GOAL-004 Live tracking without child phone | FR-GPS-001..007, FR-TRIP-002 | TR-GPS; TR-API-080..083; table location_updates | TC-GPS-001..005 | P0 |
| PRD-GOAL-005 Safe handover | FR-TRIP-004, FR-TRIP-006, FR-INST-004, FR-STU-001 | TR-OTP; TR-ALG-5/6; TR-API-062..070; table otp_challenges | TC-TRIP-002..006 | P0 |
| PRD-GOAL-006 Deviation detection & incidents | FR-SAFE-001..011, FR-GPS-006 | TR-ALG-4, TR-ALG-7; TR-API-100..103, 090..092; tables incidents, journey_events | TC-SAFE-001..005 | P0 (core) / P1 (console, escalation, SOS) |
| PRD-GOAL-007 Parent notifications | FR-NOTIF-001..005, FR-PAR-003 | TR-MAIL; TR-API-110..111; table notifications | TC-NOTIF-001 | P0 |
| PRD-GOAL-008 Disruption coordination | FR-DISR-001..004 | TR-API-030..032; tables transport_disruptions, routes | TC-DISR-001 (below) | P1 (demo trigger P0) |
| PRD-GOAL-009 Privacy & security | FR-AUTH-001..007, BR-006, BR-009, BR-011 | TR-SEC; RBAC/object-level §19–20; retention §32 | TC-AUTH-001..004, TC-ADM-001, TC-SEC-001 (below) | P0 |
| PRD-GOAL-010 AI assistance, not decisions | FR-AI-001..004, BR-008, BR-020 | TR-GEM; TR-API-130, 123 | TC-AI-001 | P1 |
| (Supporting) Student/guardian management | FR-PAR-001..004, FR-STU-001..003, FR-INST-001..003 | TR-API-010..015; tables students, institutions, users | TC-STU-001 | P0 |
| (Supporting) Reporting & history | FR-RPT-001..005 | TR-API-041, 060, 100, 122 | TC-RPT-001 (below) | P0 basic / P1 |

Additional test cases referenced above (to be written at test-plan time):

| TC ID | Scenario | Expected |
|---|---|---|
| TC-DISR-001 | Admin records disruption on route R | Only guardians of students mapped to R notified |
| TC-SEC-001 | CSRF-less POST with valid session cookie | 403 |
| TC-SEC-002 | Guardian polls GPS for completed trip | 409/404 |
| TC-SEC-003 | Secrets scan of repository | No credentials committed |
| TC-RPT-001 | Guardian history lists only own trips | Correct subset |

Full functional test list: SETU_FRD.md §H.

## 3. Assumptions Register

| ID | Assumption | Impact if wrong | Needs confirmation by |
|---|---|---|---|
| A-01 | Jurisdiction India; pilot assumed Karnataka (user location Bengaluru) | Permits, school-bus norms differ | Team / legal |
| A-02 | No payments in MVP; fare informational | Scope change | Team |
| A-03 | Drivers use the same session auth as other users (no separate device token) | Security design | Architect |
| A-04 | Route geometry = stored polyline or straight-line corridor (500 m rural / 150 m urban) | Deviation accuracy | Team |
| A-05 | Matching weights 0.40/0.25/0.20/0.15 are tunable defaults | Ranking quality | Team |
| A-06 | Proposal hold 15 min; OTP validity 10 min; max 5 attempts | UX/security trade-off | Security reviewer |
| A-07 | Pickup OTP shown to guardian; drop-off OTP shown to guardian + destination institution staff; driver enters | Handover design | Team / institution |
| A-08 | Driver reserves one seat not counted toward student capacity | Capacity maths | Team |
| A-09 | GPS retention 30 days, incidents/consents/audit 1 year | DPDP alignment | Legal |
| A-10 | Service-area bounding box configured per pilot | Validation | Team |
| A-11 | Email is secondary channel only | Production alerting | Team |
| A-12 | Using Node/npm solely to install the TypeScript compiler is acceptable ("no Node backend" rule not violated) | Hackathon compliance | **Organisers — please confirm** |
| A-13 | English UI only for MVP | Accessibility/reach | Team |
| A-14 | Prototype verification is simulated and labelled | Trust claims | Team |
| A-15 | Disruptions are entered manually (no government API) | Automation | Team |
| A-16 | Session idle timeout 30 min (admin 15) | UX | Security reviewer |
| A-17 | Sibling shared rides allowed only with all guardians' opt-in | Safeguarding | Legal/institution |
| A-18 | Community autos may legally carry school children for hire in pilot area | **Could block pilot** | **Legal review** |

## 4. Risks Register

| ID | Risk | L | I | Mitigation | Owner |
|---|---|---|---|---|---|
| R-01 | Browser GPS suspends in background | H | H | Foreground-only prototype, keep-awake, staleness UI, native app roadmap | Tech lead |
| R-02 | Fake or inaccurate GPS | M | H | Accuracy gating, plausibility checks, persistence; native attestation later | Tech lead |
| R-03 | Unsafe/unverified provider | M | Critical | Approval gate, expiry checks, suspension, audit; real checks before pilot | Product |
| R-04 | Email delay/limits/spam filtering | H | M | In-app mirror, retry, SMS/voice in production | Tech lead |
| R-05 | Regulatory non-compliance (permits, child data) | M | Critical | Legal review; DPDP-aligned consent & minimisation | Product/legal |
| R-06 | 3-hour scope overrun | H | H | Seed data, simulation controls, cut order | Team lead |
| R-07 | Over-reliance on AI | L | M | Gemini optional, explanation-only, fallbacks | Architect |
| R-08 | OSM tile policy breach/blocking | M | M | Attribution, caching, light use, alternate provider | Frontend |
| R-09 | OTP brute force | L | H | Attempt cap, lock, rate limits | Security |
| R-10 | Race condition overbooking | M | H | Row locks + recheck + concurrency test | Backend |
| R-11 | Secret leakage to GitHub | M | H | .env ignored, example file, secret scanning, rotate on leak | All |
| R-12 | False alarm fatigue from deviation alerts | M | M | Corridor/persistence tuning, driver reason, human review | Safety |
| R-13 | Parent over-trusts system ("police auto-called") | M | H | Explicit UI/legal wording; BR-012 | Product |
| R-14 | Unreliable rural connectivity | H | M | Offline queue, batch flush, signal-loss events | Tech lead |
| R-15 | Misuse of location data by insiders | L | H | Role limits, audit logs, access reviews | Security |

## 5. Document Consistency Checklist

| # | Check | Status |
|---|---|---|
| 1 | Every PRD-GOAL maps to ≥1 FR (matrix §2) | ☑ |
| 2 | Every P0 FR maps to a TRD component and ≥1 TC | ☑ (non-listed TCs flagged in §2) |
| 3 | DB fields support workflows (consent, OTP, GPS, incidents, notifications) | ☑ |
| 4 | API endpoints cover FRD modules 1–17 | ☑ |
| 5 | MVP P0 list identical in Overview, PRD §16, FRD priorities, TRD plan | ☑ |
| 6 | Mandatory stack unchanged; excluded technologies absent | ☑ (A-12 pending) |
| 7 | Safety rules appear in PRD §20/23, FRD BR + Module 13, TRD §23–31 | ☑ |
| 8 | Simulated items labelled (verification, disruption feed, route, GPS, escalation) | ☑ |
| 9 | State machines identical between FRD §F and TRD enums | ☑ (ride: SUBMITTED/NO_MATCH/PROPOSED/CONFIRMED/REJECTED_BY_PARENT/EXPIRED/CANCELLED/COMPLETED; trip: SCHEDULED/EN_ROUTE_TO_PICKUP/AT_PICKUP/IN_PROGRESS/ARRIVED/COMPLETED/CANCELLED/ABORTED) |
| 10 | Drop-off handover design identical in FRD (FR-TRIP-006, FR-INST-004) and TRD (TR-API-066..068) | ☑ (FRD patched) |
| 11 | Citations distinguish verified vs unverified | ☑ — see Source Status below |
| 12 | Mermaid diagrams use renderable syntax | ☑ — render-test in a Mermaid viewer before submission |

**Known residual inconsistencies / to-do:**
- PRD §14 uses "Password reset P1" while FRD marks FR-AUTH-004 P1 — consistent. FRD FR-DISR (P1) vs "demo disruption" button (P0) — intentional, noted in both.
- PRD metric "Median time request → proposal < 5 s" vs TRD matching < 2 s — compatible.
- Test cases listed in §2 as "(below)" must be added to the FRD test list when the test plan is formalised.

## 6. Document Review Checklist

☐ Product manager: goals, personas, scope, MVP cut order
☐ Architect: stack compliance, transactions, layering, scalability notes
☐ Security reviewer: OTP policy, RBAC/object checks, CSRF, secrets, GPS spoofing limits
☐ Evaluator: demo script maps to the 14 MVP steps; simulation labels visible
☐ Legal reviewer (before any pilot): DPDP applicability/exemptions, MV Act permits, child-safeguarding duties, driver verification, 112/police procedures
☐ Dev team: DDL, endpoints, pseudocode sufficient to start coding after approval

## 7. Source Status (research honesty)

| Topic | Status |
|---|---|
| OSM tile policy (attribution, no no-cache, ≥7-day caching, ≤2 threads, may block heavy use) | **Retrieved** (OSM wiki pages pointing to the official policy). Re-read canonical page before launch |
| DPDP Act/Rules 2025 children's provisions | **Retrieved from secondary sources only.** Primary text not read; counsel must verify |
| Browser Geolocation/background limits, Gmail SMTP limits, Flask/MySQL/Leaflet/Gemini/OR-Tools docs, NIST OTP guidance | **Not retrieved this session** — from general knowledge; marked [VERIFY] |
| Indian transport/student-safety regulations (MV Act, state school-bus norms, POCSO, driver verification), 112 integration | **Not retrieved** — no regulatory claims made beyond flagging need; **legal review required** |
