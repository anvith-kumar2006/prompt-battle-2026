# SETU — Parent-Connected Rural Student Mobility & Safety Platform

**Safe Journeys. Connected Families. Accountable Transportation.**

## Overview

SETU enables parents/guardians to arrange verified, consent-based, trackable alternative transport for students when government buses are disrupted. The child needs no smartphone — tracking comes from the driver's device. Pickup and drop-off are verified via OTP and authorised handover.

## Quick Start

### Prerequisites
- Python 3.10+
- MySQL 8.0+
- Node.js 18+ (for TypeScript compilation only)

### Installation

1. **Clone and navigate:**
```powershell
cd d:\Projects\prompt-battle-2026
```

2. **Install Python dependencies:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. **Install TypeScript compiler:**
```powershell
npm install
```

4. **Setup MySQL database:**
```powershell
# Create database
mysql -u root -p
CREATE DATABASE setu CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'setu_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON setu.* TO 'setu_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# Load schema
mysql -u setu_user -p setu < db/schema.sql

# Load seed data
mysql -u setu_user -p setu < db/seed.sql
```

5. **Configure environment:**
```powershell
cp .env.example .env
# Edit .env with your settings
```

6. **Compile TypeScript:**
```powershell
npm run build
```

7. **Run the application:**
```powershell
python backend/wsgi.py
```

8. **Access the application:**
```
http://localhost:5000
```

## Demo Accounts (from seed data)

- **Guardian:** lakshmi@example.com / Password123!
- **Driver:** suresh@example.com / Password123!
- **Admin:** admin@setu.org / Admin123!
- **Safety Admin:** safety@setu.org / Safety123!

## Project Structure

```
setu/
├── backend/            # Flask application
│   ├── app/
│   │   ├── api/        # REST API blueprints
│   │   ├── models/     # SQLAlchemy models
│   │   ├── services/   # Business logic
│   │   ├── security/   # Auth decorators
│   │   ├── templates/  # Jinja2 templates
│   │   └── static/     # CSS, compiled JS
│   ├── config.py       # Configuration
│   └── wsgi.py         # Entry point
├── frontend/           # TypeScript source
│   └── src/
├── db/                 # Database scripts
├── docs/               # Specifications
└── tests/              # Test suite
```

## Technology Stack

- **Backend:** Python, Flask, SQLAlchemy, PyMySQL
- **Database:** MySQL 8 (InnoDB)
- **Frontend:** TypeScript, Leaflet, OpenStreetMap
- **Auth:** Flask-Login, Werkzeug password hashing
- **Email:** Gmail SMTP (Flask-Mail)
- **Optional:** Gemini API (explanations)

## Key Features (P0 MVP)

✓ Guardian/driver/admin registration and authentication
✓ Student management with age categories
✓ Provider & vehicle registration with admin approval
✓ Interactive map for pickup/destination selection
✓ Capacity-aware ride matching with transaction locks
✓ Guardian consent gate before trip assignment
✓ OTP-verified pickup and drop-off
✓ Browser-based GPS tracking
✓ Route deviation detection with persistence
✓ Incident management workflow
✓ Email notifications with in-app fallback

## Development

### Run tests:
```powershell
pytest
```

### TypeScript watch mode:
```powershell
npm run watch
```

### Database migrations:
```powershell
# Manual: edit db/schema.sql and reload
mysql -u setu_user -p setu < db/schema.sql
```

## Important Notes

- **SIMULATED VERIFICATION:** Provider/vehicle approval is simulated in this prototype
- **FOREGROUND GPS ONLY:** Browser tracking works only while tab is active
- **DEMO MODE:** Simulation buttons for drive/deviation testing
- **EMAIL SECONDARY:** Gmail SMTP for demo; production needs SMS/voice
- **NO PRODUCTION USE:** Legal review and security audit required

## Documentation

See `docs/` folder:
- `PROJECT_OVERVIEW.md` — Concept and scope
- `prd.md` — Product requirements
- `frd.md` — Functional requirements
- `TRD.md` — Technical requirements
- `REQUIREMENTS_TRACEABILITY.md` — Traceability and assumptions

## License

Educational hackathon project - 2026
