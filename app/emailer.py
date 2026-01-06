"""
Email sending functionality using SMTP.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from datetime import date

from app import settings
from app.models import Contact


def create_reminder_email(
    contact: Contact,
    reminder_type: str,
    target_date: date,
) -> tuple[str, str]:
    """
    Create email subject and body for a birthday reminder.
    
    Args:
        contact: The contact whose birthday is coming up
        reminder_type: 'week', 'day', or 'today'
        target_date: The actual birthday date this year
    
    Returns:
        Tuple of (subject, html_body)
    """
    type_labels = {
        "week": "一周后",
        "day": "明天",
        "today": "今天",
    }
    
    type_emoji = {
        "week": "📅",
        "day": "⏰",
        "today": "🎂",
    }
    
    label = type_labels.get(reminder_type, reminder_type)
    emoji = type_emoji.get(reminder_type, "🔔")
    
    # Calculate age if birth year is reasonable
    age_text = ""
    if contact.birthday.year > 1900:
        age = target_date.year - contact.birthday.year
        age_text = f"（{age}岁）"
    
    subject = f"{emoji} {contact.name} 的生日{label}！"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 500px; margin: 0 auto; padding: 20px; background: #f5f5f5;">
        <div style="background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="text-align: center; font-size: 48px; margin-bottom: 20px;">{emoji}</div>
            
            <h1 style="text-align: center; color: #333; margin: 0 0 10px 0; font-size: 24px;">
                {contact.name} 的生日{label}！
            </h1>
            
            <p style="text-align: center; color: #666; margin: 0 0 30px 0;">
                {target_date.strftime('%Y年%m月%d日')} {age_text}
            </p>
            
            <div style="background: #f8f9fa; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="color: #888; padding: 5px 0;">姓名</td>
                        <td style="text-align: right; font-weight: 500;">{contact.name}</td>
                    </tr>
                    <tr>
                        <td style="color: #888; padding: 5px 0;">生日</td>
                        <td style="text-align: right;">{contact.birthday.strftime('%m月%d日')}</td>
                    </tr>
                    {"<tr><td style='color: #888; padding: 5px 0;'>备注</td><td style='text-align: right;'>" + contact.note + "</td></tr>" if contact.note else ""}
                </table>
            </div>
            
            <p style="text-align: center; color: #888; font-size: 14px; margin: 0;">
                记得送上你的祝福哦 💝
            </p>
        </div>
        
        <p style="text-align: center; color: #aaa; font-size: 12px; margin-top: 20px;">
            Birthday Notify Bird 🐦
        </p>
    </body>
    </html>
    """
    
    return subject, html_body


def send_email(to_email: str, subject: str, html_body: str) -> tuple[bool, str]:
    """
    Send an email via SMTP.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_body: HTML email body
    
    Returns:
        Tuple of (success, error_message)
    """
    # Validate settings
    valid, msg = settings.validate_email_settings()
    if not valid:
        return False, msg
    
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = formataddr(("Birthday Notify Bird", settings.FROM_EMAIL))
        msg["To"] = to_email
        
        # Add HTML body
        html_part = MIMEText(html_body, "html", "utf-8")
        msg.attach(html_part)
        
        # Connect and send
        if settings.SMTP_MODE == "ssl":
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            if settings.SMTP_MODE == "starttls":
                server.starttls()
        
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.sendmail(settings.FROM_EMAIL, [to_email], msg.as_string())
        server.quit()
        
        return True, ""
    
    except smtplib.SMTPAuthenticationError as e:
        return False, f"SMTP 认证失败: {str(e)}"
    except smtplib.SMTPException as e:
        return False, f"SMTP 错误: {str(e)}"
    except Exception as e:
        return False, f"发送失败: {str(e)}"


def send_birthday_reminder(
    contact: Contact,
    reminder_type: str,
    target_date: date,
) -> tuple[bool, str, str]:
    """
    Send a birthday reminder email.
    
    Args:
        contact: The contact
        reminder_type: 'week', 'day', or 'today'
        target_date: The birthday date this year
    
    Returns:
        Tuple of (success, subject, error_message)
    """
    subject, html_body = create_reminder_email(contact, reminder_type, target_date)
    success, error = send_email(settings.TO_EMAIL, subject, html_body)
    return success, subject, error

