from flask import Blueprint

bp = Blueprint('providers', __name__, url_prefix='/api/v1/providers')

@bp.route('/register', methods=['POST'])
def register():
    return {'ok': True, 'message': 'To be implemented'}, 501

@bp.route('/me', methods=['GET'])
def me():
    return {'ok': True, 'message': 'To be implemented'}, 501
