

## YOUR ROLE

Act as a Senior Product Manager, Software Architect, Business Analyst, Technical Lead, Cybersecurity Architect, and System Requirements Engineer.

You have extensive experience designing:
- Transportation management systems.
- School and student safety platforms.
- Location-based applications.
- Real-time GPS tracking systems.
- Ride-sharing and vehicle allocation platforms.
- Parent/guardian communication systems.
- AI-powered applications.
- Secure web applications using Python, Flask, and MySQL.

Your task is to understand the complete SETU concept and produce three professional, detailed, implementation-ready software engineering documents:

1. Product Requirements Document (PRD).
2. Functional Requirements Document (FRD).
3. Technical Requirements Document (TRD).

These documents must be comprehensive, technically accurate, internally consistent, and suitable for a real software development team.

Do not start coding yet. First analyse the idea, research relevant technical requirements, identify missing decisions, and prepare the documentation.

---

# PART 1 — COMPLETE PROJECT IDEA

## 1. Project Name

SETU — Parent-Connected Rural Student Mobility & Safety Platform.

Tagline: Safe Journeys. Connected Families. Accountable Transportation.

Project category:
- AI-assisted transportation coordination.
- Rural mobility.
- Student transportation safety.
- Parent-connected journey monitoring.
- Alternative transport management.

## 2. Problem Statement

Students in rural and semi-rural areas frequently depend on government buses and other limited public transportation to reach schools and colleges.

They face:
- Limited frequency of government buses.
- Bus cancellations, delays, route disruptions, and overcrowding.
- Long distances between homes, pickup points, and institutions.
- Lack of reliable information about alternative transport.
- Difficulty coordinating safe alternatives at short notice.
- Parents being unable to confirm whether a child was picked up or reached the destination.
- Children, particularly standards 1–10 students, not having personal smartphones.
- Limited visibility and accountability when a child travels in an alternative vehicle.

The challenge is not only to find another vehicle. The alternative journey must be approved, traceable, capacity-aware, and accountable to the parent or guardian.

## 3. Proposed Solution

SETU provides a coordinated workflow for transport disruption and alternative student journeys.

### Main capabilities

1. Parent/guardian accounts.
2. Student profiles.
3. Transport disruption alerts.
4. Alternative ride requests.
5. Provider discovery.
6. Capacity-aware matching.
7. Guardian approval.
8. Driver assignment.
9. Pickup verification.
10. Journey tracking.
11. Route deviation monitoring.
12. Drop-off verification.
13. Email notifications.

### Provider categories

A. School-approved transportation:
- School buses.
- School-operated vans.
- Institution-authorised transport contractors.

B. Registered community transportation:
- Eligible registered autos.
- Private vans.
- Other locally permitted transport providers.

Both categories must follow appropriate verification and approval workflows.

### What SETU is and is not

SETU is a transportation coordination and student-safety platform.

It is not:
- A replacement for government transport authorities.
- A guarantee that a vehicle will always be available.
- A police dispatch system.
- A substitute for driver verification and safeguarding procedures.
- A production-ready emergency service merely because it can send an email.

## 4. Stakeholders

### Parent/guardian
- Creates account.
- Registers children.
- Requests journeys.
- Approves providers.
- Tracks journeys.
- Receives notifications.

### Student
- Travels without needing a smartphone.
- Is associated with guardian or self-managed account according to age and policy.

### Driver/provider
- Registers.
- Submits documents.
- Receives approval.
- Accepts assignments.
- Shares GPS.
- Completes pickup/drop-off verification.

### School/college
- Verifies student affiliation.
- Coordinates transport information.
- Confirms student arrival where required.

### Administrator/safety coordinator
- Verifies providers.
- Approves vehicles.
- Monitors journeys.
- Reviews incidents.
- Records escalation actions.

## 5. Transport Disruption Workflow

1. Authorised operator or administrator records a bus disruption.
2. SETU identifies affected routes or journeys where possible.
3. Parents receive email notifications.
4. Parent opens SETU.
5. Parent selects alternative journey details.
6. SETU identifies suitable providers.
7. Parent reviews and approves the proposed journey.
8. Driver receives assignment.
9. Journey is tracked.
10. Parent receives completion notification.

Do not assume a government bus API exists. Use authorised manual/operator reporting for the prototype unless a verified integration is implemented.

## 6. Parent Ride Request

The parent selects:
- Student.
- Pickup location.
- Destination.
- Date.
- Required time.

The system should use a map interface.

Recommended:
- Leaflet.
- OpenStreetMap.

The system stores coordinates and displays the selected locations for confirmation.

## 7. Provider Discovery and Matching

Match based on:
- Provider verification.
- Vehicle verification.
- Capacity.
- Pickup proximity.
- Destination compatibility.
- Requested time.
- Provider availability.
- Existing trips.
- Route compatibility.

Never exceed permitted vehicle capacity.

Guardian approval is mandatory for minors.

Shared rides are allowed only where route, time, capacity, and safeguarding requirements are compatible.

## 8. GPS Tracking

The child may not own a smartphone.

Therefore, tracking must use the driver's authorised device.

Flow:
1. Parent approves.
2. Driver receives assignment.
3. Driver reaches pickup.
4. Pickup verification completes.
5. Driver starts journey.
6. Device sends GPS updates.
7. Backend stores location.
8. Parent sees the last reported location on a map.
9. Safety engine monitors route deviations.
10. Drop-off is verified.
11. Parent receives notification.

Use Leaflet and OpenStreetMap for the prototype.

Clearly explain the limitations of browser geolocation and background tracking. Recommend a dedicated mobile application for reliable production tracking.

## 9. Pickup and Drop-Off

Pickup:
- Driver arrives.
- OTP or approved handover is verified.
- Timestamp and location are recorded.
- Parent receives confirmation.

Drop-off:
- Driver reaches destination.
- OTP or authorised adult/institution handover is verified.
- Timestamp and location are recorded.
- Journey is completed.
- Parent receives confirmation.

For younger children, a GPS coordinate alone does not prove safe handover.

## 10. Safety Engine

The safety engine must:
- Validate active trip and assigned driver.
- Receive GPS updates.
- Compare current position with expected route corridor.
- Consider GPS accuracy.
- Tolerate temporary signal loss and legitimate diversions.
- Detect persistent deviations.
- Request a driver explanation where appropriate.
- Notify parent and safety administrator.
- Create an incident record.
- Store last known location and event history.
- Support human review and escalation.

Do not label every deviation as kidnapping.

For India, consider emergency number 112. Real police integration requires authorised arrangements. Email must not be the only emergency channel.

## 11. Email Notifications

Use Gmail SMTP for the prototype.

Events:
- Bus disruption.
- Ride request.
- Provider assignment.
- Guardian consent.
- Pickup.
- Route deviation.
- Incident update.
- Drop-off.

Store credentials in environment variables. Do not commit secrets to GitHub.

## 12. AI Features

Potential capabilities:
- Python-based ride matching.
- Geospatial route deviation detection.
- Demand analysis.
- Optional Gemini natural-language assistant.

Do not call deterministic algorithms machine learning without justification.

Gemini must not independently approve drivers, grant parental consent, or make emergency decisions.

The essential application must work when Gemini is unavailable.

---

# PART 2 — MANDATORY TECHNOLOGY STACK

Frontend:
- HTML5.
- CSS3.
- JavaScript.
- TypeScript.

Backend:
- Python.
- Flask.
- Flask REST APIs.

Database:
- MySQL.

Maps:
- Leaflet.
- OpenStreetMap.

Location:
- Browser Geolocation API for prototype.

Email:
- Gmail SMTP.

Optional AI:
- Gemini API.

Algorithms:
- Python.
- Optional OR-Tools.

Restrictions:
- No React.
- No Next.js.
- No Node.js backend.
- No MongoDB.
- No Firebase.
- No unnecessary microservices.
- No Docker dependency.

TypeScript should compile into browser JavaScript. Flask should serve frontend assets from the same application where practical.

The solution must be lightweight and suitable for three student developers.

---

# PART 3 — DOCUMENT 1: PRODUCT REQUIREMENTS DOCUMENT

Create a professional PRD covering:

1. Document control and version history.
2. Executive summary.
3. Product vision.
4. Product mission.
5. Background and problem statement.
6. Existing problem analysis.
7. Proposed solution.
8. Product goals.
9. Measurable success metrics.
10. Target users and personas.
11. Stakeholder analysis.
12. User pain points.
13. Product scope.
14. In-scope features.
15. Out-of-scope features.
16. MVP definition.
17. Future roadmap.
18. User journeys.
19. High-level workflows.
20. Business rules.
21. User experience requirements.
22. Accessibility requirements.
23. Safety and trust considerations.
24. Privacy considerations.
25. Product dependencies.
26. Risks and mitigation.
27. Assumptions and constraints.
28. Acceptance criteria.
29. Success measurement.
30. Release strategy.

Explain why SETU is different from an ordinary ride-booking application.

Emphasise guardian consent, student safety, rural transportation coordination, and support for children without smartphones.

---

# PART 4 — DOCUMENT 2: FUNCTIONAL REQUIREMENTS DOCUMENT

Create a detailed FRD describing exactly what every feature must do.

For each functional requirement include:

- Requirement ID.
- Feature/module.
- Requirement description.
- Actor.
- Preconditions.
- Trigger.
- Main workflow.
- Alternative workflow.
- Failure conditions.
- Input data.
- Output data.
- Business rules.
- Acceptance criteria.
- Priority (P0, P1, P2).

Organise requirements into these modules:

1. Authentication and authorisation.
2. Parent/guardian management.
3. Student management.
4. Institution management.
5. Provider and driver management.
6. Transport disruption management.
7. Location and map management.
8. Ride request management.
9. Ride matching and allocation.
10. Guardian consent.
11. Trip and journey management.
12. GPS tracking.
13. Route deviation and safety engine.
14. Email notifications.
15. Admin dashboard.
16. AI assistant and analytics.
17. Reporting and history.

For each module, document all relevant functionality.

Also include:

- Complete role-permission matrix.
- Complete use-case list.
- Use-case descriptions.
- Business rules catalogue.
- State transition diagrams for ride requests and trips.
- Error scenarios.
- Validation rules.
- Edge cases.
- Functional acceptance test scenarios.

Make requirements testable and unambiguous.

---

# PART 5 — DOCUMENT 3: TECHNICAL REQUIREMENTS DOCUMENT

Create a detailed technical blueprint covering:

1. System overview.
2. Technical architecture.
3. Technology selection and justification.
4. Frontend architecture.
5. Backend architecture.
6. Flask application structure.
7. MySQL database architecture.
8. Entity relationship diagram.
9. Database tables and fields.
10. Primary and foreign keys.
11. Indexing strategy.
12. Constraints.
13. Database relationships.
14. API architecture.
15. Complete REST API endpoint specification.
16. Request/response examples.
17. HTTP status codes.
18. Authentication mechanism.
19. Role-based access control.
20. Object-level authorisation.
21. GPS data architecture.
22. Map integration.
23. Route deviation algorithm.
24. Ride matching algorithm.
25. Capacity allocation logic.
26. OTP generation and verification.
27. Email notification architecture.
28. Gemini API integration.
29. Error handling.
30. Logging and monitoring.
31. Security architecture.
32. Privacy and data retention.
33. Performance requirements.
34. Scalability considerations.
35. Deployment architecture.
36. Environment variable configuration.
37. GitHub repository structure.
38. Testing strategy.
39. Unit and integration tests.
40. End-to-end tests.
41. Deployment checklist.
42. Known limitations.
43. Future technical improvements.

### Database design

Start with:

- users
- students
- institutions
- drivers
- vehicles
- routes
- trips
- ride_requests
- allocations
- journey_events
- guardian_consents
- incidents

Consider:
- notifications
- otp_challenges
- provider_documents
- audit_logs
- transport_disruptions
- trip_passengers

Explain the purpose and relationships of each table.

Do not create unnecessary tables.

### API documentation

Document endpoints for:
- Authentication.
- Parent and student management.
- Provider registration.
- Provider approval.
- Vehicle management.
- Transport disruptions.
- Ride requests.
- Ride allocation.
- Guardian consent.
- Trip management.
- Pickup and drop-off.
- GPS tracking.
- Route deviation.
- Incident management.
- Notifications.
- Admin operations.

For every endpoint provide:
- HTTP method.
- URL.
- Purpose.
- Required role.
- Authentication requirement.
- Request JSON.
- Response JSON.
- Validation.
- Possible error responses.

### Algorithms

Explain and provide Python-oriented pseudocode for:

1. Provider eligibility filtering.
2. Capacity-aware ride matching.
3. Shared ride grouping.
4. GPS route deviation detection.
5. Pickup OTP validation.
6. Drop-off validation.
7. Incident severity workflow.

### Safety architecture

Explain how to prevent:
- Unauthorised driver access.
- Unauthorised trip access.
- Fake GPS submissions where detectable.
- Invalid or reused OTPs.
- Over-capacity allocation.
- Parent access to another family's student.
- Unauthorised location tracking.
- Unverified provider allocation.

Explain browser GPS limitations and production requirements for background tracking.

---

# PART 6 — DIAGRAMS

Use valid Mermaid syntax.

Include:

1. High-level system architecture.
2. Entity relationship diagram.
3. Parent registration flow.
4. Bus disruption workflow.
5. Alternative ride allocation workflow.
6. Pickup and drop-off workflow.
7. GPS tracking workflow.
8. Route deviation and incident escalation.
9. Authentication and role management.
10. Complete system data flow.

Use readable diagrams and clear names.

---

# PART 7 — WEB RESEARCH AND TECHNICAL VALIDATION

Research current official documentation and reliable technical resources.

Prioritise:
- Flask official documentation.
- MySQL official documentation.
- Leaflet official documentation.
- OpenStreetMap usage policy.
- Browser Geolocation API documentation.
- Google/Gmail SMTP documentation.
- Gemini API documentation.
- OR-Tools documentation.
- Relevant Indian transport and student-safety regulations and official guidance.

Research:

1. Browser GPS limitations.
2. Background tracking requirements.
3. Security requirements for student location data.
4. OTP security practices.
5. Gmail SMTP limits and configuration.
6. Correct OpenStreetMap tile usage.
7. Flask + MySQL deployment requirements.
8. Safeguards for transporting minors in India.
9. Legal and operational approvals for deployment.
10. Limitations of emergency escalation through an application.

Use primary sources wherever possible.

For legal statements:
- Prefer official government sources.
- Identify applicable jurisdiction.
- State when legal review is necessary.
- Do not invent requirements.
- Distinguish binding regulations from recommendations.

Add references with source title, organisation, URL and access date.

Clearly distinguish verified facts, project requirements, recommendations, assumptions and future possibilities.

---

# PART 8 — CONSISTENCY AND TRACEABILITY

The documents must be consistent.

A PRD feature must have corresponding FRD requirements.

Each major FRD requirement must map to technical components in the TRD.

Database fields must support the documented workflows.

API endpoints must support the FRD requirements.

Safety requirements must appear in all relevant documents.

The technology stack must remain consistent.

Create a traceability matrix:

| PRD Goal | FRD Requirement ID | TRD Component | Test Case ID |
|---|---|---|---|

Use requirement IDs such as:

- PRD-GOAL-001
- FR-AUTH-001
- FR-RIDE-001
- FR-SAFE-001
- TR-DB-001
- TR-API-001
- TC-RIDE-001

Also include:
- Assumptions register.
- Risks register.
- Document review checklist.
- Requirements consistency checklist.

---

# PART 9 — THREE-HOUR HACKATHON REALITY

This application will initially be built by THREE students in a THREE-HOUR hackathon.

Separate requirements into:

P0 — Critical MVP.

P1 — Important enhancements.

P2 — Production/future scope.

The MVP must prioritise:

1. Parent registration/login.
2. Student registration.
3. Provider registration and approval.
4. Pickup/destination selection.
5. Ride request.
6. Capacity-aware matching.
7. Parent consent.
8. Driver assignment.
9. Pickup OTP.
10. GPS location updates.
11. Simulated route deviation.
12. Incident alert.
13. Drop-off verification.
14. Parent email notifications.

Explain what can genuinely be completed within three hours and what must be simulated.

Do not claim production-grade background GPS, police integration, government bus API integration, or complete driver verification can be completed in three hours.

---

# PART 10 — REQUIRED OUTPUT FILES

Create five separate Markdown files:

1. SETU_PRD.md
2. SETU_FRD.md
3. SETU_TRD.md
4. SETU_PROJECT_OVERVIEW.md
5. SETU_REQUIREMENTS_TRACEABILITY.md

The project overview must contain:
- Complete idea.
- Problem statement.
- Proposed solution.
- Stakeholders.
- Workflows.
- Technology stack.
- Safety model.
- Project scope.

The traceability document must contain:
- Requirements traceability matrix.
- Assumptions register.
- Risks register.
- Document consistency checklist.

If your environment supports downloadable files, create each file separately and provide working download links.

If you cannot create files, output each document separately in Markdown so I can save them manually.

Do not merge all documents into a short summary.

Do not omit important requirements to reduce length.

---

# PART 11 — WORKING SEQUENCE

Follow this sequence:

STEP 1: Analyse the SETU concept.

STEP 2: Identify ambiguities, missing decisions, risks and assumptions.

STEP 3: Research technical and regulatory areas.

STEP 4: Create the complete PRD.

STEP 5: Create the complete FRD.

STEP 6: Create the complete TRD.

STEP 7: Create the project overview.

STEP 8: Create the requirements traceability document.

STEP 9: Cross-check all documents for consistency.

STEP 10: Provide a final summary explaining:
- What each document contains.
- What assumptions were made.
- What needs confirmation from the team.
- Which features are suitable for the MVP.
- Which features require production-level development.

If a critical decision is missing, ask one concise clarification question before finalising the affected requirement.

For non-critical details, state a reasonable assumption and mark it clearly.

## FINAL QUALITY REQUIREMENT

Write these documents as if they will be reviewed by:
- A professional software architect.
- A product manager.
- A university project evaluator.
- A technical development team.
- A cybersecurity reviewer.

Use professional software engineering terminology, numbered requirements, tables, valid diagrams and testable acceptance criteria.

The result must be detailed enough for a development team to understand exactly what SETU is, what it must do, how it should work and how it can be implemented.

**Do not start application coding. Complete and validate the documentation first.**