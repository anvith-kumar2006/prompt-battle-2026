"""Ride-request matching service."""
from datetime import datetime, timedelta

from backend.app.extensions import db
from backend.app.models import Vehicle, Driver, Allocation
from backend.app.services.geo import haversine_km


def find_eligible_vehicles(ride_request, travel_date):
    """Return vehicles whose driver and vehicle are fully approved and in-radius."""
    vehicles = (
        Vehicle.query
        .join(Driver, Vehicle.driver_id == Driver.id)
        .filter(
            Driver.status == 'APPROVED',
            Vehicle.status == 'APPROVED',
            Driver.availability == 'AVAILABLE',
            Driver.licence_expiry >= travel_date,
            Vehicle.permit_expiry >= travel_date,
            Vehicle.insurance_expiry >= travel_date,
            Vehicle.fitness_expiry >= travel_date,
        )
        .all()
    )

    eligible = []
    for vehicle in vehicles:
        try:
            dist = haversine_km(
                float(vehicle.base_lat), float(vehicle.base_lng),
                float(ride_request.pickup_lat), float(ride_request.pickup_lng),
            )
            if dist <= float(vehicle.service_radius_km):
                eligible.append(vehicle)
        except (TypeError, ValueError):
            pass

    return eligible


def check_capacity(vehicle, seats_needed, window_start, window_end):
    """
    With a row-lock on the vehicle record, return (has_capacity, remaining_seats).
    CRITICAL: uses SELECT … FOR UPDATE to prevent double-booking.
    """
    locked_vehicle = (
        db.session.query(Vehicle)
        .filter_by(id=vehicle.id)
        .with_for_update()
        .first()
    )

    overlapping = Allocation.query.filter(
        Allocation.vehicle_id == vehicle.id,
        Allocation.status.in_(['PROPOSED', 'CONFIRMED']),
        Allocation.window_start < window_end,
        Allocation.window_end > window_start,
    ).all()

    used_seats = sum(a.seats_reserved for a in overlapping)
    remaining = locked_vehicle.permitted_capacity - used_seats

    return remaining >= seats_needed, remaining


def score_candidate(vehicle, ride_request):
    """Simple composite score [0-1]; higher = better match."""
    try:
        dist = haversine_km(
            float(vehicle.base_lat), float(vehicle.base_lng),
            float(ride_request.pickup_lat), float(ride_request.pickup_lng),
        )
        proximity = max(0.0, 1.0 - dist / float(vehicle.service_radius_km))
    except (TypeError, ValueError):
        proximity = 0.0

    return 0.60 * proximity + 0.25 * 1.0 + 0.15


def match_ride_request(ride_request):
    """Return up to 3 candidate {vehicle, driver, score, remaining_capacity} dicts."""
    from backend.app.models import RideRequestStudent

    seats_needed = (
        db.session.query(RideRequestStudent)
        .filter_by(request_id=ride_request.id)
        .count()
    )

    pickup_dt = datetime.combine(ride_request.travel_date, ride_request.pickup_time)
    window_start = pickup_dt - timedelta(minutes=15)
    window_end = pickup_dt + timedelta(hours=2)

    vehicles = find_eligible_vehicles(ride_request, ride_request.travel_date)

    candidates = []
    for vehicle in vehicles:
        has_cap, remaining = check_capacity(vehicle, seats_needed, window_start, window_end)
        if has_cap:
            candidates.append({
                'vehicle': vehicle,
                'driver': vehicle.driver,
                'score': score_candidate(vehicle, ride_request),
                'remaining_capacity': remaining,
            })

    candidates.sort(key=lambda x: x['score'], reverse=True)
    return candidates[:3]
