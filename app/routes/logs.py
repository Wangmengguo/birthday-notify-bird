"""
Email log viewing and manual trigger routes.
"""
from datetime import date
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from pathlib import Path

from app.db import get_db
from app.models import EmailLog
from app.scheduler import trigger_check_now

router = APIRouter(tags=["logs"])
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.get("/logs", response_class=HTMLResponse)
async def list_logs(
    request: Request,
    page: int = 1,
    db: Session = Depends(get_db),
):
    """List email send logs."""
    per_page = 50
    offset = (page - 1) * per_page
    
    # Get total count
    total = db.execute(select(EmailLog)).scalars().all()
    total_count = len(total)
    
    # Get paginated logs
    logs = db.execute(
        select(EmailLog)
        .order_by(desc(EmailLog.created_at))
        .offset(offset)
        .limit(per_page)
    ).scalars().all()
    
    total_pages = (total_count + per_page - 1) // per_page
    
    return templates.TemplateResponse(
        "logs/list.html",
        {
            "request": request,
            "logs": logs,
            "page": page,
            "total_pages": total_pages,
            "total_count": total_count,
        }
    )


@router.post("/api/trigger-check")
async def trigger_check(request: Request):
    """Manually trigger birthday check (for testing)."""
    trigger_check_now()
    return RedirectResponse(url="/logs?triggered=1", status_code=303)


@router.get("/api/trigger-check", response_class=HTMLResponse)
async def trigger_check_page(request: Request):
    """Page to trigger manual check."""
    return templates.TemplateResponse(
        "logs/trigger.html",
        {"request": request}
    )

