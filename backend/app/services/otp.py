"""OTP generation, issuance, and verification."""
import secrets
import hashlib
import hmac
from datetime import datetime, timedelta

from flask import current_app

from backend.app.extensions import db
from backend.app.models import OTPChallenge


def generate_otp():
    """Generate a 6-digit OTP string."""
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_otp(otp_id, code):
    """HMAC-SHA256 hash of the OTP using pepper + challenge id."""
    pepper = current_app.config['OTP_PEPPER'].encode()
    message = f"{otp_id}:{code}".encode()
    return hmac.new(pepper, message, hashlib.sha256).hexdigest()


def issue_otp(trip, purpose):
    """Issue a fresh OTP for a trip, superseding any previous active one."""
    # Supersede previous active OTPs for this purpose
    OTPChallenge.query.filter_by(
        trip_id=trip.id,
        purpose=purpose,
        status='ACTIVE'
    ).update({'status': 'SUPERSEDED'})

    code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    challenge = OTPChallenge(
        trip_id=trip.id,
        purpose=purpose,
        code_hash='',  # Filled after flush gives us the id
        expires_at=expires_at,
        status='ACTIVE'
    )
    db.session.add(challenge)
    db.session.flush()  # Assign PK

    challenge.code_hash = hash_otp(challenge.id, code)
    db.session.commit()

    return code, challenge


def verify_otp(trip, purpose, submitted_code):
    """Verify an OTP. Returns (success: bool, message: str, challenge)."""
    challenge = (
        OTPChallenge.query
        .filter_by(trip_id=trip.id, purpose=purpose, status='ACTIVE')
        .with_for_update()
        .first()
    )

    if not challenge:
        return False, "No active OTP found", None

    if datetime.utcnow() > challenge.expires_at:
        challenge.status = 'EXPIRED'
        db.session.commit()
        return False, "OTP expired", challenge

    if challenge.attempts >= challenge.max_attempts:
        challenge.status = 'LOCKED'
        db.session.commit()
        return False, "OTP locked – too many attempts", challenge

    challenge.attempts += 1

    submitted_hash = hash_otp(challenge.id, submitted_code)
    if hmac.compare_digest(challenge.code_hash, submitted_hash):
        challenge.status = 'CONSUMED'
        challenge.consumed_at = datetime.utcnow()
        db.session.commit()
        return True, "OTP verified", challenge
    else:
        db.session.commit()
        remaining = challenge.max_attempts - challenge.attempts
        return False, f"Invalid OTP ({remaining} attempts remaining)", challenge
