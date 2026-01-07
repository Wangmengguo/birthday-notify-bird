"""
Contact management routes.
"""
from datetime import date, datetime
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import select
from pathlib import Path

from app.db import get_db
from app.models import Contact

router = APIRouter(prefix="/contacts", tags=["contacts"])
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.get("/new", response_class=HTMLResponse)
async def new_contact_form(request: Request):
    """Show form to create new contact."""
    return templates.TemplateResponse(
        "contacts/form.html",
        {
            "request": request,
            "contact": None,
            "action": "new",
        }
    )


@router.post("/new")
async def create_contact(
    request: Request,
    name: str = Form(...),
    birthday: str = Form(...),
    note: str = Form(""),
    db: Session = Depends(get_db),
):
    """Create a new contact."""
    try:
        birthday_date = datetime.strptime(birthday, "%Y-%m-%d").date()
    except ValueError:
        return templates.TemplateResponse(
            "contacts/form.html",
            {
                "request": request,
                "contact": {"name": name, "birthday": birthday, "note": note},
                "action": "new",
                "error": "日期格式无效，请使用 YYYY-MM-DD 格式",
            },
            status_code=400,
        )
    
    contact = Contact(
        name=name.strip(),
        birthday=birthday_date,
        note=note.strip() if note else None,
    )
    db.add(contact)
    db.commit()
    
    return RedirectResponse(url="/contacts", status_code=303)


@router.get("", response_class=HTMLResponse)
async def list_contacts(request: Request, db: Session = Depends(get_db)):
    """List all contacts."""
    contacts = db.execute(
        select(Contact).order_by(Contact.birthday)
    ).scalars().all()
    
    # Calculate upcoming birthdays
    today = date.today()
    for contact in contacts:
        # Calculate days until next birthday
        next_birthday = date(today.year, contact.birthday.month, contact.birthday.day)
        if next_birthday < today:
            next_birthday = date(today.year + 1, contact.birthday.month, contact.birthday.day)
        contact.days_until = (next_birthday - today).days
    
    # Sort by days until birthday
    contacts = sorted(contacts, key=lambda c: c.days_until)
    
    return templates.TemplateResponse(
        "contacts/list.html",
        {
            "request": request,
            "contacts": contacts,
            "today": today,
        }
    )


@router.get("/{contact_id}/edit", response_class=HTMLResponse)
async def edit_contact_form(
    request: Request,
    contact_id: int,
    db: Session = Depends(get_db),
):
    """Show form to edit contact."""
    contact = db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="联系人不存在")
    
    return templates.TemplateResponse(
        "contacts/form.html",
        {
            "request": request,
            "contact": contact,
            "action": "edit",
        }
    )


@router.post("/{contact_id}/edit")
async def update_contact(
    request: Request,
    contact_id: int,
    name: str = Form(...),
    birthday: str = Form(...),
    note: str = Form(""),
    db: Session = Depends(get_db),
):
    """Update an existing contact."""
    contact = db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="联系人不存在")
    
    try:
        birthday_date = datetime.strptime(birthday, "%Y-%m-%d").date()
    except ValueError:
        return templates.TemplateResponse(
            "contacts/form.html",
            {
                "request": request,
                "contact": contact,
                "action": "edit",
                "error": "日期格式无效，请使用 YYYY-MM-DD 格式",
            },
            status_code=400,
        )
    
    contact.name = name.strip()
    contact.birthday = birthday_date
    contact.note = note.strip() if note else None
    db.commit()
    
    return RedirectResponse(url="/contacts", status_code=303)


@router.post("/{contact_id}/delete")
async def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
):
    """Delete a contact."""
    contact = db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="联系人不存在")
    
    db.delete(contact)
    db.commit()
    
    return RedirectResponse(url="/contacts", status_code=303)

