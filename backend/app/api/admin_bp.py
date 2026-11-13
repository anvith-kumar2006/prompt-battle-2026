from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from backend.app.extensions import db
from backend.app.models import Driver, Vehicle

bp = Blueprint('admin', __name__, url_prefix='/api/v1/admin')

@bp.route('/providers', methods=['GET'])
@login_required
def providers():
    """List all providers pending approval."""
    if current_user.role not in ['ADMIN', 'SAFETY_ADMIN']:
        return jsonify({'ok': False, 'error': {'message': 'Unauthorized'}}), 403
    
    drivers = Driver.query.filter_by(status='PENDING').all()
    vehicles = Vehicle.query.filter_by(status='PENDING').all()
    
    return jsonify({
        'ok': True,
        'data': {
            'drivers': [{
                'id': d.id,
                'full_name': d.full_name,
                'licence_no': d.licence_no,
                'category': d.category,
                'status': d.status
            } for d in drivers],
            'vehicles': [{
                'id': v.id,
                'reg_no': v.reg_no,
                'type': v.type,
                'capacity': v.permitted_capacity,
                'status': v.status
            } for v in vehicles]
        }
    }), 200

@bp.route('/drivers/<int:id>/approve', methods=['POST'])
@login_required
def approve_driver(id):
    """Approve a driver."""
    if current_user.role not in ['ADMIN', 'SAFETY_ADMIN']:
        return jsonify({'ok': False, 'error': {'message': 'Unauthorized'}}), 403
    
    driver = Driver.query.get_or_404(id)
    driver.status = 'APPROVED'
    driver.verified_by = current_user.id
    driver.verified_at = db.func.now()
    db.session.commit()
    
    return jsonify({'ok': True, 'data': {'message': 'Driver approved'}}), 200

@bp.route('/vehicles/<int:id>/approve', methods=['POST'])
@login_required
def approve_vehicle(id):
    """Approve a vehicle."""
    if current_user.role not in ['ADMIN', 'SAFETY_ADMIN']:
        return jsonify({'ok': False, 'error': {'message': 'Unauthorized'}}), 403
    
    vehicle = Vehicle.query.get_or_404(id)
    vehicle.status = 'APPROVED'
    vehicle.verified_by = current_user.id
    vehicle.verified_at = db.func.now()
    db.session.commit()
    
    return jsonify({'ok': True, 'data': {'message': 'Vehicle approved'}}), 200
