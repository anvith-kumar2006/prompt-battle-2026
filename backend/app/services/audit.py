"""Audit logging helper — wraps AuditLog.log() for convenience."""
from backend.app.models import AuditLog
from backend.app.extensions import db


def log_action(actor_id, action, entity_type=None, entity_id=None, detail=None, ip=None):
    """Append an audit entry. Silently absorbs errors so the caller never fails."""
    try:
        AuditLog.log(
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=detail,
            ip=ip,
        )
        # Flush without committing — the calling code owns the transaction
        db.session.flush()
    except Exception as exc:
        import sys
        print(f"[audit] WARNING: could not write audit entry: {exc}", file=sys.stderr)
