"""Geographical utility functions for SETU."""
import math


def haversine_km(lat1, lon1, lat2, lon2):
    """Calculate great-circle distance in kilometres."""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (math.sin(dphi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def point_to_segment_distance_m(px, py, x1, y1, x2, y2):
    """Minimum distance in metres from point (px,py) to segment (x1,y1)-(x2,y2)."""
    dist_to_start = haversine_km(px, py, x1, y1) * 1000
    dist_to_end = haversine_km(px, py, x2, y2) * 1000

    # Project onto segment
    dx, dy = x2 - x1, y2 - y1
    seg_len_sq = dx * dx + dy * dy
    if seg_len_sq == 0:
        return dist_to_start

    t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / seg_len_sq))
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    return haversine_km(px, py, proj_x, proj_y) * 1000


def distance_to_polyline(lat, lng, polyline):
    """Minimum distance in metres from point to a polyline [[lat,lng],...]."""
    if not polyline or len(polyline) < 2:
        if polyline:
            return haversine_km(lat, lng, polyline[0][0], polyline[0][1]) * 1000
        return float('inf')

    min_dist = float('inf')
    for i in range(len(polyline) - 1):
        p1, p2 = polyline[i], polyline[i + 1]
        dist = point_to_segment_distance_m(lat, lng, p1[0], p1[1], p2[0], p2[1])
        min_dist = min(min_dist, dist)
    return min_dist
