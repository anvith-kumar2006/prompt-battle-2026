# SETU Implementation Plan

## Documentation Review Summary

### P0 Requirements Extracted:
1. **Auth**: Registration (Guardian/Driver), Login, Logout, Role-based access, Object-level authorization
2. **Students**: CRUD by guardians, age category derivation, institution linking
3. **Providers**: Driver/vehicle registration, admin approval (SIMULATED), expiry checks
4. **Locations**: Leaflet map, pickup/destination selection, coordinate validation
5. **Ride Requests**: Create with students, match eligible providers, capacity-aware
6. **Matching**: Eligibility filter (approved+unexpired), capacity check with row locks, scoring algorithm
7. **Consent**: Guardian approval gate, consent recording, trip creation
8. **Trips**: State machine (SCHEDULED→EN_ROUTE→AT_PICKUP→IN_PROGRESS→ARRIVED→COMPLETED)
9. **OTP**: Pickup/dropoff verification, 6-digit, hashed, expiry, attempt limits
10. **GPS Tracking**: Browser watchPosition, validation, storage, parent view with staleness
11. **Safety Engine**: Corridor check, accuracy filtering, persistence threshold, incident creation
12. **Incidents**: OPEN→ACKNOWLEDGED→RESOLVED, severity levels, timeline
13. **Notifications**: Email via Gmail SMTP, in-app mirror, failure handling
14. **Admin**: Provider approval, incident monitoring, user management

### Technology Stack:
- Backend: Python 3, Flask, Flask-SQLAlchemy, PyMySQL
- Database: MySQL 8, InnoDB
- Frontend: TypeScript → compiled JS, Leaflet, vanilla DOM
- Auth: Flask-Login, Werkzeug password hashing
- Email: smtplib/Flask-Mail
- Optional: Gemini API (P1)

### Database Tables (P0):
users, institutions, students, drivers, vehicles, provider_documents, routes, transport_disruptions, ride_requests, ride_request_students, allocations, guardian_consents, trips, trip_passengers, otp_challenges, location_updates, journey_events, incidents, notifications, audit_logs

### API Endpoints (P0 Core):
- Auth: register, login, logout, me
- Students: create, list, get, update
- Providers: register, vehicles CRUD, status
- Admin: approve/reject providers, approve/reject vehicles
- Rides: create (with matching), list, get, cancel
- Allocations: get details, consent/approve, reject
- Trips: list, get, start-route, arrive-pickup, pickup/verify, arrive-destination, dropoff/verify
- GPS: submit location, get latest, get track
- Incidents: list, get, acknowledge, resolve
- Notifications: list, mark read
- Health: health check

### Development Phases:
- **Phase 0**: Project setup, Flask app, MySQL connection, TypeScript config
- **Phase 1**: Database schema, seed data, authentication
- **Phase 2**: Guardian & student management
- **Phase 3**: Driver & provider management, admin approval
- **Phase 4**: Maps & ride requests
- **Phase 5**: Matching & allocation with capacity locks
- **Phase 6**: Guardian consent & trip creation
- **Phase 7**: Trip management & OTP
- **Phase 8**: GPS tracking
- **Phase 9**: Route deviation & safety engine
- **Phase 10**: Admin & safety dashboard
- **Phase 11**: Notifications (optional Gemini P1)

### Unresolved Questions:
- None blocking P0 - all critical design decisions documented in specs

### Requirement-to-Module Mapping:
- FR-AUTH → backend/app/api/auth.py + security/decorators.py
- FR-STU → backend/app/api/students.py + models/student.py
- FR-PROV → backend/app/api/providers.py + models/provider.py
- FR-RIDE → backend/app/api/rides.py + services/matching.py
- FR-MATCH → services/matching.py + services/geo.py
- FR-CONS → backend/app/api/consent.py
- FR-TRIP → backend/app/api/trips.py + services/otp.py
- FR-GPS → backend/app/api/gps.py + services/geo.py
- FR-SAFE → services/safety.py
- FR-NOTIF → services/notify.py

### Critical Business Rules to Enforce:
- BR-001: Minors require guardian consent before trip assignment
- BR-002: Only APPROVED, unexpired driver+vehicle eligible
- BR-003: Never exceed permitted_capacity
- BR-004: OTP 6-digit, ≤10min, single-use, ≤5 attempts
- BR-005: Drop-off needs OTP/confirmation for minors
- BR-007: Single GPS point never creates incident
- BR-008: AI never decides critical actions
- BR-012: No automatic police contact

### Demo Flow (14 steps):
1. Guardian registration/login ✓
2. Student registration ✓
3. Provider & vehicle registration ✓
4. Admin approval (simulated) ✓
5. Pickup/destination selection ✓
6. Ride request ✓
7. Capacity-aware matching ✓
8. Guardian consent ✓
9. Driver assignment ✓
10. Pickup OTP ✓
11. GPS tracking/simulated drive ✓
12. Simulated deviation ✓
13. Incident creation & notification ✓
14. Drop-off verification ✓
15. Journey completion ✓

## Implementation Order (Fast-Track):
1. Setup: structure, requirements, .env, .gitignore
2. Database: schema.sql, seed.sql
3. Models: all P0 tables via SQLAlchemy
4. Auth: register, login, decorators
5. Core APIs: students, providers, rides, consent, trips, GPS, incidents
6. Services: matching, OTP, safety engine, notifications
7. Frontend: TypeScript modules, Leaflet map, dashboards
8. Testing: key P0 test cases
9. Demo prep: seed data, simulation buttons

Ready to implement.
