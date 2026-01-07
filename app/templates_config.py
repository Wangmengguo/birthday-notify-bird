"""
Shared templates configuration for all routes.
"""
from pathlib import Path
from fastapi.templating import Jinja2Templates

from app import settings

# Template directory
TEMPLATES_DIR = Path(__file__).parent / "templates"

# Create templates instance
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Add root_path helper function to template context
def url_for_with_root(path: str) -> str:
    """Helper to add root_path prefix to URLs."""
    root = settings.ROOT_PATH.rstrip("/")
    path = path if path.startswith("/") else f"/{path}"
    return f"{root}{path}"

# Register global functions
templates.env.globals["url_for_path"] = url_for_with_root
templates.env.globals["root_path"] = settings.ROOT_PATH

