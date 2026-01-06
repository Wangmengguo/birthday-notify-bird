"""
Birthday Notify Bird - Main FastAPI Application
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app import settings

# Template directory
TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"

# Ensure directories exist
TEMPLATES_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - startup and shutdown."""
    # Startup
    print("🐦 Birthday Notify Bird starting...")
    print(f"   Timezone: {settings.TIMEZONE}")
    print(f"   Daily run at: {settings.DAILY_RUN_AT}")
    
    # Initialize database
    from app.db import init_db
    init_db()
    
    # Start scheduler
    from app.scheduler import start_scheduler
    start_scheduler()
    
    # Validate email settings
    valid, msg = settings.validate_email_settings()
    if not valid:
        print(f"   ⚠️  Email not configured: {msg}")
    else:
        print(f"   ✅ Email configured: {settings.TO_EMAIL}")
    
    yield
    
    # Shutdown
    from app.scheduler import stop_scheduler
    stop_scheduler()
    print("🐦 Birthday Notify Bird shutting down...")


app = FastAPI(
    title="Birthday Notify Bird",
    description="生日提醒小助手 - 提前7天/1天/当天邮件提醒",
    version="0.1.0",
    lifespan=lifespan,
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Include routers
from app.routes import contacts, logs
app.include_router(contacts.router)
app.include_router(logs.router)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Home page."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Birthday Notify Bird",
            "daily_run_at": settings.DAILY_RUN_AT,
            "timezone": settings.TIMEZONE,
        }
    )


@app.get("/health")
async def health():
    """Health check endpoint."""
    valid, msg = settings.validate_email_settings()
    return {
        "status": "ok",
        "email_configured": valid,
        "timezone": settings.TIMEZONE,
        "daily_run_at": settings.DAILY_RUN_AT,
    }

