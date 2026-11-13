from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, time

from backend.app.extensions import db
from backend.app.models import RideRequest, RideRequestStudent, Student, Allocation
from backend.app.services.matching import match_ride_request

bp = Blueprint('rides', __name__, url_prefix='/api/v1/ride-requests')

@bp.route('', methods=['GET', 'POST'])
@login_required
def rides():
    if request.method == 'POST':
        # Create new ride request
        if current_user.role != 'GUARDIAN':
            return jsonify({'ok': False, 'error': {'message': 'Only guardians can create ride requests'}}), 403
        
        data = request.get_json()
        student_ids = data.get('student_ids', [])
        
        if not student_ids:
            return jsonify({'ok': False, 'error': {'message': 'At least one student required'}}), 400
        
        # Verify ownership
        students = Student.query.filter(Student.id.in_(student_ids), Student.guardian_id == current_user.id).all()
        if len(students) != len(student_ids):
            return jsonify({'ok': False, 'error': {'message': 'Invalid student selection'}}), 403
        
        ride_request = RideRequest(
            guardian_id=current_user.id,
            pickup_lat=data.get('pickup_lat'),
            pickup_lng=data.get('pickup_lng'),
            pickup_address=data.get('pickup_address', ''),
            dest_lat=data.get('dest_lat'),
            dest_lng=data.get('dest_lng'),
            dest_address=data.get('dest_address', ''),
            travel_date=datetime.strptime(data.get('travel_date'), '%Y-%m-%d').date(),
            pickup_time=datetime.strptime(data.get('pickup_time'), '%H:%M').time(),
            notes=data.get('notes', ''),
            status='PENDING'
        )
        db.session.add(ride_request)
        db.session.flush()
        
        for student in students:
            rrs = RideRequestStudent(request_id=ride_request.id, student_id=student.id)
            db.session.add(rrs)
        
        db.session.commit()
        
        # Run matching
        try:
            candidates = match_ride_request(ride_request)
            
            # Create allocations
            for candidate in candidates:
                allocation = Allocation(
                    request_id=ride_request.id,
                    vehicle_id=candidate['vehicle'].id,
                    driver_id=candidate['driver'].id,
                    seats_reserved=len(students),
                    status='PROPOSED'
                )
                db.session.add(allocation)
            
            db.session.commit()
            
            return jsonify({
                'ok': True,
                'data': {
                    'request_id': ride_request.id,
                    'matches_found': len(candidates)
                }
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'ok': False, 'error': {'message': f'Matching failed: {str(e)}'}}), 500
    
    else:
        # GET - List ride requests
        if current_user.role == 'GUARDIAN':
            requests = RideRequest.query.filter_by(guardian_id=current_user.id).order_by(RideRequest.created_at.desc()).all()
        else:
            requests = RideRequest.query.order_by(RideRequest.created_at.desc()).limit(100).all()
        
        return jsonify({
            'ok': True,
            'data': {
                'requests': [{
                    'id': r.id,
                    'pickup_address': r.pickup_address,
                    'dest_address': r.dest_address,
                    'travel_date': r.travel_date.isoformat(),
                    'pickup_time': r.pickup_time.isoformat(),
                    'status': r.status,
                    'created_at': r.created_at.isoformat()
                } for r in requests]
            }
        }), 200

@bp.route('/<int:id>', methods=['GET'])
@login_required
def ride(id):
    ride_request = RideRequest.query.get_or_404(id)
    
    # Authorization check
    if current_user.role == 'GUARDIAN' and ride_request.guardian_id != current_user.id:
        return jsonify({'ok': False, 'error': {'message': 'Unauthorized'}}), 403
    
    allocations = Allocation.query.filter_by(request_id=id).all()
    
    return jsonify({
        'ok': True,
        'data': {
            'request': {
                'id': ride_request.id,
                'pickup_lat': float(ride_request.pickup_lat),
                'pickup_lng': float(ride_request.pickup_lng),
                'pickup_address': ride_request.pickup_address,
                'dest_lat': float(ride_request.dest_lat),
                'dest_lng': float(ride_request.dest_lng),
                'dest_address': ride_request.dest_address,
                'travel_date': ride_request.travel_date.isoformat(),
                'pickup_time': ride_request.pickup_time.isoformat(),
                'status': ride_request.status,
                'notes': ride_request.notes
            },
            'allocations': [{
                'id': a.id,
                'vehicle_id': a.vehicle_id,
                'driver_id': a.driver_id,
                'driver_name': a.driver.full_name,
                'vehicle_reg': a.vehicle.reg_no,
                'vehicle_type': a.vehicle.type,
                'status': a.status,
                'seats_reserved': a.seats_reserved
            } for a in allocations]
        }
    }), 200
