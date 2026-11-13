# SETU — Product Requirements Document (PRD)

## 1. Document Control

| Field | Value |
|---|---|
| Product | SETU — Parent-Connected Rural Student Mobility & Safety Platform |
| Version | 0.1 (DRAFT for team review) |
| Date | 13 November 2026 |
| Owner | Product Manager (team lead) |
| Reviewers | Architect, Security reviewer, Project evaluator |
| Status | Draft — awaiting confirmation of items in Traceability §Assumptions |

| Version | Date | Author | Change |
|---|---|---|---|
| 0.1 | 2026-11-13 | Documentation team | Initial full PRD |

Labels: **[VERIFIED] [REQ] [REC] [ASM] [FUTURE] [VERIFY]** as defined in the Overview.

## 2. Executive Summary

SETU enables parents/guardians to arrange **verified, consent-based, trackable alternative transport** for students when government buses are disrupted. Unlike ride-hailing, the guardian is the decision-maker, the child needs no smartphone, handover is verified by OTP and authorised adults, and persistent route deviation raises a safeguarding incident reviewed by humans. The hackathon MVP demonstrates the complete loop end-to-end with simulated verification and foreground GPS.

## 3. Product Vision
Every rural student reaches school and returns home safely, with their family informed at every step, even when the regular bus does not run.

## 4. Product Mission
Connect parents, institutions and verified transport providers through a consent-first, accountable journey platform that works for children without phones.

## 5. Background and Problem Statement
Rural students rely on limited government buses. Cancellations, delays and crowding leave families improvising with unverified transport and no visibility. Parents cannot tell if a child boarded or arrived. See Overview §2.

## 6. Existing Problem Analysis

| # | Problem | Impact | SETU response |
|---|---|---|---|
| 1 | Unexpected cancellations | Missed school, unsafe improvisation | Disruption record + parent alert + alternatives |
| 2 | Delays/disruption | Late arrival, waiting alone | Time-based request, tracking |
| 3 | Overcrowding | Safety risk | Disruption type OVERCROWDED, alternative capacity |
| 4 | No ready alternative | Parent stress | Provider discovery & matching |
| 5 | No boarding/arrival knowledge | Anxiety | OTP pickup/drop-off + notifications |
| 6 | Child has no phone | Traditional apps unusable | Driver-device tracking, guardian-held OTP |
| 7 | Unverified drivers | Safeguarding risk | Approval workflow; unverified never matched |
| 8 | No incident process | Slow response | Deviation engine + incident workflow |

## 7. Proposed Solution
See Overview §4–6. Two provider categories (school-approved, registered community), mandatory verification, guardian consent, OTP handover, live tracking, deviation incidents, email notifications, optional Gemini explainer.

## 8. Product Goals

| ID | Goal |
|---|---|
| PRD-GOAL-001 | Let guardians arrange alternative transport with explicit per-journey consent |
| PRD-GOAL-002 | Ensure only verified, approved drivers/vehicles receive student trips |
| PRD-GOAL-003 | Never exceed vehicle permitted capacity |
| PRD-GOAL-004 | Provide live journey tracking without requiring the child to own a smartphone |
| PRD-GOAL-005 | Verify safe handover at pickup and drop-off (OTP + authorised adult/institution) |
| PRD-GOAL-006 | Detect persistent route deviation and manage incidents with human review |
| PRD-GOAL-007 | Keep parents informed via event-driven notifications |
| PRD-GOAL-008 | Connect transport disruptions to affected families and alternatives |
| PRD-GOAL-009 | Protect student privacy and secure location data |
| PRD-GOAL-010 | Provide intelligent assistance (explanations, demand insight) without delegating critical decisions to AI |

## 9. Measurable Success Metrics

| Metric | Prototype target (demo) | Pilot target [ASM] |
|---|---|---|
| End-to-end flow (register → request → consent → pickup → track → drop-off) completes | 100% on scripted demo | ≥ 95% of requests |
| Median time request → proposal | < 5 s | < 30 s |
| Unverified provider allocated | 0 | 0 (hard invariant) |
| Over-capacity allocations | 0 | 0 (hard invariant) |
| Trips started without valid pickup OTP | 0 | 0 |
| GPS ping → parent map latency | < 10 s (foreground) | < 15 s |
| Deviation incident created within persistence threshold + 10 s | 100% on simulated deviation | ≥ 95% |
| Notification email dispatch attempted within 30 s of event | ≥ 95% | ≥ 95% |
| Parent-reported usefulness (survey) | n/a | ≥ 4/5 |

## 10. Target Users and Personas

| Persona | Description | Needs |
|---|---|---|
| **Lakshmi (Parent)** | Farmer, feature phone/basic smartphone, 2 children (std 4, std 9) | Simple UI, regional language [FUTURE], trust, alerts |
| **Ravi (Pre-university student, 17)** | Has a basic phone | Reliable ride, parent oversight |
| **Meera (College student, 20)** | Adult, owns smartphone | Self-managed account per institution policy |
| **Suresh (Auto driver)** | Registered auto, low digital literacy | Simple assignment screen, one-tap start, fair income |
| **Mrs. Rao (School coordinator)** | Front-office staff | Arrival confirmation, attendance context |
| **Anil (Safety administrator)** | SETU staff | Verification queue, incident console |
| **Transport operator clerk** | Records bus disruptions | Quick disruption entry |

## 11. Stakeholder Analysis
See Overview §5. Influence/interest: Parents (high/high), Institutions (high/high), Regulators (high influence/low direct involvement), Providers (medium/high), Police/112 (high influence/indirect).

## 12. User Pain Points
Uncertainty, unverified drivers, no handover record, no contact trail, fear of being stranded, language barriers, low smartphone ownership among children, unreliable connectivity in rural areas.

## 13. Product Scope
Guardian-driven alternative transport coordination for students, within one pilot region, with verified providers.

## 14. In-Scope Features (by priority)

| Priority | Feature | FRD modules |
|---|---|---|
| P0 | Registration/login/roles | AUTH |
| P0 | Guardian profile, student management, institution link | PAR, STU, INST |
| P0 | Provider/driver/vehicle registration + admin approval (simulated) | PROV, ADM |
| P0 | Pickup/destination map selection, ride request | LOC, RIDE |
| P0 | Capacity-aware matching | MATCH |
| P0 | Guardian consent | CONS |
| P0 | Trip assignment, pickup OTP, start, drop-off OTP, completion | TRIP |
| P0 | GPS submission + parent map | GPS |
| P0 | Simulated deviation → incident | SAFE |
| P0 | Email notifications | NOTIF |
| P1 | Disruption management (manual), affected-parent notification | DISR |
| P1 | Password reset, shared rides, institution arrival confirmation UI, incident acknowledge/resolve console, history/reports, Gemini explainer, authorised handover contacts, driver reason prompt | various |
| P2 | See §15/§17 |

## 15. Out-of-Scope (prototype)
Native/background tracking, police/112 integration, government API integration, real background checks, payments, SMS/voice alerts, ML forecasting, OR-Tools optimisation, multi-guardian per student, multilingual UI, offline mode, ratings/reviews, in-app chat/calling.

## 16. MVP Definition
The 14-step demo: (1) parent registration/login, (2) student registration, (3) provider registration & approval, (4) pickup/destination selection, (5) ride request, (6) capacity-aware matching, (7) parent consent, (8) driver assignment, (9) pickup OTP, (10) GPS updates, (11) simulated deviation, (12) incident alert, (13) drop-off verification, (14) parent email notifications. Priorities are identical in the FRD (P0) and TRD.

## 17. Future Roadmap [FUTURE]

| Phase | Items |
|---|---|
| R1 (post-hackathon) | P1 list; Kannada/Hindi UI; self-hosted OSRM routing; institution portal |
| R2 | Native driver app (Android) with foreground-service background tracking; SMS/voice alerts |
| R3 | Authorised emergency/112 integration (if available), government disruption data integration, document verification APIs, OR-Tools optimisation, demand forecasting |
| R4 | Payments, ratings, multi-region, multi-guardian, audit by third party |

## 18. User Journeys

**J1 Parent requests ride:** disruption email → open SETU → choose student → set pickup/destination on map → date/time → see proposal (driver, vehicle, capacity, ETA) → approve → receive OTP in app → driver arrives → share OTP → track → drop-off confirmation email.
**J2 Driver completes trip:** login → see assigned trip → navigate to pickup → request pickup OTP → start journey → share location → arrive → drop-off OTP → complete.
**J3 Admin handles incident:** alert → open incident → view last location/timeline → acknowledge → contact driver/parent → escalate (manual 112 record) → resolve with notes.
**J4 Provider onboarding:** register → submit docs → admin reviews → approved/rejected → can receive trips.

## 19. High-Level Workflows
Mermaid versions are in the TRD §Diagrams. Summary: Disruption → Notification → Request → Match → Consent → Assign → Pickup OTP → Tracking+Safety → Drop-off OTP → Completion.

## 20. Business Rules (catalogue in FRD §Business Rules; headline rules)

| ID | Rule |
|---|---|
| BR-001 | Minors' journeys require guardian consent before assignment |
| BR-002 | Only APPROVED, unexpired driver+vehicle can be allocated |
| BR-003 | Allocated passengers ≤ vehicle `permitted_capacity` (minus driver, [ASM] one seat reserved) |
| BR-004 | Pickup OTP must validate before IN_PROGRESS |
| BR-005 | Drop-off requires OTP or authorised confirmation; destination proximity alone is insufficient for minors |
| BR-006 | Tracking is visible only to the student's guardian(s), assigned driver, and authorised admins, and only for active trips |
| BR-007 | One GPS ping is never proof of wrongdoing |
| BR-008 | AI may explain but never decide |
| BR-009 | Emails carry minimal data and a secure link |
| BR-010 | SETU never claims automatic police contact |

## 21. User Experience Requirements
Mobile-first responsive UI; ≤ 3 taps to request a ride from dashboard; large touch targets; plain language; clear status chips; persistent "Last updated hh:mm:ss" on tracking map; driver screen minimal (one primary action per state); loading/failure states for GPS and network; confirmation screens before consent.

## 22. Accessibility Requirements
Target WCAG 2.1 AA for core flows [REC]: contrast ≥ 4.5:1, keyboard operability, labelled form fields, ARIA live regions for status changes, map alternatives (text address and coordinates list), no information by colour alone, readable at 200% zoom. Regional-language support [FUTURE].

## 23. Safety and Trust Considerations
Verification gating, consent gate, OTP handover, capacity invariants, deviation engine with persistence/accuracy handling, incident workflow with human review, audit logging, visible "SIMULATED VERIFICATION" banner in prototype, clear statement that SETU does not auto-contact police, driver SOS button [P1], parent "Report concern" button [P1].

## 24. Privacy Considerations
- **[VERIFIED — secondary sources]** India's DPDP Act 2023 / Rules 2025 require verifiable parental consent for children's data and restrict tracking/behavioural monitoring subject to exemptions; many obligations commence in phases (~18 months after Nov 2025 notification). **Legal review required.**
- [REC] Data minimisation: store only necessary child fields (first name, class, institution; no photo/Aadhaar in MVP).
- [REC] Retention: GPS pings 30 days after trip completion (configurable), incidents 1 year, audit 1 year [ASM].
- [REQ] No sale or ad use of data; no tracking outside active trips; emails exclude full names/locations where possible.

## 25. Product Dependencies
Gmail SMTP + App Password; OpenStreetMap tiles (policy-compliant, light use); Gemini API key (optional); HTTPS (or localhost) for Geolocation; MySQL instance; driver device with GPS and browser; human admin availability for approvals/incidents.

## 26. Risks and Mitigation (headline; full register in Traceability doc)

| ID | Risk | Mitigation |
|---|---|---|
| R-01 | Browser GPS stops when tab backgrounded | Foreground tracking only in MVP; keep-awake; native app in R2; show "last seen" staleness |
| R-02 | Fake/inaccurate GPS | Accuracy thresholds, plausibility checks, persistence |
| R-03 | Unsafe or unverified provider | Approval gate, expiry checks, suspension |
| R-04 | Email delays/limits | Email secondary; retry; production uses SMS/calls |
| R-05 | Regulatory non-compliance | Legal review before pilot |
| R-06 | Scope overrun in 3 hours | Seed data, simulation button, strict P0 list |
| R-07 | Over-reliance on AI | Gemini optional, explanation-only |
| R-08 | OSM tile policy breach | Attribution, caching, light usage; alternative provider |

## 27. Assumptions and Constraints
Constraints: mandatory stack, 3 students, 3 hours, no coding of the platform until docs approved. Assumptions: see Traceability §Assumptions (A-01…).

## 28. Acceptance Criteria (product level)

| ID | Criterion |
|---|---|
| PRD-AC-001 | A guardian can register a student and request a ride with map-selected locations |
| PRD-AC-002 | Matching never returns unverified or over-capacity vehicles |
| PRD-AC-003 | No trip is created without recorded guardian consent |
| PRD-AC-004 | Pickup cannot start without valid OTP; reused/expired OTP is rejected |
| PRD-AC-005 | Parent sees latest driver location with timestamp during IN_PROGRESS |
| PRD-AC-006 | A simulated persistent deviation creates an incident and notifies parent and admin |
| PRD-AC-007 | A single outlier GPS point does not create an incident |
| PRD-AC-008 | Drop-off completes only after valid handover; parent receives notification |
| PRD-AC-009 | Another family's parent cannot access the student/trip (HTTP 403/404) |
| PRD-AC-010 | App's critical flows work with Gemini disabled |

## 29. Success Measurement
Prototype: scripted demo checklist + automated test run. Pilot: metrics in §9 via analytics views; incident review; parent survey.

## 30. Release Strategy
1. **Hackathon prototype** (P0, simulated checks, foreground GPS).
2. **Internal alpha** (P1, hardening, legal review start).
3. **Controlled pilot** with one institution and a handful of reviewed providers, human-staffed safety desk, native driver app.
4. **Regional rollout** after regulatory approvals and security audit.

## Appendix A — Why SETU differs from an ordinary ride-booking app
Guardian as principal; consent per journey; verified-only supply; handover verification; child without phone; deviation as safeguarding signal; disruption-triggered demand; institution involvement; human escalation; privacy-by-design for minors.
