from flask import Blueprint, jsonify
from backend.app.extensions import db
from datetime import datetime

bp = Blueprint('health', __name__, url_prefix='/api/v1')

@bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    return jsonify({
        'ok': True,
        'data': {
            'status': 'running',
            'timestamp': datetime.utcnow().isoformat(),
            'database': db_status
        }
    }), 200
