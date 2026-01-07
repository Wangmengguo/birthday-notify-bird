"""
Application settings loaded from environment variables.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if exists
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/birthday.db")

# Email settings
TO_EMAIL = os.getenv("TO_EMAIL", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "")

# SMTP settings
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_MODE = os.getenv("SMTP_MODE", "starttls")  # starttls, ssl, plain

# Schedule settings
TIMEZONE = os.getenv("TIMEZONE", "Asia/Shanghai")
DAILY_RUN_AT = os.getenv("DAILY_RUN_AT", "09:00")

# Optional
BASE_URL = os.getenv("BASE_URL", "")
ROOT_PATH = os.getenv("ROOT_PATH", "")  # 子路径，如 /birthday


def validate_email_settings() -> tuple[bool, str]:
    """Validate that required email settings are configured."""
    missing = []
    if not TO_EMAIL:
        missing.append("TO_EMAIL")
    if not FROM_EMAIL:
        missing.append("FROM_EMAIL")
    if not SMTP_USERNAME:
        missing.append("SMTP_USERNAME")
    if not SMTP_PASSWORD:
        missing.append("SMTP_PASSWORD")
    
    if missing:
        return False, f"Missing required settings: {', '.join(missing)}"
    return True, "OK"

