from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta

from backend.app.extensions import db
from backend.app.models import Allocation, RideRequest, Trip, TripPassenger, GuardianConsent
from backend.app.services.otp import issue_otp

bp = Blueprint('consent', __name__, url_prefix='/api/v1/allocations')

@bp.route('/<int:id>', methods=['GET'])
@login_required
def allocation(id):
    allocation = Allocation.query.get_or_404(id)
    
    # Authorization
    if current_user.role == 'GUARDIAN' and allocation.ride_request.guardian_id != current_user.id:
        return jsonify({'ok': False, 'error': {'message': 'Unauthorized'}}), 403
    
    return jsonify({
        'ok': True,
        'data': {
            'allocation': {
                'id': allocation.id,
                'status': allocation.status,
                'driver_name': allocation.driver.full_name,
                'driver_phone': allocation.driver.user.phone,
                'vehicle_reg': allocation.vehicle.reg_no,
                'vehicle_type': allocation.vehicle.type,
                'capacity': allocation.vehicle.permitted_capacity,
                'seats_reserved': allocation.seats_reserved
            }
        }
    }), 200

@bp.route('/<int:id>/consent', methods=['POST'])
@login_required
def consent(id):
    """Guardian approves or rejects an allocation."""
    if current_user.role != 'GUARDIAN':
        return jsonify({'ok': False, 'error': {'message': 'Only guardians can give consent'}}), 403
    
    allocation = Allocation.query.get_or_404(id)
    
    if allocation.ride_request.guardian_id != current_user.id:
        return jsonify({'ok': False, 'error': {'message': 'Unauthorized'}}), 403
    
    if allocation.status != 'PROPOSED':
        return jsonify({'ok': False, 'error': {'message': 'Allocation is not in proposed state'}}), 400
    
    data = request.get_json()
    action = data.get('action')  # 'approve' or 'reject'
    
    if action == 'approve':
        # Create consent record
        consent = GuardianConsent(
            allocation_id=allocation.id,
            guardian_id=current_user.id,
            consent_given=True,
            consent_at=datetime.utcnow()
        )
        db.session.add(consent)
        
        allocation.status = 'CONFIRMED'
        allocation.ride_request.status = 'MATCHED'
        
        # Create trip
        ride_request = allocation.ride_request
        pickup_dt = datetime.combine(ride_request.travel_date, ride_request.pickup_time)
        
        trip = Trip(
            allocation_id=allocation.id,
            driver_id=allocation.driver_id,
            vehicle_id=allocation.vehicle_id,
            pickup_lat=ride_request.pickup_lat,
            pickup_lng=ride_request.pickup_lng,
            pickup_address=ride_request.pickup_address,
            dest_lat=ride_request.dest_lat,
            dest_lng=ride_request.dest_lng,
            dest_address=ride_request.dest_address,
            scheduled_pickup=pickup_dt,
            status='ASSIGNED'
        )
        db.session.add(trip)
        db.session.flush()
        
        # Add passengers
        for rrs in ride_request.students:
            passenger = TripPassenger(trip_id=trip.id, student_id=rrs.student_id)
            db.session.add(passenger)
        
        # Issue pickup OTP
        pickup_code, _ = issue_otp(trip, 'PICKUP')
        
        db.session.commit()
        
        return jsonify({
            'ok': True,
            'data': {
                'trip_id': trip.id,
                'pickup_otp': pickup_code,
                'message': 'Trip created successfully'
            }
        }), 201
    
    elif action == 'reject':
        consent = GuardianConsent(
            allocation_id=allocation.id,
            guardian_id=current_user.id,
            consent_given=False,
            consent_at=datetime.utcnow()
        )
        db.session.add(consent)
        
        allocation.status = 'REJECTED'
        db.session.commit()
        
        return jsonify({'ok': True, 'data': {'message': 'Allocation rejected'}}), 200
    
    else:
        return jsonify({'ok': False, 'error': {'message': 'Invalid action'}}), 400
