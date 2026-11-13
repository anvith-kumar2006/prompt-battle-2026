from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime

from backend.app.extensions import db
from backend.app.models import Trip, TripPassenger
from backend.app.services.otp import verify_otp, issue_otp

bp = Blueprint('trips', __name__, url_prefix='/api/v1/trips')

@bp.route('', methods=['GET'])
@login_required
def trips():
    """List trips based on user role."""
    if current_user.role == 'DRIVER':
        trips_list = Trip.query.filter_by(driver_id=current_user.id).order_by(Trip.scheduled_pickup.desc()).all()
    elif current_user.role == 'GUARDIAN':
        trips_list = (
            Trip.query
            .join(TripPassenger)
            .join(TripPassenger.student)
            .filter(TripPassenger.student.guardian_id == current_user.id)
            .order_by(Trip.scheduled_pickup.desc())
            .all()
        )
    else:
        trips_list = Trip.query.order_by(Trip.scheduled_pickup.desc()).limit(100).all()
    
    return jsonify({
        'ok': True,
        'data': {
            'trips': [{
                'id': t.id,
                'status': t.status,
                'pickup_address': t.pickup_address,
                'dest_address': t.dest_address,
                'scheduled_pickup': t.scheduled_pickup.isoformat() if t.scheduled_pickup else None,
                'driver_name': t.driver.full_name if t.driver else None,
                'vehicle_reg': t.vehicle.reg_no if t.vehicle else None
            } for t in trips_list]
        }
    }), 200

@bp.route('/<int:id>', methods=['GET'])
@login_required
def trip(id):
    """Get trip details."""
    trip = Trip.query.get_or_404(id)
    
    # Authorization
    if current_user.role == 'GUARDIAN':
        passenger_guardians = [p.student.guardian_id for p in trip.passengers]
        if current_user.id not in passenger_guardians:
            return jsonify({'ok': False, 'error': {'message': 'Unauthorized'}}), 403
    elif current_user.role == 'DRIVER':
        if trip.driver_id != current_user.id:
            return jsonify({'ok': False, 'error': {'message': 'Unauthorized'}}), 403
    
    return jsonify({
        'ok': True,
        'data': {
            'trip': {
                'id': trip.id,
                'status': trip.status,
                'pickup_lat': float(trip.pickup_lat) if trip.pickup_lat else None,
                'pickup_lng': float(trip.pickup_lng) if trip.pickup_lng else None,
                'pickup_address': trip.pickup_address,
                'dest_lat': float(trip.dest_lat) if trip.dest_lat else None,
                'dest_lng': float(trip.dest_lng) if trip.dest_lng else None,
                'dest_address': trip.dest_address,
                'scheduled_pickup': trip.scheduled_pickup.isoformat() if trip.scheduled_pickup else None,
                'actual_pickup': trip.actual_pickup.isoformat() if trip.actual_pickup else None,
                'actual_dropoff': trip.actual_dropoff.isoformat() if trip.actual_dropoff else None,
                'driver_name': trip.driver.full_name if trip.driver else None,
                'driver_phone': trip.driver.user.phone if trip.driver else None,
                'vehicle_reg': trip.vehicle.reg_no if trip.vehicle else None,
                'vehicle_type': trip.vehicle.type if trip.vehicle else None
            }
        }
    }), 200

@bp.route('/<int:id>/start', methods=['POST'])
@login_required
def start_trip(id):
    """Driver starts the trip."""
    if current_user.role != 'DRIVER':
        return jsonify({'ok': False, 'error': {'message': 'Only drivers can start trips'}}), 403
    
    trip = Trip.query.get_or_404(id)
    
    if trip.driver_id != current_user.id:
        return jsonify({'ok': False, 'error': {'message': 'Unauthorized'}}), 403
    
    if trip.status != 'ASSIGNED':
        return jsonify({'ok': False, 'error': {'message': 'Trip cannot be started'}}), 400
    
    trip.status = 'EN_ROUTE_PICKUP'
    trip.started_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'ok': True, 'data': {'message': 'Trip started'}}), 200

@bp.route('/<int:id>/pickup', methods=['POST'])
@login_required
def confirm_pickup(id):
    """Confirm pickup with OTP."""
    trip = Trip.query.get_or_404(id)
    
    if current_user.role != 'DRIVER' or trip.driver_id != current_user.id:
        return jsonify({'ok': False, 'error': {'message': 'Unauthorized'}}), 403
    
    if trip.status != 'EN_ROUTE_PICKUP':
        return jsonify({'ok': False, 'error': {'message': 'Invalid trip state'}}), 400
    
    data = request.get_json()
    otp_code = data.get('otp')
    
    success, message, _ = verify_otp(trip, 'PICKUP', otp_code)
    
    if not success:
        return jsonify({'ok': False, 'error': {'message': message}}), 400
    
    trip.status = 'IN_PROGRESS'
    trip.actual_pickup = datetime.utcnow()
    
    # Issue dropoff OTP
    dropoff_code, _ = issue_otp(trip, 'DROPOFF')
    
    db.session.commit()
    
    return jsonify({
        'ok': True,
        'data': {
            'message': 'Pickup confirmed',
            'dropoff_otp': dropoff_code
        }
    }), 200

@bp.route('/<int:id>/dropoff', methods=['POST'])
@login_required
def confirm_dropoff(id):
    """Confirm dropoff with OTP."""
    trip = Trip.query.get_or_404(id)
    
    if current_user.role != 'DRIVER' or trip.driver_id != current_user.id:
        return jsonify({'ok': False, 'error': {'message': 'Unauthorized'}}), 403
    
    if trip.status != 'IN_PROGRESS':
        return jsonify({'ok': False, 'error': {'message': 'Invalid trip state'}}), 400
    
    data = request.get_json()
    otp_code = data.get('otp')
    
    success, message, _ = verify_otp(trip, 'DROPOFF', otp_code)
    
    if not success:
        return jsonify({'ok': False, 'error': {'message': message}}), 400
    
    trip.status = 'COMPLETED'
    trip.actual_dropoff = datetime.utcnow()
    trip.completed_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'ok': True, 'data': {'message': 'Trip completed successfully'}}), 200
