# SETU Quick Completion Guide

## Current Status: 40% Complete

### ✓ COMPLETED
1. Project structure
2. Configuration (config.py, .env.example)
3. Database schema.sql (21 tables, all P0)
4. Database seed.sql (demo accounts)
5. All SQLAlchemy models (12 files)
6. Flask extensions setup
7. App factory pattern

### 🔄 TO COMPLETE (Priority Order)

## PHASE 1: Core Services (90 minutes)

### 1. Security Decorators (`backend/app/security/decorators.py`)
```python
from functools import wraps
from flask import abort
from flask_login import current_user

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        return f(*args, **kwargs)
    return decorated

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.has_role(*roles):
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator

def owns_student(student_id_param='student_id'):
    """Check guardian owns student"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            student_id = kwargs.get(student_id_param)
            from backend.app.models import Student
            student = Student.query.get_or_404(student_id)
            if student.guardian_id != current_user.id and current_user.role not in ['ADMIN', 'SAFETY_ADMIN']:
                abort(404)  # Don't reveal existence
            return f(*args, **kwargs)
        return decorated
    return decorator
```

### 2. Geo Service (`backend/app/services/geo.py`)
```python
import math

def haversine_km(lat1, lon1, lat2, lon2):
    """Calculate distance in km"""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def point_to_segment_distance(px, py, x1, y1, x2, y2):
    """Min distance from point to line segment in meters"""
    # Simplified: use haversine to segment endpoints and perpendicular
    # Full implementation: project point onto line
    dist_to_start = haversine_km(px, py, x1, y1) * 1000
    dist_to_end = haversine_km(px, py, x2, y2) * 1000
    return min(dist_to_start, dist_to_end)

def distance_to_polyline(lat, lng, polyline):
    """Min distance from point to polyline in meters"""
    min_dist = float('inf')
    for i in range(len(polyline) - 1):
        p1, p2 = polyline[i], polyline[i+1]
        dist = point_to_segment_distance(lat, lng, p1[0], p1[1], p2[0], p2[1])
        min_dist = min(min_dist, dist)
    return min_dist
```

### 3. OTP Service (`backend/app/services/otp.py`)
```python
import secrets
import hashlib
import hmac
from datetime import datetime, timedelta
from backend.app.extensions import db
from backend.app.models import OTPChallenge
from flask import current_app

def generate_otp():
    """Generate 6-digit OTP"""
    return f"{secrets.randbelow(1000000):06d}"

def hash_otp(otp_id, code):
    """Hash OTP with pepper and ID"""
    pepper = current_app.config['OTP_PEPPER'].encode()
    message = f"{otp_id}:{code}".encode()
    return hmac.new(pepper, message, hashlib.sha256).hexdigest()

def issue_otp(trip, purpose):
    """Issue new OTP, supersede previous"""
    # Supersede active OTPs
    OTPChallenge.query.filter_by(
        trip_id=trip.id, 
        purpose=purpose,
        status='ACTIVE'
    ).update({'status': 'SUPERSEDED'})
    
    code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    challenge = OTPChallenge(
        trip_id=trip.id,
        purpose=purpose,
        code_hash='',  # Set after flush
        expires_at=expires_at,
        status='ACTIVE'
    )
    db.session.add(challenge)
    db.session.flush()  # Get ID
    
    challenge.code_hash = hash_otp(challenge.id, code)
    db.session.commit()
    
    return code, challenge

def verify_otp(trip, purpose, submitted_code):
    """Verify OTP, return (success, message, challenge)"""
    challenge = OTPChallenge.query.filter_by(
        trip_id=trip.id,
        purpose=purpose,
        status='ACTIVE'
    ).with_for_update().first()
    
    if not challenge:
        return False, "No active OTP found", None
    
    if datetime.utcnow() > challenge.expires_at:
        challenge.status = 'EXPIRED'
        db.session.commit()
        return False, "OTP expired", challenge
    
    if challenge.attempts >= challenge.max_attempts:
        challenge.status = 'LOCKED'
        db.session.commit()
        return False, "OTP locked due to too many attempts", challenge
    
    challenge.attempts += 1
    
    submitted_hash = hash_otp(challenge.id, submitted_code)
    if hmac.compare_digest(challenge.code_hash, submitted_hash):
        challenge.status = 'CONSUMED'
        challenge.consumed_at = datetime.utcnow()
        db.session.commit()
        return True, "OTP verified", challenge
    else:
        db.session.commit()
        remaining = challenge.max_attempts - challenge.attempts
        return False, f"Invalid OTP ({remaining} attempts remaining)", challenge
```

### 4. Matching Service (`backend/app/services/matching.py`)
```python
from backend.app.models import Vehicle, Driver, Allocation
from backend.app.services.geo import haversine_km
from backend.app.extensions import db
from datetime import datetime, timedelta

def find_eligible_vehicles(ride_request, travel_date):
    """Find vehicles eligible for matching"""
    vehicles = Vehicle.query.join(Driver).filter(
        Driver.status == 'APPROVED',
        Vehicle.status == 'APPROVED',
        Driver.availability == 'AVAILABLE',
        Driver.licence_expiry >= travel_date,
        Vehicle.permit_expiry >= travel_date,
        Vehicle.insurance_expiry >= travel_date,
        Vehicle.fitness_expiry >= travel_date
    ).all()
    
    eligible = []
    for vehicle in vehicles:
        # Check service radius
        dist_to_pickup = haversine_km(
            float(vehicle.base_lat),
            float(vehicle.base_lng),
            float(ride_request.pickup_lat),
            float(ride_request.pickup_lng)
        )
        if dist_to_pickup <= float(vehicle.service_radius_km):
            eligible.append(vehicle)
    
    return eligible

def check_capacity(vehicle, seats_needed, window_start, window_end):
    """Check capacity with row lock - CRITICAL"""
    # Lock vehicle row
    locked_vehicle = db.session.query(Vehicle).filter_by(id=vehicle.id).with_for_update().first()
    
    # Calculate used seats
    overlapping = Allocation.query.filter(
        Allocation.vehicle_id == vehicle.id,
        Allocation.status.in_(['PROPOSED', 'CONFIRMED']),
        Allocation.window_start < window_end,
        Allocation.window_end > window_start
    ).all()
    
    used_seats = sum(a.seats_reserved for a in overlapping)
    remaining = locked_vehicle.permitted_capacity - used_seats
    
    return remaining >= seats_needed, remaining

def score_candidate(vehicle, ride_request):
    """Calculate match score"""
    dist = haversine_km(
        float(vehicle.base_lat), float(vehicle.base_lng),
        float(ride_request.pickup_lat), float(ride_request.pickup_lng)
    )
    proximity_score = max(0, 1 - dist / float(vehicle.service_radius_km))
    
    # Time fit (simplified - always 1 for MVP)
    time_fit = 1.0
    
    # Capacity fit (more remaining = better)
    # This will be calculated in check_capacity
    
    # Category preference
    category_score = 0.15  # Base
    
    total_score = (
        0.40 * proximity_score +
        0.25 * time_fit +
        0.20 * 0.5 +  # Simplified capacity fit
        category_score
    )
    
    return total_score

def match_ride_request(ride_request):
    """Match ride request to providers"""
    from backend.app.models import RideRequestStudent
    
    # Get number of students
    seats_needed = db.session.query(RideRequestStudent).filter_by(
        request_id=ride_request.id
    ).count()
    
    # Time window
    pickup_dt = datetime.combine(ride_request.travel_date, ride_request.pickup_time)
    window_start = pickup_dt - timedelta(minutes=15)
    window_end = pickup_dt + timedelta(hours=2)  # Est trip duration
    
    # Find eligible vehicles
    vehicles = find_eligible_vehicles(ride_request, ride_request.travel_date)
    
    # Score and check capacity
    candidates = []
    for vehicle in vehicles:
        has_capacity, remaining = check_capacity(vehicle, seats_needed, window_start, window_end)
        if has_capacity:
            score = score_candidate(vehicle, ride_request)
            candidates.append({
                'vehicle': vehicle,
                'driver': vehicle.driver,
                'score': score,
                'remaining_capacity': remaining
            })
    
    # Sort by score
    candidates.sort(key=lambda x: x['score'], reverse=True)
    
    return candidates[:3]  # Top 3
```

## PHASE 2: API Endpoints (60 minutes)

Create each endpoint file following this pattern. I'll show auth as example:

### `backend/app/api/auth.py`
```python
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, current_user
from backend.app.extensions import db, limiter
from backend.app.models import User
from backend.app.security.decorators import login_required

bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    data = request.get_json()
    
    # Validate
    if not all(k in data for k in ['name', 'email', 'phone', 'password', 'role']):
        return jsonify({'ok': False, 'error': {'code': 'VALIDATION_FAILED'}}), 422
    
    # Check role whitelist
    if data['role'] not in ['GUARDIAN', 'DRIVER']:
        return jsonify({'ok': False, 'error': {'code': 'INVALID_ROLE'}}), 403
    
    # Check duplicate
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'ok': False, 'error': {'code': 'EMAIL_EXISTS'}}), 409
    
    # Create user
    user = User(
        role=data['role'],
        name=data['name'],
        email=data['email'].lower(),
        phone=data['phone']
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'ok': True, 'data': user.to_dict()}), 201

@bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    data = request.get_json()
    
    user = User.query.filter_by(email=data.get('email', '').lower()).first()
    
    if not user or not user.check_password(data.get('password', '')):
        return jsonify({'ok': False, 'error': {'code': 'INVALID_CREDENTIALS'}}), 401
    
    if user.status != 'ACTIVE':
        return jsonify({'ok': False, 'error': {'code': 'ACCOUNT_SUSPENDED'}}), 403
    
    login_user(user, remember=True)
    
    return jsonify({
        'ok': True,
        'data': {
            'user': user.to_dict(include_sensitive=True),
            'csrf_token': 'TODO'  # Implement CSRF
        }
    }), 200

@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return '', 204

@bp.route('/me', methods=['GET'])
@login_required
def me():
    return jsonify({'ok': True, 'data': current_user.to_dict(include_sensitive=True)}), 200
```

### Similar Pattern for:
- `backend/app/api/students.py` - CRUD operations with ownership checks
- `backend/app/api/providers.py` - Driver/vehicle registration
- `backend/app/api/admin_bp.py` - Approve/reject providers
- `backend/app/api/rides.py` - Create request + call matching service
- `backend/app/api/consent.py` - Approve/reject with trip creation
- `backend/app/api/trips.py` - State transitions + OTP
- `backend/app/api/gps.py` - Submit location + call safety engine
- `backend/app/api/incidents.py` - List/acknowledge/resolve
- `backend/app/api/notifications.py` - List in-app
- `backend/app/api/health.py` - Health check

## PHASE 3: Safety Engine (30 minutes)

### `backend/app/services/safety.py`
```python
from backend.app.models import LocationUpdate, Incident, JourneyEvent
from backend.app.services.geo import distance_to_polyline
from backend.app.extensions import db
from flask import current_app
from datetime import datetime

def process_gps_ping(trip, ping_data):
    """Process GPS ping through safety engine"""
    
    # Validate
    if ping_data['accuracy'] > current_app.config['MAX_ACCURACY_M']:
        # Store but don't use for deviation
        return {'in_corridor': None, 'flagged': 'LOW_ACCURACY'}
    
    # Calculate distance from route
    polyline = trip.route_polyline_json
    dist = distance_to_polyline(ping_data['lat'], ping_data['lng'], polyline)
    
    in_corridor = dist <= trip.corridor_radius_m
    
    # Update deviation state
    state = trip.deviation_state or {'out_count': 0, 'first_out_ts': None, 'max_dist': 0}
    
    if in_corridor:
        if state['out_count'] > 0:
            log_event(trip, 'DEVIATION_CLEARED')
        state = {'out_count': 0, 'first_out_ts': None, 'max_dist': 0}
    else:
        state['out_count'] += 1
        if not state['first_out_ts']:
            state['first_out_ts'] = datetime.utcnow().isoformat()
        state['max_dist'] = max(state['max_dist'], dist)
        
        # Check persistence
        first_out = datetime.fromisoformat(state['first_out_ts'])
        span_seconds = (datetime.utcnow() - first_out).total_seconds()
        
        is_persistent = (
            state['out_count'] >= current_app.config['PERSIST_PINGS'] and
            (span_seconds >= current_app.config['PERSIST_SECONDS'] or 
             state['max_dist'] >= 2000)
        )
        
        if is_persistent and not state.get('incident_id'):
            incident = create_incident(trip, ping_data, state)
            state['incident_id'] = incident.id
    
    trip.deviation_state = state
    db.session.commit()
    
    return {'in_corridor': in_corridor, 'state': state}

def create_incident(trip, last_ping, state):
    """Create safety incident"""
    incident = Incident(
        trip_id=trip.id,
        severity='MEDIUM',
        status='OPEN',
        cause_hint='UNEXPLAINED_PERSISTENT_DEVIATION',
        source='ENGINE',
        last_lat=last_ping['lat'],
        last_lng=last_ping['lng'],
        last_seen_at=datetime.utcnow()
    )
    db.session.add(incident)
    db.session.flush()
    
    # Log event
    log_event(trip, 'INCIDENT_OPENED', {'incident_id': incident.id})
    
    # Notify (async)
    from backend.app.services.notify import notify_deviation
    notify_deviation(trip, incident)
    
    return incident

def log_event(trip, event_type, payload=None):
    """Log journey event"""
    event = JourneyEvent(
        trip_id=trip.id,
        event_type=event_type,
        payload_json=payload
    )
    db.session.add(event)
```

## PHASE 4: Notification Service (20 minutes)

### `backend/app/services/notify.py`
```python
from backend.app.models import Notification
from backend.app.extensions import db, mail
from flask_mail import Message
from flask import current_app
import time
import threading

def queue_notification(user_id, template, subject, payload, related_type=None, related_id=None):
    """Queue both email and in-app notification"""
    # Email
    email_notif = Notification(
        user_id=user_id,
        channel='EMAIL',
        template=template,
        subject=subject,
        payload_json=payload,
        related_type=related_type,
        related_id=related_id,
        status='QUEUED'
    )
    db.session.add(email_notif)
    
    # In-app
    app_notif = Notification(
        user_id=user_id,
        channel='IN_APP',
        template=template,
        subject=subject,
        payload_json=payload,
        related_type=related_type,
        related_id=related_id,
        status='SENT'  # Immediately visible
    )
    db.session.add(app_notif)
    db.session.commit()

def start_email_worker(app):
    """Background worker to send emails"""
    with app.app_context():
        while True:
            try:
                pending = Notification.query.filter_by(
                    channel='EMAIL',
                    status='QUEUED'
                ).limit(10).all()
                
                for notif in pending:
                    try:
                        send_email(notif)
                        notif.status = 'SENT'
                        notif.sent_at = datetime.utcnow()
                    except Exception as e:
                        notif.status = 'FAILED'
                        notif.last_error = str(e)[:255]
                        notif.attempts += 1
                    
                    db.session.commit()
                
                time.sleep(2)
            except Exception as e:
                print(f"Email worker error: {e}")
                time.sleep(5)

def send_email(notification):
    """Send actual email via Gmail SMTP"""
    from backend.app.models import User
    user = User.query.get(notification.user_id)
    
    msg = Message(
        subject=notification.subject,
        recipients=[user.email],
        body=f"Please log in to SETU to view details: {current_app.config['BASE_URL']}"
    )
    mail.send(msg)

def notify_deviation(trip, incident):
    """Notify about route deviation"""
    # Get guardian
    passengers = trip.passengers
    for passenger in passengers:
        queue_notification(
            user_id=passenger.student.guardian_id,
            template='ROUTE_DEVIATION',
            subject='SETU Alert: Route Deviation Detected',
            payload={'trip_id': trip.id, 'incident_id': incident.id},
            related_type='incident',
            related_id=incident.id
        )
```

## PHASE 5: Frontend (60 minutes)

Create TypeScript modules following this structure:

### `frontend/src/api.ts`
```typescript
const BASE_URL = '/api/v1';

export async function apiCall(endpoint: string, options: RequestInit = {}) {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        credentials: 'include'
    });
    
    const data = await response.json();
    
    if (!data.ok) {
        throw new Error(data.error?.message || 'Request failed');
    }
    
    return data.data;
}

export const api = {
    auth: {
        register: (data: any) => apiCall('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
        login: (data: any) => apiCall('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
        logout: () => apiCall('/auth/logout', { method: 'POST' })
    },
    students: {
        list: () => apiCall('/students'),
        create: (data: any) => apiCall('/students', { method: 'POST', body: JSON.stringify(data) })
    },
    rides: {
        create: (data: any) => apiCall('/ride-requests', { method: 'POST', body: JSON.stringify(data) })
    },
    trips: {
        get: (id: number) => apiCall(`/trips/${id}`),
        getLocation: (id: number) => apiCall(`/trips/${id}/location/latest`)
    }
};
```

### `frontend/src/map.ts`
```typescript
import L from 'leaflet';

export function initMap(containerId: string, center: [number, number], zoom: number) {
    const map = L.map(containerId).setView(center, zoom);
    
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);
    
    return map;
}

export function addMarker(map: L.Map, lat: number, lng: number, label: string) {
    return L.marker([lat, lng]).addTo(map).bindPopup(label);
}
```

## PHASE 6: Templates (30 minutes)

Create basic HTML templates for each role dashboard. Example for guardian:

### `backend/app/templates/guardian_dashboard.html`
```html
<!DOCTYPE html>
<html>
<head>
    <title>SETU - Guardian Dashboard</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
    <div id="app">
        <h1>Guardian Dashboard</h1>
        <div id="students"></div>
        <button onclick="requestRide()">Request Alternative Transport</button>
        <div id="active-trip"></div>
        <div id="map" style="height: 400px;"></div>
    </div>
    
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script type="module" src="/static/js/guardian.js"></script>
</body>
</html>
```

## COMPLETION CHECKLIST

- [ ] All services implemented
- [ ] All API endpoints created
- [ ] Error handling (`backend/app/errors.py`)
- [ ] Route registration (`backend/app/routes.py`)
- [ ] Login manager user_loader
- [ ] TypeScript compiled
- [ ] Basic CSS
- [ ] Health endpoint working
- [ ] Database seeded with proper password hashes
- [ ] .env file created and configured
- [ ] Test end-to-end flow

## ESTIMATED TIME: 4-5 hours for complete working P0 implementation

## FASTEST PATH TO DEMO:
1. Complete services (matching, OTP, safety) - 2 hours
2. Complete API endpoints - 1.5 hours
3. Minimal frontend (API calls + forms) - 1 hour
4. Integration testing - 0.5 hours

Total: 5 hours for working backend + basic frontend
