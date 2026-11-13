-- SETU Database Schema
-- MySQL 8.0, InnoDB, utf8mb4

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS incidents;
DROP TABLE IF EXISTS journey_events;
DROP TABLE IF EXISTS location_updates;
DROP TABLE IF EXISTS otp_challenges;
DROP TABLE IF EXISTS trip_passengers;
DROP TABLE IF EXISTS trips;
DROP TABLE IF EXISTS guardian_consents;
DROP TABLE IF EXISTS allocations;
DROP TABLE IF EXISTS ride_request_students;
DROP TABLE IF EXISTS ride_requests;
DROP TABLE IF EXISTS transport_disruptions;
DROP TABLE IF EXISTS routes;
DROP TABLE IF EXISTS provider_documents;
DROP TABLE IF EXISTS vehicles;
DROP TABLE IF EXISTS drivers;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS institutions;
DROP TABLE IF EXISTS users;

SET FOREIGN_KEY_CHECKS = 1;

-- Users table
CREATE TABLE users (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    role ENUM('GUARDIAN', 'STUDENT_ADULT', 'DRIVER', 'INSTITUTION_STAFF', 'ADMIN', 'SAFETY_ADMIN', 'OPERATOR') NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    phone VARCHAR(16) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    status ENUM('ACTIVE', 'SUSPENDED') DEFAULT 'ACTIVE',
    institution_id BIGINT UNSIGNED NULL,
    failed_logins INT DEFAULT 0,
    locked_until DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role_status (role, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Institutions table
CREATE TABLE institutions (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    type ENUM('SCHOOL', 'PU', 'COLLEGE') NOT NULL,
    address TEXT,
    lat DECIMAL(9,6),
    lng DECIMAL(9,6),
    contact_phone VARCHAR(16),
    status ENUM('PENDING', 'VERIFIED', 'SUSPENDED') DEFAULT 'PENDING',
    allows_adult_self_booking BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE users ADD CONSTRAINT fk_users_institution 
    FOREIGN KEY (institution_id) REFERENCES institutions(id) ON DELETE SET NULL;

-- Students table
CREATE TABLE students (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    guardian_id BIGINT UNSIGNED NOT NULL,
    institution_id BIGINT UNSIGNED NOT NULL,
    first_name VARCHAR(60) NOT NULL,
    class_label VARCHAR(30),
    dob DATE,
    age_category ENUM('MINOR_PRIMARY', 'MINOR_SECONDARY', 'ADULT') NOT NULL,
    status ENUM('ACTIVE', 'INACTIVE', 'ARCHIVED') DEFAULT 'ACTIVE',
    default_route_id BIGINT UNSIGNED NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (guardian_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (institution_id) REFERENCES institutions(id) ON DELETE RESTRICT,
    INDEX idx_guardian_status (guardian_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Drivers table
CREATE TABLE drivers (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED UNIQUE NOT NULL,
    category ENUM('SCHOOL_APPROVED', 'COMMUNITY') NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    licence_no VARCHAR(32) UNIQUE NOT NULL,
    licence_class VARCHAR(20),
    licence_expiry DATE NOT NULL,
    status ENUM('PENDING', 'APPROVED', 'REJECTED', 'SUSPENDED') DEFAULT 'PENDING',
    availability ENUM('AVAILABLE', 'UNAVAILABLE') DEFAULT 'UNAVAILABLE',
    verification_notes TEXT,
    verified_by BIGINT UNSIGNED NULL,
    verified_at DATETIME NULL,
    is_simulated_verification BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_status_availability (status, availability)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Vehicles table
CREATE TABLE vehicles (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    driver_id BIGINT UNSIGNED NOT NULL,
    reg_no VARCHAR(16) UNIQUE NOT NULL,
    type ENUM('BUS', 'VAN', 'AUTO') NOT NULL,
    permitted_capacity TINYINT UNSIGNED NOT NULL CHECK (permitted_capacity BETWEEN 1 AND 60),
    permit_expiry DATE,
    insurance_expiry DATE,
    fitness_expiry DATE,
    base_lat DECIMAL(9,6),
    base_lng DECIMAL(9,6),
    service_radius_km DECIMAL(5,2) DEFAULT 10.00,
    status ENUM('PENDING', 'APPROVED', 'REJECTED', 'SUSPENDED') DEFAULT 'PENDING',
    verified_by BIGINT UNSIGNED NULL,
    verified_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (driver_id) REFERENCES drivers(id) ON DELETE CASCADE,
    FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_status_location (status, base_lat, base_lng)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Provider documents table
CREATE TABLE provider_documents (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    owner_type ENUM('DRIVER', 'VEHICLE') NOT NULL,
    owner_id BIGINT UNSIGNED NOT NULL,
    doc_type ENUM('LICENCE', 'RC', 'INSURANCE', 'PERMIT', 'FITNESS', 'POLICE_CLEARANCE') NOT NULL,
    doc_number VARCHAR(50),
    expiry_date DATE NULL,
    file_path VARCHAR(255) NULL,
    status ENUM('SUBMITTED', 'ACCEPTED', 'REJECTED') DEFAULT 'SUBMITTED',
    reviewed_by BIGINT UNSIGNED NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Routes table
CREATE TABLE routes (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120),
    institution_id BIGINT UNSIGNED NULL,
    origin_lat DECIMAL(9,6),
    origin_lng DECIMAL(9,6),
    dest_lat DECIMAL(9,6),
    dest_lng DECIMAL(9,6),
    polyline_json JSON NOT NULL,
    distance_m INT,
    is_template BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (institution_id) REFERENCES institutions(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Transport disruptions table
CREATE TABLE transport_disruptions (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    route_id BIGINT UNSIGNED NULL,
    stop_label VARCHAR(120),
    type ENUM('CANCELLED', 'DELAYED', 'ROUTE_DISRUPTED', 'OVERCROWDED') NOT NULL,
    starts_at DATETIME NOT NULL,
    ends_at DATETIME NULL,
    note TEXT,
    reported_by BIGINT UNSIGNED NOT NULL,
    source ENUM('MANUAL', 'DEMO') DEFAULT 'MANUAL',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE SET NULL,
    FOREIGN KEY (reported_by) REFERENCES users(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Ride requests table
CREATE TABLE ride_requests (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    guardian_id BIGINT UNSIGNED NOT NULL,
    institution_id BIGINT UNSIGNED,
    pickup_lat DECIMAL(9,6) NOT NULL,
    pickup_lng DECIMAL(9,6) NOT NULL,
    pickup_label VARCHAR(200),
    dest_lat DECIMAL(9,6) NOT NULL,
    dest_lng DECIMAL(9,6) NOT NULL,
    dest_label VARCHAR(200),
    travel_date DATE NOT NULL,
    pickup_time TIME NOT NULL,
    shared_ok BOOLEAN DEFAULT FALSE,
    disruption_id BIGINT UNSIGNED NULL,
    status ENUM('SUBMITTED', 'NO_MATCH', 'PROPOSED', 'CONFIRMED', 'REJECTED_BY_PARENT', 'EXPIRED', 'CANCELLED', 'COMPLETED') DEFAULT 'SUBMITTED',
    expires_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (guardian_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (institution_id) REFERENCES institutions(id) ON DELETE SET NULL,
    FOREIGN KEY (disruption_id) REFERENCES transport_disruptions(id) ON DELETE SET NULL,
    INDEX idx_guardian_status (guardian_id, status),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Ride request students (junction table)
CREATE TABLE ride_request_students (
    request_id BIGINT UNSIGNED NOT NULL,
    student_id BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (request_id, student_id),
    FOREIGN KEY (request_id) REFERENCES ride_requests(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Allocations table
CREATE TABLE allocations (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    request_id BIGINT UNSIGNED NOT NULL,
    vehicle_id BIGINT UNSIGNED NOT NULL,
    driver_id BIGINT UNSIGNED NOT NULL,
    seats_reserved TINYINT UNSIGNED NOT NULL,
    score DECIMAL(6,3),
    window_start DATETIME,
    window_end DATETIME,
    status ENUM('PROPOSED', 'CONFIRMED', 'RELEASED', 'EXPIRED') DEFAULT 'PROPOSED',
    hold_expires_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES ride_requests(id) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE RESTRICT,
    FOREIGN KEY (driver_id) REFERENCES drivers(id) ON DELETE RESTRICT,
    INDEX idx_vehicle_window (vehicle_id, window_start, window_end),
    INDEX idx_request_status (request_id, status),
    INDEX idx_status_expires (status, hold_expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Guardian consents table
CREATE TABLE guardian_consents (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    allocation_id BIGINT UNSIGNED UNIQUE NOT NULL,
    guardian_id BIGINT UNSIGNED NOT NULL,
    status ENUM('PENDING', 'APPROVED', 'REJECTED', 'EXPIRED') DEFAULT 'PENDING',
    consent_text_version VARCHAR(16) DEFAULT 'v1',
    decided_at DATETIME NULL,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (allocation_id) REFERENCES allocations(id) ON DELETE CASCADE,
    FOREIGN KEY (guardian_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Trips table
CREATE TABLE trips (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    allocation_id BIGINT UNSIGNED UNIQUE NOT NULL,
    vehicle_id BIGINT UNSIGNED NOT NULL,
    driver_id BIGINT UNSIGNED NOT NULL,
    status ENUM('SCHEDULED', 'EN_ROUTE_TO_PICKUP', 'AT_PICKUP', 'IN_PROGRESS', 'ARRIVED', 'COMPLETED', 'CANCELLED', 'ABORTED') DEFAULT 'SCHEDULED',
    planned_pickup_at DATETIME NOT NULL,
    pickup_lat DECIMAL(9,6) NOT NULL,
    pickup_lng DECIMAL(9,6) NOT NULL,
    dest_lat DECIMAL(9,6) NOT NULL,
    dest_lng DECIMAL(9,6) NOT NULL,
    destination_institution_id BIGINT UNSIGNED NULL,
    route_polyline_json JSON,
    corridor_radius_m INT DEFAULT 500,
    deviation_state JSON NULL,
    pickup_at DATETIME NULL,
    pickup_actual_lat DECIMAL(9,6) NULL,
    pickup_actual_lng DECIMAL(9,6) NULL,
    dropoff_at DATETIME NULL,
    dropoff_actual_lat DECIMAL(9,6) NULL,
    dropoff_actual_lng DECIMAL(9,6) NULL,
    handover_method ENUM('OTP', 'STAFF_CONFIRM', 'ADMIN_OVERRIDE') NULL,
    handover_by BIGINT UNSIGNED NULL,
    last_ping_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (allocation_id) REFERENCES allocations(id) ON DELETE RESTRICT,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE RESTRICT,
    FOREIGN KEY (driver_id) REFERENCES drivers(id) ON DELETE RESTRICT,
    FOREIGN KEY (destination_institution_id) REFERENCES institutions(id) ON DELETE SET NULL,
    FOREIGN KEY (handover_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_driver_status (driver_id, status),
    INDEX idx_status_last_ping (status, last_ping_at),
    INDEX idx_planned_pickup (planned_pickup_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Trip passengers table
CREATE TABLE trip_passengers (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    trip_id BIGINT UNSIGNED NOT NULL,
    student_id BIGINT UNSIGNED NOT NULL,
    pickup_confirmed_at DATETIME NULL,
    dropoff_confirmed_at DATETIME NULL,
    UNIQUE KEY unique_trip_student (trip_id, student_id),
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- OTP challenges table
CREATE TABLE otp_challenges (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    trip_id BIGINT UNSIGNED NOT NULL,
    purpose ENUM('PICKUP', 'DROPOFF') NOT NULL,
    code_hash CHAR(64) NOT NULL,
    expires_at DATETIME NOT NULL,
    attempts TINYINT DEFAULT 0,
    max_attempts TINYINT DEFAULT 5,
    status ENUM('ACTIVE', 'CONSUMED', 'EXPIRED', 'LOCKED', 'SUPERSEDED') DEFAULT 'ACTIVE',
    consumed_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE,
    INDEX idx_trip_purpose_status (trip_id, purpose, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Location updates table
CREATE TABLE location_updates (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    trip_id BIGINT UNSIGNED NOT NULL,
    driver_id BIGINT UNSIGNED NOT NULL,
    lat DECIMAL(9,6) NOT NULL,
    lng DECIMAL(9,6) NOT NULL,
    accuracy_m FLOAT,
    speed_mps FLOAT NULL,
    heading FLOAT NULL,
    client_ts DATETIME(3),
    server_ts DATETIME(3) NOT NULL,
    dist_from_route_m FLOAT NULL,
    in_corridor BOOLEAN NULL,
    flags SET('LOW_ACCURACY', 'CLOCK_SKEW', 'IMPLAUSIBLE', 'DUPLICATE') NULL,
    is_simulated BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE,
    FOREIGN KEY (driver_id) REFERENCES drivers(id) ON DELETE CASCADE,
    INDEX idx_trip_server_ts (trip_id, server_ts DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Journey events table
CREATE TABLE journey_events (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    trip_id BIGINT UNSIGNED NOT NULL,
    event_type VARCHAR(40) NOT NULL,
    severity ENUM('INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL') DEFAULT 'INFO',
    payload_json JSON,
    actor_user_id BIGINT UNSIGNED NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE,
    FOREIGN KEY (actor_user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_trip_created (trip_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Incidents table
CREATE TABLE incidents (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    trip_id BIGINT UNSIGNED NOT NULL,
    severity ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') NOT NULL,
    status ENUM('OPEN', 'ACKNOWLEDGED', 'ESCALATED', 'RESOLVED') DEFAULT 'OPEN',
    cause_hint ENUM('GPS_ERROR_SUSPECTED', 'SIGNAL_LOSS', 'TRAFFIC_DIVERSION', 'ROAD_CLOSURE', 'UNEXPLAINED_PERSISTENT_DEVIATION', 'EMERGENCY_REPORTED', 'OTHER') DEFAULT 'UNEXPLAINED_PERSISTENT_DEVIATION',
    source ENUM('ENGINE', 'DRIVER_SOS', 'GUARDIAN_CONCERN', 'ADMIN') DEFAULT 'ENGINE',
    last_lat DECIMAL(9,6),
    last_lng DECIMAL(9,6),
    last_seen_at DATETIME,
    driver_reason VARCHAR(40) NULL,
    opened_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    acknowledged_by BIGINT UNSIGNED NULL,
    acknowledged_at DATETIME NULL,
    escalation_note TEXT NULL,
    escalated_at DATETIME NULL,
    resolved_by BIGINT UNSIGNED NULL,
    resolved_at DATETIME NULL,
    resolution_type ENUM('FALSE_ALARM', 'TRAFFIC_OR_ROAD', 'DRIVER_EXPLAINED', 'SAFETY_CONCERN_CONFIRMED', 'EMERGENCY_HANDLED') NULL,
    resolution_notes TEXT,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE,
    FOREIGN KEY (acknowledged_by) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (resolved_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_status_severity_opened (status, severity, opened_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Notifications table
CREATE TABLE notifications (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL,
    channel ENUM('EMAIL', 'IN_APP') NOT NULL,
    template VARCHAR(40) NOT NULL,
    subject VARCHAR(200),
    payload_json JSON,
    status ENUM('QUEUED', 'SENT', 'FAILED', 'READ') DEFAULT 'QUEUED',
    attempts TINYINT DEFAULT 0,
    last_error VARCHAR(255),
    related_type VARCHAR(30),
    related_id BIGINT UNSIGNED,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    sent_at DATETIME NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_status_created (status, created_at),
    INDEX idx_user_status (user_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Audit logs table
CREATE TABLE audit_logs (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    actor_user_id BIGINT UNSIGNED NULL,
    action VARCHAR(60) NOT NULL,
    entity_type VARCHAR(30),
    entity_id BIGINT UNSIGNED,
    detail_json JSON,
    ip_address VARCHAR(45),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (actor_user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_entity (entity_type, entity_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
