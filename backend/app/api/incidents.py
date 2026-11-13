from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from backend.app.extensions import db
from backend.app.models import Incident, Trip

bp = Blueprint('incidents', __name__, url_prefix='/api/v1/incidents')

@bp.route('', methods=['GET'])
@login_required
def incidents():
    """List incidents."""
    if current_user.role in ['ADMIN', 'SAFETY_ADMIN']:
        incidents_list = Incident.query.order_by(Incident.created_at.desc()).limit(100).all()
    else:
        return jsonify({'ok': False, 'error': {'message': 'Unauthorized'}}), 403
    
    return jsonify({
        'ok': True,
        'data': {
            'incidents': [{
                'id': i.id,
                'trip_id': i.trip_id,
                'severity': i.severity,
                'status': i.status,
                'cause_hint': i.cause_hint,
                'created_at': i.created_at.isoformat(),
                'last_seen_at': i.last_seen_at.isoformat() if i.last_seen_at else None
            } for i in incidents_list]
        }
    }), 200

@bp.route('/<int:id>', methods=['GET'])
@login_required
def incident(id):
    """Get incident details."""
    if current_user.role not in ['ADMIN', 'SAFETY_ADMIN']:
        return jsonify({'ok': False, 'error': {'message': 'Unauthorized'}}), 403
    
    incident = Incident.query.get_or_404(id)
    
    return jsonify({
        'ok': True,
        'data': {
            'incident': {
                'id': incident.id,
                'trip_id': incident.trip_id,
                'severity': incident.severity,
                'status': incident.status,
                'cause_hint': incident.cause_hint,
                'last_lat': float(incident.last_lat) if incident.last_lat else None,
                'last_lng': float(incident.last_lng) if incident.last_lng else None,
                'created_at': incident.created_at.isoformat(),
                'last_seen_at': incident.last_seen_at.isoformat() if incident.last_seen_at else None
            }
        }
    }), 200

@bp.route('/<int:id>/acknowledge', methods=['POST'])
@login_required
def acknowledge(id):
    """Acknowledge an incident."""
    if current_user.role not in ['ADMIN', 'SAFETY_ADMIN']:
        return jsonify({'ok': False, 'error': {'message': 'Unauthorized'}}), 403
    
    incident = Incident.query.get_or_404(id)
    incident.status = 'ACKNOWLEDGED'
    incident.acknowledged_by = current_user.id
    db.session.commit()
    
    return jsonify({'ok': True, 'data': {'message': 'Incident acknowledged'}}), 200

@bp.route('/<int:id>/resolve', methods=['POST'])
@login_required
def resolve(id):
    """Resolve an incident."""
    if current_user.role not in ['ADMIN', 'SAFETY_ADMIN']:
        return jsonify({'ok': False, 'error': {'message': 'Unauthorized'}}), 403
    
    incident = Incident.query.get_or_404(id)
    
    data = request.get_json()
    incident.status = 'RESOLVED'
    incident.resolution_notes = data.get('notes', '')
    db.session.commit()
    
    return jsonify({'ok': True, 'data': {'message': 'Incident resolved'}}), 200
