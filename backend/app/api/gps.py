from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime

from backend.app.extensions import db
from backend.app.models import Trip, LocationUpdate
from backend.app.services.safety import process_location_update

bp = Blueprint('gps', __name__, url_prefix='/api/v1/trips')

@bp.route('/<int:id>/location', methods=['POST'])
@login_required
def submit_location(id):
    """Driver submits GPS location."""
    if current_user.role != 'DRIVER':
        return jsonify({'ok': False, 'error': {'message': 'Only drivers can submit locations'}}), 403
    
    trip = Trip.query.get_or_404(id)
    
    if trip.driver_id != current_user.id:
        return jsonify({'ok': False, 'error': {'message': 'Unauthorized'}}), 403
    
    if trip.status not in ['EN_ROUTE_PICKUP', 'IN_PROGRESS']:
        return jsonify({'ok': False, 'error': {'message': 'Trip is not active'}}), 400
    
    data = request.get_json()
    
    location = LocationUpdate(
        trip_id=trip.id,
        lat=data.get('lat'),
        lng=data.get('lng'),
        accuracy_m=data.get('accuracy_m', 50),
        heading=data.get('heading'),
        speed_kmh=data.get('speed_kmh'),
        recorded_at=datetime.utcnow()
    )
    db.session.add(location)
    db.session.flush()
    
    # Run safety check
    try:
        process_location_update(trip, location)
    except Exception as e:
        # Don't fail the request if safety check fails
        pass
    
    db.session.commit()
    
    return jsonify({'ok': True, 'data': {'message': 'Location recorded'}}), 201

@bp.route('/<int:id>/location/latest', methods=['GET'])
@login_required
def latest_location(id):
    """Get latest location for a trip."""
    trip = Trip.query.get_or_404(id)
    
    # Authorization
    if current_user.role == 'GUARDIAN':
        passenger_guardians = [p.student.guardian_id for p in trip.passengers]
        if current_user.id not in passenger_guardians:
            return jsonify({'ok': False, 'error': {'message': 'Unauthorized'}}), 403
    elif current_user.role == 'DRIVER':
        if trip.driver_id != current_user.id:
            return jsonify({'ok': False, 'error': {'message': 'Unauthorized'}}), 403
    
    latest = LocationUpdate.query.filter_by(trip_id=id).order_by(LocationUpdate.recorded_at.desc()).first()
    
    if not latest:
        return jsonify({'ok': True, 'data': {'location': None}}), 200
    
    return jsonify({
        'ok': True,
        'data': {
            'location': {
                'lat': float(latest.lat),
                'lng': float(latest.lng),
                'accuracy_m': latest.accuracy_m,
                'heading': latest.heading,
                'speed_kmh': latest.speed_kmh,
                'recorded_at': latest.recorded_at.isoformat()
            }
        }
    }), 200
