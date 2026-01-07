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

# Add root_path to template context
def url_for_with_root(path: str) -> str:
    """Helper to add root_path prefix to URLs."""
    root = settings.ROOT_PATH.rstrip("/")
    path = path if path.startswith("/") else f"/{path}"
    return f"{root}{path}"

templates.env.globals["url_for_path"] = url_for_with_root
templates.env.globals["root_path"] = settings.ROOT_PATH


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
    root_path=settings.ROOT_PATH,  # 支持子路径部署
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


@app.get("/api/test-email")
async def test_email():
    """Send a test email to verify email configuration."""
    from app.emailer import send_email
    from datetime import date
    
    # Create a test email
    test_subject = "🧪 Birthday Notify Bird - 测试邮件"
    test_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 500px; margin: 0 auto; padding: 20px; background: #f5f5f5;">
        <div style="background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="text-align: center; font-size: 48px; margin-bottom: 20px;">🧪</div>
            
            <h1 style="text-align: center; color: #333; margin: 0 0 10px 0; font-size: 24px;">
                测试邮件发送成功！
            </h1>
            
            <p style="text-align: center; color: #666; margin: 0 0 30px 0;">
                如果你收到这封邮件，说明邮件配置正确 ✅
            </p>
            
            <div style="background: #f8f9fa; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                <p style="color: #333; margin: 0;">
                    这是一封测试邮件，用于验证 Birthday Notify Bird 的邮件发送功能是否正常工作。
                </p>
            </div>
            
            <p style="text-align: center; color: #888; font-size: 14px; margin: 0;">
                邮件配置信息：
            </p>
            <ul style="color: #666; font-size: 14px;">
                <li>SMTP 服务器: {smtp_host}:{smtp_port}</li>
                <li>SMTP 模式: {smtp_mode}</li>
                <li>发送邮箱: {from_email}</li>
                <li>接收邮箱: {to_email}</li>
            </ul>
        </div>
        
        <p style="text-align: center; color: #aaa; font-size: 12px; margin-top: 20px;">
            Birthday Notify Bird 🐦
        </p>
    </body>
    </html>
    """.format(
        smtp_host=settings.SMTP_HOST,
        smtp_port=settings.SMTP_PORT,
        smtp_mode=settings.SMTP_MODE,
        from_email=settings.FROM_EMAIL,
        to_email=settings.TO_EMAIL
    )
    
    success, error_msg = send_email(settings.TO_EMAIL, test_subject, test_html)
    
    if success:
        return {
            "status": "success",
            "message": f"测试邮件已成功发送到 {settings.TO_EMAIL}",
            "to_email": settings.TO_EMAIL,
        }
    else:
        return {
            "status": "error",
            "message": f"邮件发送失败: {error_msg}",
            "to_email": settings.TO_EMAIL,
        }

