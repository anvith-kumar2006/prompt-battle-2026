"""Notification queuing and email background worker."""
import time
from datetime import datetime

from backend.app.extensions import db, mail
from backend.app.models import Notification


def queue_notification(user_id, template, subject, payload,
                        related_type=None, related_id=None):
    """Queue an EMAIL + IN_APP notification pair."""
    # Email (processed by background worker)
    email_notif = Notification(
        user_id=user_id,
        channel='EMAIL',
        template=template,
        subject=subject,
        payload_json=payload,
        related_type=related_type,
        related_id=related_id,
        status='QUEUED',
    )
    db.session.add(email_notif)

    # In-app (immediately visible)
    app_notif = Notification(
        user_id=user_id,
        channel='IN_APP',
        template=template,
        subject=subject,
        payload_json=payload,
        related_type=related_type,
        related_id=related_id,
        status='SENT',
    )
    db.session.add(app_notif)
    db.session.commit()


def send_email(notification):
    """Send a single email notification via Flask-Mail."""
    from flask_mail import Message
    from flask import current_app
    from backend.app.models import User

    user = User.query.get(notification.user_id)
    if not user:
        return

    msg = Message(
        subject=notification.subject,
        recipients=[user.email],
        body=(
            f"Dear {user.name},\n\n"
            f"You have a new notification from SETU.\n\n"
            f"Please log in to view details: {current_app.config['BASE_URL']}\n\n"
            "— SETU Team"
        ),
    )
    mail.send(msg)


def start_email_worker(app):
    """Background daemon that drains the email queue every 2 seconds."""
    with app.app_context():
        while True:
            try:
                pending = (
                    Notification.query
                    .filter_by(channel='EMAIL', status='QUEUED')
                    .limit(10)
                    .all()
                )

                for notif in pending:
                    try:
                        send_email(notif)
                        notif.status = 'SENT'
                        notif.sent_at = datetime.utcnow()
                    except Exception as exc:
                        notif.status = 'FAILED'
                        notif.last_error = str(exc)[:255]
                        notif.attempts = (notif.attempts or 0) + 1
                    db.session.commit()

                time.sleep(2)
            except Exception as exc:
                import sys
                print(f"[email-worker] error: {exc}", file=sys.stderr)
                time.sleep(5)


def notify_deviation(trip, incident):
    """Alert guardians of passengers about a route deviation."""
    for passenger in trip.passengers:
        try:
            queue_notification(
                user_id=passenger.student.guardian_id,
                template='ROUTE_DEVIATION',
                subject='SETU Alert: Route Deviation Detected',
                payload={'trip_id': trip.id, 'incident_id': incident.id},
                related_type='incident',
                related_id=incident.id,
            )
        except Exception:
            pass  # Notification failure must not block the transaction
