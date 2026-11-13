"""Security decorators for SETU API."""
from functools import wraps
from flask import abort
from flask_login import current_user


def login_required(f):
    """Require authenticated user."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        return f(*args, **kwargs)
    return decorated


def roles_required(*roles):
    """Require one of the given roles."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not current_user.has_role(*roles):
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator


def owns_student(student_id_param='student_id'):
    """Check that the current guardian owns the student."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            student_id = kwargs.get(student_id_param)
            from backend.app.models import Student
            student = Student.query.get_or_404(student_id)
            if (student.guardian_id != current_user.id and
                    current_user.role not in ['ADMIN', 'SAFETY_ADMIN']):
                abort(404)  # Don't reveal existence
            return f(*args, **kwargs)
        return decorated
    return decorator
