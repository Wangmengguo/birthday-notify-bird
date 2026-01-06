"""
SQLAlchemy models for Birthday Notify Bird.
"""
from datetime import datetime, date
from sqlalchemy import String, Text, Date, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Contact(Base):
    """Contact with birthday information."""
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    birthday: Mapped[date] = mapped_column(Date, nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )

    # Relationship to email logs
    email_logs: Mapped[list["EmailLog"]] = relationship(
        back_populates="contact", cascade="all, delete-orphan"
    )

    @property
    def birthday_display(self) -> str:
        """Format birthday for display (MM-DD)."""
        return self.birthday.strftime("%m-%d")

    @property
    def birthday_month_day(self) -> tuple[int, int]:
        """Get (month, day) tuple for matching."""
        return (self.birthday.month, self.birthday.day)

    def __repr__(self) -> str:
        return f"<Contact(id={self.id}, name='{self.name}', birthday={self.birthday})>"


class EmailLog(Base):
    """Log of sent reminder emails (for idempotency)."""
    __tablename__ = "email_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contact_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("contacts.id"), nullable=False
    )
    reminder_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # 'week', 'day', 'today'
    send_date: Mapped[date] = mapped_column(Date, nullable=False)
    email_to: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="sent"
    )  # 'sent', 'failed'
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )

    # Relationship to contact
    contact: Mapped["Contact"] = relationship(back_populates="email_logs")

    @property
    def reminder_type_display(self) -> str:
        """Human-readable reminder type."""
        mapping = {
            "week": "提前7天",
            "day": "提前1天",
            "today": "当天",
        }
        return mapping.get(self.reminder_type, self.reminder_type)

    def __repr__(self) -> str:
        return f"<EmailLog(id={self.id}, contact_id={self.contact_id}, type='{self.reminder_type}')>"

