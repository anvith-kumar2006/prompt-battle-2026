from flask import jsonify

def register_error_handlers(app):
    """Register error handlers for the Flask app"""
    
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({
            'ok': False,
            'error': {
                'code': 'BAD_REQUEST',
                'message': str(e)
            }
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({
            'ok': False,
            'error': {
                'code': 'UNAUTHORIZED',
                'message': 'Authentication required'
            }
        }), 401
    
    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({
            'ok': False,
            'error': {
                'code': 'FORBIDDEN',
                'message': 'Access denied'
            }
        }), 403
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            'ok': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Resource not found'
            }
        }), 404
    
    @app.errorhandler(409)
    def conflict(e):
        return jsonify({
            'ok': False,
            'error': {
                'code': 'CONFLICT',
                'message': str(e)
            }
        }), 409
    
    @app.errorhandler(422)
    def validation_error(e):
        return jsonify({
            'ok': False,
            'error': {
                'code': 'VALIDATION_FAILED',
                'message': str(e)
            }
        }), 422
    
    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({
            'ok': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500
