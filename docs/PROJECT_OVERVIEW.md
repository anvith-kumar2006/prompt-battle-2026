# SETU — Project Overview

**SETU — Parent-Connected Rural Student Mobility & Safety Platform**
*Safe Journeys. Connected Families. Accountable Transportation.*

| Item | Value |
|---|---|
| Document | SETU_PROJECT_OVERVIEW.md (v0.1 DRAFT) |
| Companion documents | SETU_PRD.md, SETU_FRD.md, SETU_TRD.md, SETU_REQUIREMENTS_TRACEABILITY.md |
| Date | 13 November 2026 |
| Jurisdiction assumed | India (pilot assumed in Karnataka — see Assumption A-01) |
| Team / timebox | 3 students, ~3-hour hackathon prototype |

> **Labelling convention used in all SETU documents**
> **[VERIFIED]** = checked against a source retrieved while writing; **[REQ]** = project requirement; **[REC]** = technical recommendation; **[ASM]** = assumption; **[FUTURE]** = future possibility; **[VERIFY]** = from general knowledge, not retrieved this session — confirm before relying on it.

---

## 1. The idea in one paragraph

Students in rural and semi-rural areas depend on a small number of government buses. When a bus is cancelled, delayed, or overcrowded, parents have no safe, structured alternative and no visibility into who is carrying their child. SETU lets a parent/guardian arrange an **alternative ride with a verified provider**, **explicitly consent** to each journey, **track it live** (the child needs no smartphone — location comes from the driver's authorised device), confirm **pickup/drop-off with OTP-based handover**, and receive **alerts if the vehicle persistently leaves the expected route**.

## 2. Problem statement

1. Government buses are cancelled, delayed, overcrowded or re-routed.
2. Alternatives are scarce and unverified.
3. Parents do not know whether the child boarded or arrived.
4. Children in standards 1–10 typically have no smartphone.
5. No structured driver/vehicle verification, journey monitoring or incident reporting exists for informal alternatives.

The problem is **not** "find another vehicle". It is **coordinated, consent-based, trackable, accountable** alternative transport.

## 3. Why SETU is not an ordinary ride-hailing app

| Ordinary ride-hailing | SETU |
|---|---|
| Rider is the account holder and decision-maker | **Guardian is the account holder**; minors never self-book |
| Any nearby driver can accept | **Only verified, approved providers/vehicles** are eligible |
| Rider confirms by tapping | **Explicit, recorded guardian consent per journey** |
| Rider has a phone | **Child needs no phone**; tracking is driver-device based |
| Arrival = GPS reached | **Arrival ≠ safe handover**; authorised adult/institution confirms |
| Detour is a billing issue | **Persistent route deviation is a safeguarding event** |
| Surge/price optimisation | Safety, capacity and accountability optimisation |
| Trigger: rider demand | Trigger: **transport disruption** affecting a known route |

## 4. Proposed solution

Two provider categories, both verified before receiving any student trip:

- **A. School-approved transport** — school buses, vans, institution-authorised contractors.
- **B. Registered community transport** — eligible registered autos, private vans, other permitted local providers.

Users: guardians, students (no login needed for minors), institution staff, drivers/providers, SETU administrators/safety administrators.

## 5. Stakeholders

| Stakeholder | Interest |
|---|---|
| Parents/guardians | Safety, visibility, control, affordability |
| Students (minors / adult college) | Reliable, safe travel; adult college students may self-manage subject to institution policy |
| Schools/colleges | Attendance, arrival confirmation, reduced absenteeism, liability |
| School transport operators | Utilisation, approved demand |
| Community providers (autos/vans) | Income, legitimacy |
| SETU safety administrators | Verification, incident response |
| Government transport authority | Disruption data (no API assumed — see §9) |
| Police / emergency services (112) | Escalation target — **no automated integration claimed** |
| Regulators / legal counsel | Permits, child-safety, data-protection compliance |

## 6. Core workflows (summary)

1. **Disruption:** operator/admin records disruption → affected parents notified → parent opens SETU.
2. **Request:** parent picks student, pickup & destination on map, date, time.
3. **Match:** backend filters eligible providers (verified, capacity, proximity, time, route) and ranks them.
4. **Consent:** parent reviews driver/vehicle and approves or rejects. **No assignment before consent.**
5. **Assign:** trip created; driver notified.
6. **Pickup:** driver arrives; authorised person gives pickup OTP; backend validates; trip → IN_PROGRESS.
7. **Track:** driver device posts GPS; parent sees last known location on map.
8. **Safety engine:** deterministic corridor check with accuracy and persistence handling; incident created if warranted.
9. **Drop-off:** drop-off OTP / institution confirmation; trip → COMPLETED; parent notified.

## 7. Technology stack (mandatory, fixed)

| Layer | Choice |
|---|---|
| Frontend | HTML5, CSS3, JavaScript, **TypeScript compiled to browser JS** (single source of truth — no duplicate JS/TS) |
| Backend | Python, Flask, Flask REST APIs; Flask serves the frontend |
| Database | MySQL |
| Maps | Leaflet + OpenStreetMap |
| Location | Browser Geolocation API (prototype, foreground only) |
| Email | Gmail SMTP (prototype) |
| Optional AI | Gemini API (explanatory only; never decision-making) |
| Algorithms | Python matching, geospatial maths; optional OR-Tools later |
| **Excluded** | React, Next.js, Node backend, MongoDB, Firebase, Supabase-as-primary-DB, microservices, Kubernetes, Docker-dependent deployment |

## 8. Safety model

1. **Verified-only supply:** unverified/suspended/expired drivers and vehicles are never matched.
2. **Guardian consent gate:** per-journey, recorded, required before assignment.
3. **Capacity hard limit:** transactional check; never exceed vehicle permitted capacity.
4. **Handover, not just arrival:** OTPs (hashed, expiring, single-use, attempt-limited) and authorised-adult/institution confirmation.
5. **Object-level authorisation:** guardians see only their students; drivers see only assigned trips; tracking only during active trips.
6. **Deterministic deviation detection:** corridor + accuracy + persistence + signal-loss handling; one bad GPS point is never proof of wrongdoing; no automatic "kidnapping" label.
7. **Human-in-the-loop escalation:** safety administrator reviews/escalates. SETU **does not** automatically contact police; 112 escalation is a documented manual procedure unless an authorised integration exists.
8. **Email is secondary.** Urgent production alerts need calls/SMS/authorised channels.
9. **AI never decides** approvals, consent, allocation or emergency severity; all critical flows work without Gemini.
10. **Data minimisation:** minimal student data in emails; location retained only as needed; secrets in environment variables.

## 9. Scope reality (three hours, three students)

### What can genuinely be built (P0)
Parent/provider/admin/institution login; student CRUD; provider + vehicle registration with **admin approval (simulated verification, clearly labelled)**; Leaflet pickup/destination selection; ride request; capacity-aware matching; guardian consent; trip creation; pickup OTP; foreground GPS posting (with a **"simulate drive" button** for demos); simulated route deviation → incident; drop-off OTP; Gmail email notifications.

### Must be simulated or manual in the prototype
- Verification of licences/RC/police clearance (admin clicks "approve"; UI banner: *SIMULATED VERIFICATION*).
- Government bus disruption feed (**no API assumed**; manual admin/operator form).
- Emergency escalation (checklist + "112 escalation recorded manually" button; no integration).
- Background GPS (foreground browser tab only).
- Route geometry (stored polyline / straight-line corridor).

### Not achievable in three hours (P2)
Production background tracking (native driver app), police/112 integration, official transport-authority API, real background verification, payments, SMS/voice alerting, ML demand forecasting, OR-Tools route optimisation, legal compliance sign-off.

> **Candid assessment:** the 14-item MVP in the brief is aggressive for 3 people in 3 hours. The plan in the TRD (§Hackathon plan) uses seeded data, a simulated-drive control and minimal UI so that the end-to-end demo is achievable. If time slips, cut order is: Gemini → demand analytics → shared rides → email templates polish.

## 10. Key external facts (research summary)

- **[VERIFIED]** OpenStreetMap standard tile server (`tile.openstreetmap.org`): must display attribution; must not send no-cache headers; cache per HTTP expiry or ≥7 days; max 2 download threads; heavy use of the OSM-hosted tiles is restricted and may be blocked without notice; the policy lives at `operations.osmfoundation.org/policies/tiles/`. Fine for a small demo; use a commercial/self-hosted tile provider for production.
- **[VERIFIED — secondary sources]** India's DPDP Act 2023 and DPDP Rules 2025 (notified Nov 2025): verifiable parental consent required for processing personal data of children (<18); tracking/behavioural monitoring of children is restricted subject to exemptions; sources indicate a safety-related location-tracking exemption exists and that many obligations commence ~18 months after notification. **Legal review required to confirm applicability of exemptions to SETU.**
- **[VERIFY]** Browser Geolocation needs a secure context (HTTPS, or localhost) and permission; `watchPosition` stops when tab is backgrounded/screen locked on most mobile browsers; Wake Lock only helps foreground.
- **[VERIFY]** Gmail SMTP: `smtp.gmail.com`, port 587 (STARTTLS) or 465 (SSL); requires 2-Step Verification + App Password; consumer accounts have low daily sending limits (commonly cited ~500/day) — confirm in Google's current docs.
- **[VERIFY]** Motor Vehicles Act 1988 / state rules (permits for carrying passengers for hire, school-bus norms), POCSO Act 2012, driver police-verification practices — **legal review necessary before any real deployment.**

## 11. Open questions needing team confirmation

1. Pilot state/district? (affects permits, school-bus rules.)
2. Pricing/payments in MVP? (Assumed: none; fare field informational.)
3. Do community autos legally carry school children for hire in the pilot area? (Assumed: legal review pending; demo uses fictional providers.)
4. Who confirms drop-off for a school: reception staff user or authorised guardian contact? (Assumed: both supported; P0 = institution staff role.)
5. Languages? (Assumed: English P0; Kannada/Hindi labels P1.)

— End of overview —
