"""GPS safety engine: validate pings, detect deviations, raise incidents."""
import json
from datetime import datetime

from flask import current_app

from backend.app.extensions import db
from backend.app.models import LocationUpdate, JourneyEvent, Incident
from backend.app.services.geo import distance_to_polyline, haversine_km


def _get_polyline(trip):
    """Return the route polyline as a list of [lat, lng] pairs, or []."""
    raw = getattr(trip, 'route_polyline_json', None)
    if not raw:
        return []
    if isinstance(raw, list):
        return raw
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return []


def _get_deviation_state(trip):
    raw = getattr(trip, 'deviation_state', None)
    if isinstance(raw, dict):
        return dict(raw)
    if raw:
        try:
            return json.loads(raw)
        except (TypeError, ValueError):
            pass
    return {'out_count': 0, 'first_out_ts': None, 'max_dist': 0}


def _set_deviation_state(trip, state):
    trip.deviation_state = state


def log_event(trip, event_type, payload=None):
    """Append a JourneyEvent row (not committed — caller must commit)."""
    event = JourneyEvent(
        trip_id=trip.id,
        event_type=event_type,
        payload_json=payload,
    )
    db.session.add(event)


def create_incident(trip, last_ping, state):
    """Create a MEDIUM OPEN incident and return it (not committed)."""
    incident = Incident(
        trip_id=trip.id,
        severity='MEDIUM',
        status='OPEN',
        cause_hint='UNEXPLAINED_PERSISTENT_DEVIATION',
        source='ENGINE',
        last_lat=last_ping['lat'],
        last_lng=last_ping['lng'],
        last_seen_at=datetime.utcnow(),
    )
    db.session.add(incident)
    db.session.flush()

    log_event(trip, 'INCIDENT_OPENED', {'incident_id': incident.id})

    # Notify asynchronously (best-effort)
    try:
        from backend.app.services.notify import notify_deviation
        notify_deviation(trip, incident)
    except Exception:
        pass

    return incident


def process_gps_ping(trip, ping_data):
    """
    Validate a GPS ping against the safety rules.

    Returns a dict with keys: in_corridor (bool|None), flagged (str|None), state (dict).
    """
    cfg = current_app.config
    max_accuracy = cfg.get('MAX_ACCURACY_M', 100)

    # Persist location update (driver_id sourced from trip)
    loc = LocationUpdate(
        trip_id=trip.id,
        driver_id=trip.driver_id,
        lat=ping_data['lat'],
        lng=ping_data['lng'],
        accuracy_m=ping_data.get('accuracy', 0),
        server_ts=datetime.utcnow(),
    )
    db.session.add(loc)

    if ping_data.get('accuracy', 0) > max_accuracy:
        db.session.commit()
        return {'in_corridor': None, 'flagged': 'LOW_ACCURACY', 'state': _get_deviation_state(trip)}

    polyline = _get_polyline(trip)
    corridor_radius = getattr(trip, 'corridor_radius_m', None) or cfg.get('CORRIDOR_RADIUS_M', 500)

    if polyline:
        dist = distance_to_polyline(ping_data['lat'], ping_data['lng'], polyline)
        in_corridor = dist <= corridor_radius
    else:
        # No route stored; treat all pings as in-corridor
        dist = 0
        in_corridor = True

    state = _get_deviation_state(trip)

    if in_corridor:
        if state['out_count'] > 0:
            log_event(trip, 'DEVIATION_CLEARED')
        state = {'out_count': 0, 'first_out_ts': None, 'max_dist': 0}
    else:
        state['out_count'] += 1
        if not state.get('first_out_ts'):
            state['first_out_ts'] = datetime.utcnow().isoformat()
        state['max_dist'] = max(state.get('max_dist', 0), dist)

        # Check persistence thresholds
        first_out = datetime.fromisoformat(state['first_out_ts'])
        span_seconds = (datetime.utcnow() - first_out).total_seconds()

        is_persistent = (
            state['out_count'] >= cfg.get('PERSIST_PINGS', 3) and
            (span_seconds >= cfg.get('PERSIST_SECONDS', 20) or state['max_dist'] >= 2000)
        )

        if is_persistent and not state.get('incident_id'):
            incident = create_incident(trip, ping_data, state)
            state['incident_id'] = incident.id

    _set_deviation_state(trip, state)
    db.session.commit()

    return {'in_corridor': in_corridor, 'state': state, 'flagged': None}


def process_location_update(trip, location):
    """Process a new location update for safety monitoring."""
    # Simple corridor check
    if not trip.pickup_lat or not trip.dest_lat:
        return
    
    cfg = current_app.config
    corridor_radius = cfg.get('CORRIDOR_RADIUS_M', 500) / 1000.0  # Convert to km
    
    # Check if location is within corridor to pickup or dest
    dist_to_pickup = haversine_km(float(location.lat), float(location.lng), 
                                   float(trip.pickup_lat), float(trip.pickup_lng))
    dist_to_dest = haversine_km(float(location.lat), float(location.lng),
                                 float(trip.dest_lat), float(trip.dest_lng))
    
    # Simple deviation: more than corridor_radius from both pickup and dest
    if dist_to_pickup > corridor_radius and dist_to_dest > corridor_radius:
        # Check if there's already an open incident
        existing = Incident.query.filter_by(trip_id=trip.id, status='OPEN').first()
        if not existing:
            incident = Incident(
                trip_id=trip.id,
                severity='MEDIUM',
                status='OPEN',
                cause_hint='ROUTE_DEVIATION',
                source='ENGINE',
                last_lat=location.lat,
                last_lng=location.lng,
                last_seen_at=datetime.utcnow()
            )
            db.session.add(incident)
            
            # Log event
            event = JourneyEvent(
                trip_id=trip.id,
                event_type='INCIDENT_OPENED',
                payload_json={'incident_id': incident.id}
            )
            db.session.add(event)

