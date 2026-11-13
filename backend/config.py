import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://setu_user:password@localhost:3306/setu?charset=utf8mb4'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Security
    OTP_PEPPER = os.getenv('OTP_PEPPER', 'change-me-in-production')
    SESSION_COOKIE_SECURE = FLASK_ENV == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = int(os.getenv('SESSION_IDLE_MINUTES', 30)) * 60
    
    # Email
    MAIL_SERVER = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('SMTP_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv('SMTP_USER')
    MAIL_PASSWORD = os.getenv('SMTP_APP_PASSWORD')
    MAIL_DEFAULT_SENDER = (os.getenv('MAIL_FROM_NAME', 'SETU'), os.getenv('SMTP_USER'))
    
    # Gemini (optional)
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
    
    # Features
    ENABLE_SIMULATION = os.getenv('ENABLE_SIMULATION', 'true').lower() == 'true'
    
    # Safety Engine
    CORRIDOR_RADIUS_M = int(os.getenv('CORRIDOR_RADIUS_M', 500))
    PERSIST_SECONDS = int(os.getenv('PERSIST_SECONDS', 20))
    PERSIST_PINGS = int(os.getenv('PERSIST_PINGS', 3))
    MAX_ACCURACY_M = int(os.getenv('MAX_ACCURACY_M', 100))
    SIGNAL_LOSS_SECONDS = int(os.getenv('SIGNAL_LOSS_SECONDS', 90))
    SIGNAL_LOSS_ESCALATE_S = int(os.getenv('SIGNAL_LOSS_ESCALATE_S', 300))
    MAX_SPEED_KMH = int(os.getenv('MAX_SPEED_KMH', 120))
    
    # Service Area
    SERVICE_AREA_BBOX = os.getenv('SERVICE_AREA_BBOX', '12.80,77.40,13.20,77.80')
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = 'memory://'
    RATELIMIT_ENABLED = True
