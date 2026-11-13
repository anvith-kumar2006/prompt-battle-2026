from flask import Blueprint

bp = Blueprint('notifications', __name__, url_prefix='/api/v1/notifications')

@bp.route('', methods=['GET'])
def notifications():
    return {'ok': True, 'message': 'To be implemented'}, 501

@bp.route('/<int:id>/read', methods=['POST'])
def mark_read(id):
    return {'ok': True, 'message': 'To be implemented'}, 501
