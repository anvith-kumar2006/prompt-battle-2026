# SETU — Technical Requirements Document (TRD)

| Field | Value |
|---|---|
| Version | 0.1 DRAFT · 13 Nov 2026 |
| Companion | SETU_PRD.md, SETU_FRD.md, SETU_REQUIREMENTS_TRACEABILITY.md |
| Scope | Hackathon prototype (P0) with P1/P2 extension notes |
| Labels | **[VERIFIED] [REQ] [REC] [ASM] [FUTURE] [VERIFY]** |

> No application code is written here. Pseudocode and DDL-style schemas are blueprints.

---

## 1. System Overview
SETU is a Flask monolith that serves a TypeScript-compiled browser frontend, exposes REST/JSON APIs, persists to MySQL, sends email via Gmail SMTP, renders maps with Leaflet/OSM, collects GPS from the driver's browser, and optionally calls Gemini for explanations.

## 2. Technical Architecture

```mermaid
flowchart LR
  subgraph Browser
    G[Guardian UI<br/>HTML CSS TS-compiled JS<br/>Leaflet]
    D[Driver UI<br/>Geolocation API]
    A[Admin and Institution UI]
  end
  subgraph Flask["Flask monolith"]
    ST[Static and template serving]
    API[REST API blueprints]
    SVC[Service layer<br/>matching, safety engine, OTP, notify]
    BG[Background worker thread<br/>email queue, signal-loss sweeper]
  end
  DB[(MySQL)]
  SMTP[Gmail SMTP]
  OSM[OpenStreetMap tiles]
  GEM[Gemini API optional]
  G --> ST
  G --> API
  D --> API
  A --> API
  G -. tiles .-> OSM
  API --> SVC
  SVC --> DB
  SVC --> BG
  BG --> SMTP
  SVC -. optional .-> GEM
```

## 3. Technology Selection and Justification

| Choice | Justification |
|---|---|
| Flask | Mandated; small, fast to build; blueprints keep modules separate |
| Flask-SQLAlchemy + PyMySQL [REC] | ORM speeds CRUD, parameterised queries prevent SQL injection; PyMySQL pure-Python simplifies Windows laptops |
| MySQL 8 (InnoDB) | Mandated; transactions + row locks needed for capacity |
| Flask-Login or signed sessions + Werkzeug password hashing | Simple, secure server-side session cookies; no JWT complexity |
| Flask-WTF/CSRF or custom header check | CSRF protection for cookie sessions |
| Flask-Limiter | Login/OTP/GPS rate limits (in-memory storage in MVP) |
| TypeScript → `static/js` via `tsc` | Mandated; one source (`/frontend/src/*.ts`), generated JS is a build artefact (git-ignored or committed for demo laptops — decide once) |
| Leaflet + OSM | Mandated; lightweight |
| smtplib / Flask-Mail | Gmail SMTP |
| google-genai SDK or REST (optional) | Gemini explainer |
| Haversine + custom point-to-segment maths [REC] | No heavy GIS dependency; Shapely optional P1 |
| OR-Tools | Optional P2 only |
| pytest | Testing |

No React/Next/Node backend/MongoDB/Firebase/Docker/Kubernetes/microservices. (Node/npm is only a **dev-time** dependency if you install `typescript` via npm; alternatively `pip`-free option: install the standalone `tsc` — flag to team: the "no Node backend" rule is not violated by using Node tooling to compile TS, but confirm with organisers [ASM A-12].)

## 4. Frontend Architecture
- Server-rendered shell templates (Jinja2) per role + static TS-compiled modules; no SPA framework.
- `tsconfig.json`: `target ES2020`, `strict`, `outDir ../backend/app/static/js`, `module ES2020`.
- Modules: `api.ts` (fetch wrapper with CSRF header, error normaliser), `auth.ts`, `map.ts` (Leaflet helpers), `guardian.ts`, `driver.ts` (GPS watcher + sim), `admin.ts`, `types.ts` (shared DTO interfaces), `ui.ts` (toasts, status chips).
- Leaflet loaded from CDN with pinned version + SRI hash [REC]; OSM tile layer with attribution; tile requests use browser defaults (≤ 2 threads acceptable per policy). **[VERIFIED]** policy requires attribution, no no-cache headers, caching ≥ 7 days/HTTP expiry.
- Accessibility: semantic HTML, labels, `aria-live` for status; text fallback for map.
- Polling: guardian map polls every 5 s; `visibilitychange` slows polling when hidden.

## 5. Backend Architecture
Layers: **blueprint (HTTP) → service (business rules) → repository/ORM → MySQL**. Cross-cutting: auth decorators, error handler, audit logger, rate limiter, config.

## 6. Flask Application Structure / 37. Repository Structure

```
setu/
├─ README.md
├─ .gitignore                # .env, __pycache__, node_modules, *.log, uploads/
├─ .env.example              # placeholders only
├─ requirements.txt
├─ package.json              # dev only: typescript
├─ docs/                     # these five documents
├─ db/
│  ├─ schema.sql
│  └─ seed.sql               # demo institutions, guardian, drivers, admin (hashed pw script)
├─ frontend/
│  ├─ tsconfig.json
│  └─ src/*.ts
├─ backend/
│  ├─ wsgi.py
│  ├─ config.py
│  └─ app/
│     ├─ __init__.py         # create_app()
│     ├─ extensions.py
│     ├─ models/             # one file per table group
│     ├─ api/                # auth.py guardians.py students.py providers.py disruptions.py rides.py consent.py trips.py gps.py incidents.py notifications.py admin.py ai.py
│     ├─ services/           # matching.py safety.py otp.py notify.py geo.py audit.py gemini.py
│     ├─ security/           # decorators.py (roles, ownership), csrf.py
│     ├─ templates/          # base + guardian/driver/admin/institution pages
│     └─ static/{css,js,img}
└─ tests/ {unit,integration,e2e}
```

## 7. MySQL Database Architecture
InnoDB, `utf8mb4`, `DATETIME` stored in **UTC**, coordinates `DECIMAL(9,6)`, IDs `BIGINT UNSIGNED AUTO_INCREMENT`. Prototype: schema created from `schema.sql`.

### 8. Entity Relationship Diagram

```mermaid
erDiagram
  users ||--o{ students : "guardian has"
  institutions ||--o{ students : enrols
  institutions ||--o{ users : "staff belong"
  users ||--o| drivers : "is"
  drivers ||--o{ vehicles : operates
  drivers ||--o{ provider_documents : submits
  vehicles ||--o{ provider_documents : has
  users ||--o{ ride_requests : creates
  ride_requests ||--o{ ride_request_students : includes
  students ||--o{ ride_request_students : in
  ride_requests ||--o{ allocations : proposes
  vehicles ||--o{ allocations : reserved
  allocations ||--o| guardian_consents : requires
  allocations ||--o| trips : becomes
  trips ||--o{ trip_passengers : carries
  students ||--o{ trip_passengers : rides
  trips ||--o{ otp_challenges : verifies
  trips ||--o{ location_updates : tracks
  trips ||--o{ journey_events : logs
  trips ||--o{ incidents : raises
  routes ||--o{ transport_disruptions : affected
  transport_disruptions ||--o{ ride_requests : triggers
  users ||--o{ notifications : receives
  users ||--o{ audit_logs : acts
```

### 9–13. Tables, Keys, Constraints (PK = `id` unless noted; FK shown as →)

```
users(id PK, role ENUM('GUARDIAN','STUDENT_ADULT','DRIVER','INSTITUTION_STAFF','ADMIN','SAFETY_ADMIN','OPERATOR') NOT NULL,
  name VARCHAR(100) NOT NULL, email VARCHAR(254) UNIQUE NOT NULL, phone VARCHAR(16) NOT NULL,
  password_hash VARCHAR(255) NOT NULL, status ENUM('ACTIVE','SUSPENDED') DEFAULT 'ACTIVE',
  institution_id → institutions NULL, failed_logins INT DEFAULT 0, locked_until DATETIME NULL,
  created_at, updated_at)

institutions(id PK, name, type ENUM('SCHOOL','PU','COLLEGE'), address, lat DECIMAL(9,6), lng DECIMAL(9,6),
  contact_phone, status ENUM('PENDING','VERIFIED','SUSPENDED'), allows_adult_self_booking BOOL DEFAULT 0, created_at)

students(id PK, guardian_id → users NOT NULL, institution_id → institutions NOT NULL, first_name VARCHAR(60) NOT NULL,
  class_label VARCHAR(30), dob DATE, age_category ENUM('MINOR_PRIMARY','MINOR_SECONDARY','ADULT') NOT NULL,
  status ENUM('ACTIVE','INACTIVE','ARCHIVED') DEFAULT 'ACTIVE', default_route_id → routes NULL, created_at)

drivers(id PK, user_id → users UNIQUE NOT NULL, category ENUM('SCHOOL_APPROVED','COMMUNITY') NOT NULL,
  full_name, licence_no VARCHAR(32) UNIQUE NOT NULL, licence_class, licence_expiry DATE NOT NULL,
  status ENUM('PENDING','APPROVED','REJECTED','SUSPENDED') DEFAULT 'PENDING',
  availability ENUM('AVAILABLE','UNAVAILABLE') DEFAULT 'UNAVAILABLE',
  verification_notes TEXT, verified_by → users NULL, verified_at DATETIME NULL, is_simulated_verification BOOL DEFAULT 1)

vehicles(id PK, driver_id → drivers NOT NULL, reg_no VARCHAR(16) UNIQUE NOT NULL, type ENUM('BUS','VAN','AUTO'),
  permitted_capacity TINYINT UNSIGNED NOT NULL CHECK (permitted_capacity BETWEEN 1 AND 60),
  permit_expiry DATE, insurance_expiry DATE, fitness_expiry DATE,
  base_lat DECIMAL(9,6), base_lng DECIMAL(9,6), service_radius_km DECIMAL(5,2) DEFAULT 10,
  status ENUM('PENDING','APPROVED','REJECTED','SUSPENDED') DEFAULT 'PENDING', verified_by → users NULL, verified_at)

provider_documents(id PK, owner_type ENUM('DRIVER','VEHICLE'), owner_id BIGINT, doc_type ENUM('LICENCE','RC','INSURANCE','PERMIT','FITNESS','POLICE_CLEARANCE'),
  doc_number, expiry_date NULL, file_path NULL, status ENUM('SUBMITTED','ACCEPTED','REJECTED'), reviewed_by → users NULL, created_at)

routes(id PK, name, institution_id → institutions NULL, origin_lat, origin_lng, dest_lat, dest_lng,
  polyline_json JSON NOT NULL,  -- [[lat,lng],...]
  distance_m INT, is_template BOOL DEFAULT 0)

transport_disruptions(id PK, route_id → routes NULL, stop_label VARCHAR(120), type ENUM('CANCELLED','DELAYED','ROUTE_DISRUPTED','OVERCROWDED'),
  starts_at, ends_at NULL, note TEXT, reported_by → users NOT NULL, source ENUM('MANUAL','DEMO') DEFAULT 'MANUAL', created_at)

ride_requests(id PK, guardian_id → users NOT NULL, institution_id → institutions,
  pickup_lat, pickup_lng, pickup_label, dest_lat, dest_lng, dest_label,
  travel_date DATE, pickup_time TIME, shared_ok BOOL DEFAULT 0, disruption_id → transport_disruptions NULL,
  status ENUM('SUBMITTED','NO_MATCH','PROPOSED','CONFIRMED','REJECTED_BY_PARENT','EXPIRED','CANCELLED','COMPLETED'),
  expires_at DATETIME NULL, created_at)

ride_request_students(request_id → ride_requests, student_id → students, PRIMARY KEY(request_id, student_id))

allocations(id PK, request_id → ride_requests, vehicle_id → vehicles, driver_id → drivers, seats_reserved TINYINT,
  score DECIMAL(6,3), window_start DATETIME, window_end DATETIME,
  status ENUM('PROPOSED','CONFIRMED','RELEASED','EXPIRED'), hold_expires_at DATETIME, created_at)

guardian_consents(id PK, allocation_id → allocations UNIQUE, guardian_id → users, status ENUM('PENDING','APPROVED','REJECTED','EXPIRED'),
  consent_text_version VARCHAR(16), decided_at NULL, ip_address VARCHAR(45), user_agent VARCHAR(255), created_at)

trips(id PK, allocation_id → allocations UNIQUE, vehicle_id → vehicles, driver_id → drivers,
  status ENUM('SCHEDULED','EN_ROUTE_TO_PICKUP','AT_PICKUP','IN_PROGRESS','ARRIVED','COMPLETED','CANCELLED','ABORTED'),
  planned_pickup_at DATETIME, pickup_lat, pickup_lng, dest_lat, dest_lng, destination_institution_id → institutions NULL,
  route_polyline_json JSON, corridor_radius_m INT DEFAULT 500, deviation_state JSON NULL,
  pickup_at NULL, pickup_actual_lat NULL, pickup_actual_lng NULL, dropoff_at NULL, dropoff_actual_lat NULL, dropoff_actual_lng NULL,
  handover_method ENUM('OTP','STAFF_CONFIRM','ADMIN_OVERRIDE') NULL, handover_by → users NULL, last_ping_at DATETIME NULL, created_at)

trip_passengers(id PK, trip_id → trips, student_id → students, UNIQUE(trip_id, student_id),
  pickup_confirmed_at NULL, dropoff_confirmed_at NULL)

otp_challenges(id PK, trip_id → trips, purpose ENUM('PICKUP','DROPOFF'), code_hash CHAR(64) NOT NULL, expires_at DATETIME,
  attempts TINYINT DEFAULT 0, max_attempts TINYINT DEFAULT 5, status ENUM('ACTIVE','CONSUMED','EXPIRED','LOCKED','SUPERSEDED'),
  consumed_at NULL, created_at)   -- UNIQUE active per (trip_id,purpose) enforced in service

location_updates(id BIGINT PK, trip_id → trips, driver_id → drivers, lat, lng, accuracy_m FLOAT, speed_mps FLOAT NULL, heading FLOAT NULL,
  client_ts DATETIME(3), server_ts DATETIME(3), dist_from_route_m FLOAT NULL, in_corridor BOOL NULL,
  flags SET('LOW_ACCURACY','CLOCK_SKEW','IMPLAUSIBLE','DUPLICATE'), is_simulated BOOL DEFAULT 0)

journey_events(id PK, trip_id → trips, event_type VARCHAR(40), severity ENUM('INFO','LOW','MEDIUM','HIGH','CRITICAL') DEFAULT 'INFO',
  payload_json JSON, actor_user_id → users NULL, created_at)

incidents(id PK, trip_id → trips, severity ENUM('LOW','MEDIUM','HIGH','CRITICAL'),
  status ENUM('OPEN','ACKNOWLEDGED','ESCALATED','RESOLVED'), cause_hint ENUM('GPS_ERROR_SUSPECTED','SIGNAL_LOSS','TRAFFIC_DIVERSION','ROAD_CLOSURE','UNEXPLAINED_PERSISTENT_DEVIATION','EMERGENCY_REPORTED','OTHER'),
  source ENUM('ENGINE','DRIVER_SOS','GUARDIAN_CONCERN','ADMIN'), last_lat, last_lng, last_seen_at,
  driver_reason VARCHAR(40) NULL, opened_at, acknowledged_by → users NULL, acknowledged_at NULL,
  escalation_note TEXT NULL, escalated_at NULL, resolved_by → users NULL, resolved_at NULL, resolution_type ENUM('FALSE_ALARM','TRAFFIC_OR_ROAD','DRIVER_EXPLAINED','SAFETY_CONCERN_CONFIRMED','EMERGENCY_HANDLED') NULL, resolution_notes TEXT)

notifications(id PK, user_id → users, channel ENUM('EMAIL','IN_APP'), template VARCHAR(40), subject VARCHAR(200), payload_json JSON,
  status ENUM('QUEUED','SENT','FAILED','READ'), attempts TINYINT DEFAULT 0, last_error VARCHAR(255), related_type VARCHAR(30), related_id BIGINT, created_at, sent_at NULL)

audit_logs(id BIGINT PK, actor_user_id → users NULL, action VARCHAR(60), entity_type VARCHAR(30), entity_id BIGINT, detail_json JSON, ip_address VARCHAR(45), created_at)
```

**Table purposes:** `users` identity/roles · `students` minors/adults linked to guardians · `institutions` schools/colleges · `drivers`/`vehicles` provider supply & verification · `provider_documents` evidence metadata · `routes` planned geometry · `transport_disruptions` manual disruption records · `ride_requests` (+`ride_request_students`) demand · `allocations` seat holds/proposals · `guardian_consents` consent evidence · `trips`/`trip_passengers` execution · `otp_challenges` handover secrets · `location_updates` high-volume GPS (separate from `journey_events` to keep the timeline small) · `journey_events` human-readable timeline · `incidents` safeguarding cases · `notifications` outbound + in-app · `audit_logs` accountability. P1 table: `authorised_contacts(id, student_id→students, name, phone, relationship, active)`. Tables deliberately **not** created: ratings, payments, chat.

### 11. Indexing Strategy

| Table | Index | Reason |
|---|---|---|
| users | UNIQUE(email); (role,status) | login; admin filters |
| students | (guardian_id,status) | dashboard |
| vehicles | (status, base_lat, base_lng); UNIQUE(reg_no) | matching prefilter |
| drivers | (status, availability) | matching |
| allocations | (vehicle_id, window_start, window_end); (request_id,status); (status,hold_expires_at) | overlap & expiry sweep |
| trips | (driver_id,status); (status,last_ping_at); (planned_pickup_at) | driver list; signal-loss sweeper |
| location_updates | (trip_id, server_ts DESC) | latest-point query |
| journey_events | (trip_id, created_at) | timeline |
| incidents | (status,severity,opened_at) | admin console |
| notifications | (status,created_at); (user_id,status) | sender queue; inbox |
| otp_challenges | (trip_id,purpose,status) | validation |
| audit_logs | (entity_type,entity_id); (created_at) | review |

## 14. API Architecture
Base `/api/v1`, JSON, UTF-8, ISO-8601 UTC timestamps, consistent envelope:

```json
{"ok": true, "data": {...}}
{"ok": false, "error": {"code": "CAPACITY_EXCEEDED", "message": "…", "details": {...}}}
```
Pagination: `?page=1&page_size=20`. Idempotency-Key header accepted on ride request and consent endpoints [REC].

### 17. HTTP Status Codes
200 OK · 201 Created · 204 No Content · 400 Bad Request (malformed/OTP invalid) · 401 Unauthenticated · 403 Forbidden (role) · 404 Not Found (also for cross-tenant objects) · 409 Conflict (state/capacity/duplicate) · 410 Gone (expired OTP/proposal) · 422 Validation failed · 423 Locked (OTP attempts/account) · 429 Too Many Requests · 500 Server error · 503 dependency unavailable.

### 18. Authentication Mechanism
Server-side session cookie (`Secure` in HTTPS, `HttpOnly`, `SameSite=Lax`), password hash via Werkzeug `generate_password_hash` (scrypt/pbkdf2, salted). CSRF: `X-CSRF-Token` header (token from `/auth/me`) required on POST/PUT/PATCH/DELETE. Login throttling + lockout. No tokens in URLs; email links point to login-gated pages. [ASM A-03] Driver browser uses the same session (no separate device token in MVP).

### 19–20. RBAC and Object-Level Authorisation
Decorators: `@login_required`, `@roles_required(...)`, then **ownership guard** in service layer:

| Check | Rule |
|---|---|
| Student access | `student.guardian_id == current_user.id` (or admin read) |
| Ride request | `request.guardian_id == user.id` |
| Trip read (guardian) | exists `trip_passengers` → student.guardian_id == user.id |
| Trip read/write (driver) | `trip.driver_id == user.driver.id` |
| GPS read | guardian ownership AND trip status ∈ {EN_ROUTE_TO_PICKUP, AT_PICKUP, IN_PROGRESS, ARRIVED} (admin always) |
| GPS write | assigned driver AND same trackable states |
| Institution staff | `trip.destination_institution_id == user.institution_id` |
| Admin/safety | role check + audit |
Unauthorised object access returns **404** to avoid enumeration.

## 15–16. REST API Endpoint Specification

Legend — Role: G guardian · D driver · I institution staff · A admin · S safety admin · O operator · * any authenticated · — public. All non-public endpoints require session auth + CSRF on mutating calls.

| ID | Method & URL | Purpose | Role | Key request fields | Key response | Errors |
|---|---|---|---|---|---|---|
| TR-API-001 | POST `/auth/register` | Register guardian/driver | — | name,email,phone,password,role | 201 user | 409,422 |
| TR-API-002 | POST `/auth/login` | Login | — | email,password | 200 user+csrf | 401,403,429 |
| TR-API-003 | POST `/auth/logout` | Logout | * | — | 204 | 401 |
| TR-API-004 | GET `/auth/me` | Current user + csrf | * | — | user | 401 |
| TR-API-005 | POST `/auth/password-reset/request` | Start reset (P1) | — | email | 202 | 429 |
| TR-API-006 | POST `/auth/password-reset/confirm` | Confirm reset (P1) | — | token,new_password | 204 | 400,410 |
| TR-API-010 | GET/PATCH `/guardians/me` | Profile | G | name,phone | profile | 422 |
| TR-API-011 | GET `/guardians/me/dashboard` | Dashboard aggregates | G | — | students, active_trip, pending_consents | — |
| TR-API-012 | POST `/students` | Create student | G | first_name,class_label,dob,institution_id | 201 student | 422 |
| TR-API-013 | GET `/students` · GET/PATCH/DELETE `/students/{id}` | List/manage own | G | — | student(s) | 404 |
| TR-API-014 | GET `/institutions` | List verified | G,A | — | list | — |
| TR-API-015 | POST/PATCH `/institutions` | Manage (P1) | A | fields | 201 | 422 |
| TR-API-020 | POST `/providers/register` | Create driver profile | D | category,licence_no,licence_expiry,… | 201 PENDING | 409,422 |
| TR-API-021 | GET `/providers/me` | Own status | D | — | status | — |
| TR-API-022 | POST/GET/PATCH `/vehicles` | Vehicle mgmt | D | reg_no,type,capacity,expiries,base | 201 PENDING | 409,422 |
| TR-API-023 | POST `/providers/me/documents` | Doc metadata (files P1) | D | doc_type,doc_number,expiry | 201 | 422 |
| TR-API-024 | PUT `/providers/me/availability` | Toggle availability | D | availability,windows | 200 | 403(not approved) |
| TR-API-025 | GET `/admin/providers?status=PENDING` | Approval queue | A | — | list | 403 |
| TR-API-026 | POST `/admin/providers/{id}/approve` | Approve | A | notes | 200 | 404,409 |
| TR-API-027 | POST `/admin/providers/{id}/reject` | Reject | A | reason | 200 | 422 |
| TR-API-028 | POST `/admin/providers/{id}/suspend` | Suspend (P1) | A | reason | 200 | — |
| TR-API-029 | POST `/admin/vehicles/{id}/approve|reject|suspend` | Vehicle decision | A | notes/reason | 200 | — |
| TR-API-030 | POST `/disruptions` | Record disruption (P1) | O,A | route_id/stop,type,starts_at,note | 201 + affected_count | 422 |
| TR-API-031 | GET `/disruptions` · GET `/disruptions/{id}` | List/view | G(affected),A | — | list | — |
| TR-API-032 | POST `/admin/demo/disruption` | Demo trigger (P0 demo) | A | — | 201 | — |
| TR-API-040 | POST `/ride-requests` | Create + match | G | student_ids,pickup,destination,travel_date,pickup_time,shared_ok | 201 request + proposals[] | 404,422 |
| TR-API-041 | GET `/ride-requests` · `/ride-requests/{id}` | List/view | G | — | request+timeline | 404 |
| TR-API-042 | POST `/ride-requests/{id}/cancel` | Cancel | G | reason | 200 | 409 |
| TR-API-043 | POST `/ride-requests/{id}/rematch` | Re-run matching | G | — | proposals | 409 |
| TR-API-050 | GET `/allocations/{id}` | Proposal detail for consent | G | — | provider/vehicle summary | 404,410 |
| TR-API-051 | POST `/allocations/{id}/consent` | Approve consent | G | decision=APPROVE, text_version | 201 trip | 409,410,403 |
| TR-API-052 | POST `/allocations/{id}/reject` | Reject | G | reason | 200 | 410 |
| TR-API-053 | GET `/consents` | Consent history (P1) | G | — | list | — |
| TR-API-060 | GET `/trips` · `/trips/{id}` | List/detail | G,D,I,A,S | — | trip | 404 |
| TR-API-061 | POST `/trips/{id}/start-route` | Driver heads to pickup | D | — | status EN_ROUTE_TO_PICKUP | 409 |
| TR-API-062 | POST `/trips/{id}/arrive-pickup` | Mark AT_PICKUP; issues pickup OTP | D | lat,lng | AT_PICKUP | 409,422(too far) |
| TR-API-063 | GET `/trips/{id}/otp/pickup` | Guardian views pickup OTP | G | — | `{code, expires_at}` | 404,409 |
| TR-API-064 | POST `/trips/{id}/pickup/verify` | Verify pickup OTP | D | otp,lat,lng | IN_PROGRESS | 400,410,423,409 |
| TR-API-065 | POST `/trips/{id}/arrive-destination` | Mark ARRIVED; issues drop-off OTP | D | lat,lng | ARRIVED | 409 |
| TR-API-066 | GET `/trips/{id}/otp/dropoff` | Receiving party views OTP | G,I | — | code | 403,409 |
| TR-API-067 | POST `/trips/{id}/dropoff/verify` | Verify drop-off OTP | D | otp,lat,lng | COMPLETED | 400,410,423 |
| TR-API-068 | POST `/trips/{id}/dropoff/confirm` | Institution staff handover confirm (no OTP) | I | note | COMPLETED | 403,409 |
| TR-API-069 | POST `/trips/{id}/cancel` | Cancel | G,D,A | reason | 200 | 409 |
| TR-API-070 | POST `/trips/{id}/override-handover` | Admin override | A | purpose,reason | 200 audited | 422 |
| TR-API-080 | POST `/trips/{id}/location` | Submit GPS (single or batch) | D | points[{lat,lng,accuracy,speed,heading,ts}] | 202 `{accepted, flagged}` | 403,409,422,429 |
| TR-API-081 | GET `/trips/{id}/location/latest` | Latest point + staleness | G,A,S | — | point | 404,409 |
| TR-API-082 | GET `/trips/{id}/location/track?since=` | Track polyline | G,A,S | — | points | 404 |
| TR-API-083 | POST `/trips/{id}/simulate` | Demo: sim drive/deviation (dev flag only) | D,A | mode=DRIVE|DEVIATE | 202 | 403(disabled) |
| TR-API-090 | POST `/trips/{id}/deviation-reason` | Driver reason (P1) | D | reason | 200 | 409 |
| TR-API-091 | POST `/trips/{id}/sos` | Driver SOS (P1) | D | note | 201 incident | — |
| TR-API-092 | POST `/trips/{id}/concern` | Guardian concern (P1) | G | note | 201 incident | — |
| TR-API-100 | GET `/incidents` · `/incidents/{id}` | List/detail+timeline | S,A; G(own read-limited) | — | incident | 404 |
| TR-API-101 | POST `/incidents/{id}/acknowledge` | Acknowledge | S | — | ACKNOWLEDGED | 409 |
| TR-API-102 | POST `/incidents/{id}/escalate` | Record manual escalation | S | channel,reference,note | ESCALATED | 422 |
| TR-API-103 | POST `/incidents/{id}/resolve` | Resolve | S | resolution_type,notes | RESOLVED | 422 |
| TR-API-110 | GET `/notifications` · POST `/notifications/{id}/read` | In-app inbox | * | — | list | — |
| TR-API-111 | GET `/admin/notifications?status=FAILED` | Delivery failures | A | — | list | — |
| TR-API-120 | GET `/admin/users` · POST `/admin/users/{id}/suspend` · PATCH `/admin/users/{id}/role` | User mgmt | A | role/status | 200 | 403 |
| TR-API-121 | GET `/admin/trips/live` | Monitor active trips | A,S | — | trips+last_ping | — |
| TR-API-122 | GET `/admin/audit-logs` | Audit | A,S | filters | list | — |
| TR-API-123 | GET `/admin/analytics/demand` | Demand aggregates | A | range | cells/peaks/unmet | — |
| TR-API-130 | POST `/ai/assistant` | Gemini explainer (P1) | G | message,context_ref | `{reply, source:"AI"/"FALLBACK"}` | 429,503→fallback |
| TR-API-140 | GET `/health` | Liveness + DB ping | — | — | 200 | 503 |

### Request/Response Examples

**Create ride request** `POST /api/v1/ride-requests`
```json
{
  "student_ids": [12],
  "pickup": {"lat": 12.971600, "lng": 77.594600, "label": "Village bus stop"},
  "destination": {"lat": 12.982300, "lng": 77.608100, "label": "Govt High School"},
  "travel_date": "2026-11-16",
  "pickup_time": "07:30",
  "shared_ok": false,
  "disruption_id": 3
}
```
`201`:
```json
{"ok": true, "data": {"request_id": 55, "status": "PROPOSED", "expires_at": "2026-11-16T02:15:00Z",
 "proposals": [{"allocation_id": 301, "provider_first_name": "Suresh", "category": "COMMUNITY", "vehicle_type": "VAN",
   "reg_no_masked": "KA01••••1234", "capacity": 8, "seats_reserved": 1, "distance_to_pickup_km": 1.8, "score": 0.82, "verified": true}]}}
```
Errors: `404 STUDENT_NOT_FOUND`, `422 VALIDATION_FAILED` (`details.field`), `200 NO_MATCH` returned as `status:"NO_MATCH"` with empty proposals (not an error).

**Consent** `POST /api/v1/allocations/301/consent`
```json
{"decision": "APPROVE", "consent_text_version": "v1", "acknowledged_tracking": true}
```
`201` → `{"ok":true,"data":{"trip_id":88,"status":"SCHEDULED"}}`; `410 PROPOSAL_EXPIRED`; `409 CAPACITY_EXCEEDED` (race lost).

**Pickup verify** `POST /api/v1/trips/88/pickup/verify`
```json
{"otp": "483920", "lat": 12.9716, "lng": 77.5946}
```
`200` → `{"ok":true,"data":{"status":"IN_PROGRESS","pickup_at":"2026-11-16T02:01:12Z"}}`
`400` → `{"ok":false,"error":{"code":"OTP_INVALID","details":{"attempts_remaining":3}}}` · `410 OTP_EXPIRED` · `423 OTP_LOCKED`.

**GPS submit** `POST /api/v1/trips/88/location`
```json
{"points":[{"lat":12.9731,"lng":77.5962,"accuracy":18.5,"speed":8.2,"heading":42,"ts":"2026-11-16T02:03:05.120Z"}]}
```
`202` → `{"ok":true,"data":{"accepted":1,"flagged":0,"deviation_state":"IN_CORRIDOR"}}` (state hint is not returned to non-driver roles beyond latest-location endpoint).

**Latest location (guardian)** `GET /api/v1/trips/88/location/latest`
```json
{"ok":true,"data":{"lat":12.9731,"lng":77.5962,"accuracy_m":18.5,"server_ts":"2026-11-16T02:03:05Z","age_seconds":4,"stale":false,"trip_status":"IN_PROGRESS"}}
```

**Incident** `GET /api/v1/incidents/9`
```json
{"ok":true,"data":{"id":9,"severity":"MEDIUM","status":"OPEN","cause_hint":"UNEXPLAINED_PERSISTENT_DEVIATION",
 "trip":{"id":88,"vehicle":"KA01••••1234","driver_first_name":"Suresh"},
 "last_location":{"lat":12.99,"lng":77.62,"seen_at":"2026-11-16T02:09:41Z"},
 "timeline":[{"t":"02:06:10Z","event":"OUT_OF_CORRIDOR_POINT"},{"t":"02:08:40Z","event":"DEVIATION_PERSISTENT"},{"t":"02:08:41Z","event":"INCIDENT_OPENED"},{"t":"02:08:45Z","event":"GUARDIAN_NOTIFIED"}]}}
```

### Validation (all endpoints)
Server-side schema validation (e.g., `marshmallow`/`pydantic`-style manual validators), strip/normalise strings, enum whitelist, coordinate bounds, bound batch size (≤ 50), request size ≤ 1 MB, reject unknown fields [REC].

## 21. GPS Data Architecture
- Client: `navigator.geolocation.watchPosition(cb, err, {enableHighAccuracy:true, maximumAge:0, timeout:15000})`; throttle to ≥ 5 s between posts; queue in memory when offline; flush ≤ 50 points oldest-first; show tracking state.
- Server: validate → insert `location_updates` → update `trips.last_ping_at` → run safety engine on newest accurate point(s) → return 202.
- Read path: latest-point query via `(trip_id, server_ts DESC)`; polling 5 s.
- Volume estimate: 1 ping/5 s × 40 min trip ≈ 480 rows/trip; 100 concurrent trips ≈ 20 rows/s — trivial for MySQL.
- Retention: delete `location_updates` 30 days after trip completion (scheduled job; P1) [ASM].

### Limitations of browser-based tracking vs production **[VERIFY — MDN/W3C general knowledge, not retrieved this session]**
| Aspect | Prototype (browser) | Production recommendation |
|---|---|---|
| Secure context | HTTPS or localhost required | HTTPS everywhere |
| Background | Typically suspended when tab hidden/screen locked/browser killed; Wake Lock only helps while foreground | **Dedicated Android driver app** with foreground service + persistent notification, battery-optimisation guidance, fused location provider |
| Accuracy | Device/browser dependent; indoors/urban canyon errors | Fused location + accuracy filtering, map matching |
| Spoofing | Mock-location indistinguishable in browser | Native mock-location detection, Play Integrity, device attestation |
| Transport | HTTP polling | WebSocket/SSE/MQTT, batching, offline queue with persistence |
| Battery/data | Not managed | Adaptive sampling |
| Fleet GPS alternative | — | Approved vehicle-mounted AIS-140-style trackers where mandated [VERIFY regulation] |

## 22. Map Integration
Leaflet map with OSM raster tiles `https://tile.openstreetmap.org/{z}/{x}/{y}.png`, attribution "© OpenStreetMap contributors" **[VERIFIED requirement]**; do not add no-cache headers; no bulk/offline tile download; do not prefetch. Demo traffic only; production must use a hosting provider with a commercial tile plan or self-hosted tiles **[VERIFIED policy: OSM-hosted tiles are for light use and may be blocked]**. Address search (Nominatim) is **P1 and rate-limited** (≤ 1 req/s, identify the app via User-Agent/Referer — [VERIFY current Nominatim policy]); MVP uses pin-drop with manual label.

## 23. Route Deviation Algorithm (pseudocode)

Config (env/db): `CORRIDOR_RADIUS_M=500`, `MAX_ACCURACY_M=100`, `PERSIST_PINGS=3`, `PERSIST_SECONDS=120` (demo 20), `PERSIST_DISTANCE_M=2000`, `SIGNAL_LOSS_SECONDS=90`, `SIGNAL_LOSS_ESCALATE_S=300`, `MAX_SPEED_KMH=120`, `CLOCK_SKEW_S=120`.

```python
def process_ping(trip, ping):
    flags = validate_ping(trip, ping)            # clock skew, implausible jump, duplicate
    save(ping, flags)
    trip.last_ping_at = now()
    if ping.accuracy_m > MAX_ACCURACY_M or 'IMPLAUSIBLE' in flags:
        log_event(trip, 'LOW_QUALITY_PING'); return        # never counted as evidence
    d = distance_to_polyline_m(ping.lat, ping.lng, trip.polyline)   # min point-to-segment
    ping.dist_from_route_m, ping.in_corridor = d, d <= trip.corridor_radius_m
    st = load_deviation_state(trip)              # {out_count, first_out_ts, max_dist, active_incident_id}
    if ping.in_corridor:
        if st.out_count > 0: log_event(trip,'DEVIATION_CLEARED')
        reset(st); return
    # outside corridor
    st.out_count += 1; st.first_out_ts = st.first_out_ts or ping.server_ts
    st.max_dist = max(st.max_dist, d)
    span = ping.server_ts - st.first_out_ts
    persistent = st.out_count >= PERSIST_PINGS and (span >= PERSIST_SECONDS or st.max_dist >= PERSIST_DISTANCE_M)
    if persistent and not st.active_incident_id:
        inc = open_incident(trip, severity='MEDIUM', cause_hint='UNEXPLAINED_PERSISTENT_DEVIATION', last=ping)
        notify_guardian(trip, 'ROUTE_DEVIATION'); notify_safety_admins(inc)
        request_driver_reason(trip)                      # P1
        st.active_incident_id = inc.id
    elif st.active_incident_id:
        maybe_escalate_severity(inc, st, span)           # see §Incident severity
    save(st)

def distance_to_polyline_m(lat, lon, poly):
    # equirectangular projection around the point; min over segments of point-to-segment distance
    ...
```

Signal-loss sweeper (every 30 s): for trips `IN_PROGRESS` where `now − last_ping_at > 90 s` log `SIGNAL_LOST` (LOW); `> 300 s` open MEDIUM incident `SIGNAL_LOSS`; resolves automatically as `SIGNAL_RESTORED` event when pings resume (incident still requires human closure).

## 24–25. Ride Matching, Capacity Allocation

**1. Provider eligibility filtering**
```python
def eligible_vehicles(req, day, t_start, t_end):
    q = vehicles JOIN drivers WHERE drivers.status='APPROVED' AND vehicles.status='APPROVED'
        AND drivers.availability='AVAILABLE'
        AND drivers.licence_expiry >= day AND vehicles.permit_expiry >= day
        AND vehicles.insurance_expiry >= day AND vehicles.fitness_expiry >= day
    return [v for v in q if haversine_km(v.base, req.pickup) <= v.service_radius_km]
```

**2. Capacity-aware matching (transactional)**
```python
def match(req):
    need = len(req.students); window = (req.pickup_time-15m, req.pickup_time+est_duration+15m)
    cands = []
    for v in eligible_vehicles(req,...):
        with tx():                                   # per candidate evaluation
            lock vehicle row (SELECT ... FOR UPDATE)
            used = sum(a.seats_reserved for a in allocations
                       if a.vehicle_id==v.id and a.status in ('PROPOSED','CONFIRMED') and overlaps(a.window, window)
                       and not shared_compatible(a, req))
            remaining = v.permitted_capacity - used
            if remaining >= need and no_trip_conflict(v, window): cands.append(score(v, req, remaining))
    top = sorted(cands, reverse=True)[:3]
    for c in top[:1]: create_allocation(PROPOSED, seats=need, hold=15min)   # hold first choice; others shown after reject
    return top
# score = 0.40*prox + 0.25*timefit + 0.20*capfit + 0.15*category ; prox = 1 - d/radius
```
Defence in depth: after consent, **re-check** inside one transaction (`FOR UPDATE` on vehicle) and compare against `permitted_capacity`; DB `CHECK` on column bounds; unit test with threads.

**3. Shared ride grouping (P1)**
```python
def group_requests(pending, vehicle):
    pending.sort(key=pickup_time)
    group=[pending[0]]
    for r in pending[1:]:
        if all(haversine(r.pickup, g.pickup)<=1.5 and haversine(r.dest, g.dest)<=1.0
               and abs(r.time-g.time)<=15m and r.shared_ok and g.shared_ok
               and r.institution==g.institution for g in group) \
           and seats(group)+seats(r) <= vehicle.remaining:
            group.append(r)
    return group      # each guardian still consents separately; trip created only when all consent
```

## 26. OTP Generation and Verification

Practices **[REC — aligned with common OTP guidance; [VERIFY] against current NIST SP 800-63B before production]**: CSPRNG, short expiry, single use, attempt limit, rate limiting, hashed storage, no logging of codes, constant-time compare, supersede previous codes.

```python
def issue_otp(trip, purpose, recipient_role):
    supersede_active(trip, purpose)
    code = f"{secrets.randbelow(10**6):06d}"
    ch = OtpChallenge(trip=trip, purpose=purpose, expires_at=now()+10min, max_attempts=5, status='ACTIVE')
    ch.code_hash = hmac_sha256(OTP_PEPPER, f"{ch.id}:{code}")   # id assigned before hashing (flush)
    save(ch); return code            # code shown only to authorised viewer endpoint; never logged/emailed by default

def verify_otp(trip, purpose, submitted, actor):
    with tx():
        ch = select ... FOR UPDATE where trip, purpose, status='ACTIVE'
        if not ch: raise Gone/Invalid
        if now() > ch.expires_at: ch.status='EXPIRED'; raise OtpExpired(410)
        if ch.attempts >= ch.max_attempts: ch.status='LOCKED'; raise OtpLocked(423)
        ch.attempts += 1
        ok = hmac.compare_digest(ch.code_hash, hmac_sha256(OTP_PEPPER, f"{ch.id}:{submitted}"))
        if not ok: raise OtpInvalid(400, remaining=ch.max_attempts-ch.attempts)   # locks at limit
        ch.status='CONSUMED'; ch.consumed_at=now(); return True
```
Note: 6-digit space is small → attempt cap + per-trip rate limit + lockout are the real protection. Where the code is shown: **pickup** → guardian (and authorised contact P1); **drop-off** → guardian and destination institution staff. Driver enters codes. [ASM A-07]

**5. Pickup validation:** trip `AT_PICKUP` ∧ driver is assigned ∧ driver coordinates ≤ 300 m of pickup (else 422 unless ADMIN override) ∧ OTP valid → set `IN_PROGRESS`, `pickup_at`, actual coords, `trip_passengers.pickup_confirmed_at`, event `PICKUP_VERIFIED`, email guardian.

**6. Drop-off validation:**
```python
def complete_dropoff(trip, actor, method, otp=None, coords=None):
    assert trip.status == 'ARRIVED'
    if any(p.student.age_category != 'ADULT' for p in trip.passengers):
        assert method in ('OTP','STAFF_CONFIRM','ADMIN_OVERRIDE')     # proximity alone never sufficient
    if method=='OTP': verify_otp(trip,'DROPOFF',otp,actor); assert actor.is_assigned_driver
    elif method=='STAFF_CONFIRM': assert actor.role=='INSTITUTION_STAFF' and actor.institution_id==trip.destination_institution_id
    elif method=='ADMIN_OVERRIDE': require_reason(); audit()
    trip.status='COMPLETED'; set dropoff_at, coords, handover_method, handover_by
    release capacity; end tracking visibility; notify guardian
```

## 7. Incident Severity Workflow (algorithm)
```python
def maybe_escalate_severity(inc, st, span):
    if inc.severity=='MEDIUM' and (span >= 600 and not inc.driver_reason or st.max_dist >= 5000):
        inc.severity='HIGH'; add_event('SEVERITY_RAISED_HIGH'); notify_admins_urgent(inc)   # production: call/SMS
# CRITICAL is only set by SAFETY_ADMIN manually. Driver SOS -> HIGH; guardian concern -> MEDIUM.
# Escalation (POST /incidents/{id}/escalate) records: channel(e.g. 'MANUAL_112'), reference, note, by, at.
# SETU never places a call or message to police by itself.
```

## 27. Email Notification Architecture
`notify(event, user, payload)` → insert `notifications` (QUEUED + IN_APP) → background worker (thread started in `create_app`, polls every 2 s) sends via `smtplib.SMTP('smtp.gmail.com',587)`+STARTTLS (or SSL 465), login with `SMTP_USER`/`SMTP_APP_PASSWORD` from env; retry 3× (1 s, 5 s, 30 s); mark SENT/FAILED. Templates are Jinja2 plain text + minimal HTML; links `{BASE_URL}/trips/{id}`; **no OTPs, no coordinates, no full child names** in emails [REC]. Gmail constraints **[VERIFY]**: requires 2-Step Verification + App Password; low daily send limits on consumer accounts; Google may throttle/flag; unsuitable as sole emergency channel — use SMS/voice and staffed escalation in production. Failure never blocks core transaction (BR-020).

## 28. Gemini API Integration
Server-side only (key in env). Endpoint `/ai/assistant` builds a prompt from: fixed system instruction (explain only; never approve/consent/allocate/assess emergency; say "contact the safety desk/112 for emergencies"), the guardian's own minimal structured context (status strings, not coordinates), user message ≤ 500 chars; input sanitised; output length-capped, labelled AI-generated; 8 s timeout; on error/timeout/no key → static fallback text keyed by status. Model name via `GEMINI_MODEL` env [VERIFY current model names in Gemini docs]. No student names or exact coordinates sent [REC]. Per-user rate limit 20/hour.

## 29. Error Handling
Central `@app.errorhandler`: map domain exceptions (`ValidationError→422`, `NotFound→404`, `Forbidden→403`, `Conflict→409`, `Gone→410`, `Locked→423`, `Dependency→503`) to the JSON envelope; unexpected exceptions → 500 with correlation id, details logged not returned. Client `api.ts` surfaces `error.code` to friendly messages.

## 30. Logging and Monitoring
Python `logging` JSON lines to file + console: request id, user id (not PII), route, status, latency. Never log passwords, OTPs, SMTP/API secrets, full coordinates for non-incident events at INFO. Audit logs in DB for privileged actions. `/health` endpoint. Admin "failed notifications" and "stale trips" panels. [FUTURE] Prometheus/Sentry.

## 31. Security Architecture

| Threat | Control |
|---|---|
| Unauthorised driver access | Auth + role + driver status APPROVED; `trip.driver_id` ownership; suspended driver sessions invalidated |
| Unauthorised trip access | Object-level guards; 404 on foreign objects |
| Fake GPS (detectable) | Server timestamps authoritative; accuracy gating; speed/teleport plausibility; clock-skew flag; duplicate suppression; assigned-driver-only; geofence sanity vs pickup at start; [FUTURE] native mock-location detection, attestation |
| Invalid/reused OTP | Single-use, expiry, attempts, lock, HMAC hash, supersede |
| Over-capacity | Row lock + re-check at consent + CHECK constraints + tests |
| Cross-family student access | Ownership checks on every student/request/trip endpoint |
| Unauthorised tracking | Tracking visible only in trackable states to owning guardian/assigned driver/admins; no access after completion except admin history |
| Unverified provider allocation | Matching filter + trip-creation re-check + status guard |
| OWASP Top-10 | Parameterised ORM queries, Jinja autoescape, CSRF token, secure cookies, rate limiting, security headers (CSP restricting scripts to self + pinned Leaflet CDN, `X-Content-Type-Options`, `Referrer-Policy`, `frame-ancestors 'none'`), dependency pinning, no debug mode in demo-public deployment |
| Secrets | `.env` never committed; `.gitignore`; `.env.example`; rotate leaked Gmail App Password immediately; GitHub secret scanning |
| Data at rest/in transit | HTTPS; MySQL least-privilege user; encrypted backups [P1]; file uploads outside web root, type/size checked, AV scan [P2] |
| Insider abuse | Audit logs; admin actions require reason; least privilege roles |

## 32. Privacy and Data Retention
**[VERIFIED — secondary sources]** DPDP Act 2023 + DPDP Rules 2025 (notified Nov 2025): verifiable parental consent for under-18 data; restrictions on tracking/behavioural monitoring of children with exemptions (sources indicate a safety-related location exemption); phased commencement (children's-data obligations expected ~18 months after notification); 72-hour breach reporting. **Legal review required — SETU must not assume an exemption applies.** [REC] Controls: purpose-limited data; guardian consent text versions stored; minimal fields; no ads/analytics trackers; GPS retention 30 days post-trip, incidents/consents/audit 1 year (configurable) [ASM]; deletion/export request path [P2]; breach response plan [P2]; hide student last names/photos in MVP.

## 33. Performance Requirements
p95 API < 500 ms at 50 concurrent users on a laptop; GPS ingest < 200 ms; matching < 2 s for ≤ 200 vehicles; map refresh ≤ 5 s; email dispatch attempt ≤ 30 s.

## 34. Scalability Considerations
Monolith is adequate for prototype/pilot. Later: Gunicorn workers, MySQL read replica/partition `location_updates` by month, Redis for rate limits/queue, SSE/WebSocket, Celery/RQ for jobs, OR-Tools/OSRM for routing. Keep services behind clean interfaces. (No microservices now.)

## 35. Deployment Architecture
Prototype: single laptop/VM, `flask run` (dev) or `waitress`/`gunicorn`; MySQL local; ngrok/Cloudflare Tunnel **only if** HTTPS phone testing needed (Geolocation requires secure context; `localhost` works for the same machine). Production: reverse proxy (Nginx) with TLS, Gunicorn, managed MySQL, secrets manager, backups, monitoring. No Docker dependency required.

## 36. Environment Variables (`.env.example`)
```
FLASK_ENV=development
SECRET_KEY=change-me
BASE_URL=http://localhost:5000
DATABASE_URL=mysql+pymysql://setu_user:CHANGE_ME@localhost:3306/setu?charset=utf8mb4
OTP_PEPPER=change-me-long-random
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-gmail@gmail.com
SMTP_APP_PASSWORD=your-16-char-app-password
MAIL_FROM_NAME=SETU
GEMINI_API_KEY=
GEMINI_MODEL=
ENABLE_SIMULATION=true
CORRIDOR_RADIUS_M=500
PERSIST_SECONDS=20
PERSIST_PINGS=3
MAX_ACCURACY_M=100
SERVICE_AREA_BBOX=12.80,77.40,13.20,77.80
SESSION_IDLE_MINUTES=30
```

## 38–40. Testing Strategy
| Level | Scope | Tools |
|---|---|---|
| Unit | geo distance, deviation state machine, OTP, capacity maths, age category, validators | pytest |
| Integration | API + MySQL test DB: auth/ownership, matching/consent/trip lifecycle, GPS ingest, incident flow, email failure | pytest + Flask test client |
| Concurrency | two threads booking last seat | pytest threads |
| Security | role/object access matrix, CSRF, rate limits, OTP lockout | pytest |
| End-to-end | scripted demo run (manual checklist for hackathon; Playwright optional P1) | manual / Playwright |
| Accessibility | axe-core spot checks | browser tool |

Test-case IDs: see FRD §H and Traceability file (TC-AUTH/STU/PROV/LOC/RIDE/MATCH/CONS/TRIP/GPS/SAFE/NOTIF/AI/ADM).

## 41. Deployment Checklist
☐ `.env` created locally, not committed ☐ MySQL schema + seed loaded ☐ Admin password changed ☐ `ENABLE_SIMULATION` set intentionally ☐ SMTP App Password tested ☐ TS compiled (`tsc`) and `static/js` present ☐ OSM attribution visible ☐ HTTPS for phone GPS ☐ Demo data labelled fictional ☐ "SIMULATED VERIFICATION" banner visible ☐ Debug off for shared URLs ☐ Dry-run of 14-step demo.

## 42. Known Limitations
Foreground-only GPS; simulated verification; manual disruptions; no police/112 integration; straight-line/stored routes; email-only alerts; polling not push; in-memory rate limiting; single-process background threads (lost on restart); no real document validation; OSM tile policy limits scale; legal compliance not assessed.

## 43. Future Technical Improvements
Native Android driver app; WebSocket/SSE; OSRM routing & map matching; OR-Tools; SMS/voice (authorised gateway); DigiLocker/Vahan/Sarathi-type verification **[FUTURE, subject to availability/authorisation]**; field-level encryption; MFA for admins; Redis/Celery; ML demand forecasting.

---

## Hackathon Reality Plan (3 members × 3 hours)

| Time | A: Backend/DB | B: Frontend (TS/Leaflet) | C: Safety/Integration |
|---|---|---|---|
| 0:00–0:20 | schema.sql, seed, app skeleton, auth | TS config, base templates, api.ts | email service, `.env`, geo utils |
| 0:20–1:10 | students, providers, approval, ride request + matching | guardian dashboard, student form, map picker, provider form | OTP service, trip state machine |
| 1:10–2:00 | consent, trips, pickup/drop-off APIs | consent screen, driver trip screen, parent tracking map | GPS ingest, deviation engine, incident, notifications |
| 2:00–2:35 | admin queue/incident APIs | admin pages, simulate buttons | tests of OTP/capacity/deviation |
| 2:35–3:00 | Integration, bug fixes, demo dry-run, README, slides | | |

Cut order if behind: Gemini → analytics → shared rides → password reset → disruption UI (use demo-trigger button). **Must be simulated:** verification, disruption feed, route geometry, background GPS, escalation.

## Diagrams

### D1 High-level architecture — see §2.
### D2 ERD — see §8.

### D3 Parent registration flow
```mermaid
sequenceDiagram
  actor P as Parent
  participant UI as Browser UI
  participant API as Flask API
  participant DB as MySQL
  participant M as Mail worker
  P->>UI: Fill registration form
  UI->>API: POST /auth/register
  API->>API: Validate and hash password
  API->>DB: Insert user GUARDIAN
  API->>M: Queue welcome email
  API-->>UI: 201 created
  P->>UI: Login then add student
  UI->>API: POST /students
  API->>DB: Insert student linked to guardian
  API-->>UI: 201 student
```

### D4 Bus disruption workflow
```mermaid
flowchart TD
  A[Operator or Admin records disruption] --> B[Validate and save disruption]
  B --> C[Find affected students by route or stop proximity]
  C --> D[Resolve guardians]
  D --> E[Queue email and in-app notifications]
  E --> F[Parent opens SETU]
  F --> G[Create alternative ride request]
```

### D5 Alternative ride allocation
```mermaid
flowchart TD
  R[Ride request submitted] --> V[Validate student ownership and locations]
  V --> F[Filter eligible providers]
  F --> C{Capacity and time OK}
  C -- No --> N[Status NO_MATCH]
  C -- Yes --> S[Rank candidates]
  S --> H[Hold seats 15 min and status PROPOSED]
  H --> P[Parent reviews provider and vehicle]
  P -- Approve --> T[Recheck capacity in transaction then create trip]
  P -- Reject --> X[Release seats and offer next or end]
  P -- Timeout --> E[Status EXPIRED and release seats]
  T --> D[Notify driver and parent]
```

### D6 Pickup and drop-off workflow
```mermaid
sequenceDiagram
  actor Dr as Driver
  actor Pa as Parent or authorised person
  actor In as Institution staff
  participant API as Flask API
  Dr->>API: arrive-pickup with location
  API-->>Pa: Pickup OTP visible in app
  Pa->>Dr: Tell OTP in person
  Dr->>API: pickup/verify with OTP
  API->>API: Validate hash expiry attempts
  API-->>Dr: IN_PROGRESS
  API-->>Pa: Email pickup confirmed
  Dr->>API: arrive-destination
  API-->>In: Drop-off OTP visible to staff
  In->>Dr: Tell OTP or confirm handover
  Dr->>API: dropoff/verify or Staff dropoff/confirm
  API-->>Pa: Email drop-off confirmed
```

### D7 GPS tracking workflow
```mermaid
sequenceDiagram
  participant D as Driver browser
  participant API as Flask API
  participant DB as MySQL
  participant G as Guardian browser
  loop every 5 seconds while trackable
    D->>API: POST location
    API->>API: Validate driver trip state and point
    API->>DB: Insert location update
    API->>API: Run safety engine
  end
  loop every 5 seconds
    G->>API: GET location latest
    API->>DB: Read latest point
    API-->>G: Position with age and stale flag
  end
```

### D8 Route deviation and incident escalation
```mermaid
flowchart TD
  P[GPS point received] --> Q{Accuracy within limit}
  Q -- No --> L[Store as low quality and ignore for deviation]
  Q -- Yes --> C{Inside corridor}
  C -- Yes --> R[Reset deviation state]
  C -- No --> K[Increment out count]
  K --> T{Persistent by count and time or distance}
  T -- No --> W[Keep watching]
  T -- Yes --> I[Open incident MEDIUM]
  I --> N[Notify guardian and safety admin]
  N --> A[Safety admin acknowledges]
  A --> E{Credible concern}
  E -- Yes --> M[Admin records manual escalation e.g. 112]
  E -- No --> Z[Resolve with reason]
  M --> Z
```

### D9 Authentication and role management
```mermaid
flowchart LR
  U[User submits credentials] --> L[POST auth login]
  L --> V{Valid and active}
  V -- No --> F[401 or 403 or 429]
  V -- Yes --> S[Create session cookie and CSRF token]
  S --> RB{Role}
  RB --> G[Guardian pages]
  RB --> D[Driver pages]
  RB --> I[Institution pages]
  RB --> A[Admin and Safety pages]
  G & D & I & A --> O[Object ownership check on every request]
```

### D10 Complete system data flow
```mermaid
flowchart TD
  Parent[Guardian] -->|requests consents| API
  Driver[Driver device] -->|GPS OTP status| API
  Admin[Admin and Safety] -->|approvals incidents| API
  Staff[Institution staff] -->|handover| API
  API --> DB[(MySQL)]
  API -->|events| Queue[Notification queue]
  Queue --> Gmail[Gmail SMTP]
  Gmail --> Parent
  API -->|safe context only| Gemini[Gemini optional]
  Parent -->|map tiles| OSM[OpenStreetMap]
```

## References and Source Status

| # | Title | Organisation | URL | Accessed | Status |
|---|---|---|---|---|---|
| 1 | Tile Usage Policy | OpenStreetMap Foundation | https://operations.osmfoundation.org/policies/tiles/ (referenced from wiki.openstreetmap.org/wiki/Tile_usage_policy) | 13 Nov 2026 | Retrieved via wiki summary/translations — **re-read the canonical page before launch** |
| 2 | DPDP Rules 2025 explainers (Mondaq; DSCI; Lakshmikumaran & Sridharan; ORF; Bar & Bench) | Various law firms/think tanks | e.g. https://www.mondaq.com/india/data-protection/1832690/childrens-data-protection-under-indias-dpdp-act-what-businesses-need-to-know ; https://www.dsci.in/article/content/indias-framework-processing-childrens-data-and-disability-related-information | 13 Nov 2026 | **Secondary sources**; primary text (MeitY/Gazette) must be checked by counsel |
| 3 | Flask, MySQL, Leaflet, Geolocation (MDN), Gmail SMTP, Gemini, OR-Tools docs | Respective vendors | — | **Not retrieved this session** | [VERIFY] before relying on specifics |
| 4 | Motor Vehicles Act 1988 / state rules; school-bus norms; POCSO 2012; driver verification | Govt. of India / state | — | **Not retrieved this session** | [VERIFY] — legal review required |
| 5 | NIST SP 800-63B (OTP guidance) | NIST | — | **Not retrieved this session** | [VERIFY] |
