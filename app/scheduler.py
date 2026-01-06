"""
Birthday reminder scheduler using APScheduler.
"""
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select, and_
import pytz

from app import settings
from app.db import SessionLocal
from app.models import Contact, EmailLog
from app.emailer import send_birthday_reminder


# Global scheduler instance
scheduler: BackgroundScheduler | None = None


def check_and_send_reminders():
    """
    Check for upcoming birthdays and send reminder emails.
    This is the main job that runs daily.
    """
    # Use configured timezone to determine "today"
    try:
        tz = pytz.timezone(settings.TIMEZONE)
    except pytz.exceptions.UnknownTimeZoneError:
        tz = pytz.timezone("Asia/Shanghai")
    
    today = datetime.now(tz).date()
    print(f"🔍 Checking birthdays at {today} ({settings.TIMEZONE})...")
    
    db = SessionLocal()
    try:
        # Calculate target dates for each reminder type
        reminder_dates = {
            "today": today,
            "day": today + timedelta(days=1),
            "week": today + timedelta(days=7),
        }
        
        # Get all contacts
        contacts = db.execute(select(Contact)).scalars().all()
        
        sent_count = 0
        for reminder_type, target_date in reminder_dates.items():
            target_month = target_date.month
            target_day = target_date.day
            
            for contact in contacts:
                # Check if birthday matches (month and day)
                if contact.birthday.month == target_month and contact.birthday.day == target_day:
                    # Check if we already sent this reminder today (idempotency)
                    existing = db.execute(
                        select(EmailLog).where(
                            and_(
                                EmailLog.contact_id == contact.id,
                                EmailLog.reminder_type == reminder_type,
                                EmailLog.send_date == today,
                            )
                        )
                    ).scalar_one_or_none()
                    
                    if existing:
                        print(f"   ⏭️  Skip: {contact.name} ({reminder_type}) - already sent")
                        continue
                    
                    # Send the reminder
                    print(f"   📧 Sending: {contact.name} ({reminder_type})...")
                    success, subject, error = send_birthday_reminder(
                        contact, reminder_type, target_date
                    )
                    
                    # Log the result
                    log = EmailLog(
                        contact_id=contact.id,
                        reminder_type=reminder_type,
                        send_date=today,
                        email_to=settings.TO_EMAIL,
                        subject=subject,
                        status="sent" if success else "failed",
                        error=error if not success else None,
                    )
                    db.add(log)
                    db.commit()
                    
                    if success:
                        sent_count += 1
                        print(f"   ✅ Sent: {contact.name} ({reminder_type})")
                    else:
                        print(f"   ❌ Failed: {contact.name} ({reminder_type}) - {error}")
        
        print(f"✅ Check complete. Sent {sent_count} reminder(s).")
        
    except Exception as e:
        print(f"❌ Error during reminder check: {e}")
        db.rollback()
    finally:
        db.close()


def start_scheduler():
    """Start the background scheduler."""
    global scheduler
    
    if scheduler is not None:
        return
    
    # Parse run time
    try:
        hour, minute = map(int, settings.DAILY_RUN_AT.split(":"))
    except ValueError:
        hour, minute = 9, 0
        print(f"   ⚠️  Invalid DAILY_RUN_AT format, using default 09:00")
    
    # Get timezone
    try:
        tz = pytz.timezone(settings.TIMEZONE)
    except pytz.exceptions.UnknownTimeZoneError:
        tz = pytz.timezone("Asia/Shanghai")
        print(f"   ⚠️  Invalid TIMEZONE, using Asia/Shanghai")
    
    scheduler = BackgroundScheduler(timezone=tz)
    
    # Add daily job
    scheduler.add_job(
        check_and_send_reminders,
        CronTrigger(hour=hour, minute=minute, timezone=tz),
        id="daily_birthday_check",
        replace_existing=True,
    )
    
    scheduler.start()
    print(f"   ✅ Scheduler started: daily at {hour:02d}:{minute:02d} ({settings.TIMEZONE})")


def stop_scheduler():
    """Stop the background scheduler."""
    global scheduler
    
    if scheduler is not None:
        scheduler.shutdown(wait=False)
        scheduler = None
        print("   ✅ Scheduler stopped")


def trigger_check_now():
    """Manually trigger a birthday check (for testing)."""
    check_and_send_reminders()

