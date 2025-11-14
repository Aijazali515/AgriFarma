"""Email service for AgriFarma.

Provides email sending functionality with support for both plain text and HTML.
Uses Flask-Mail for SMTP integration with fallback to logging for development.
"""
from __future__ import annotations
from typing import Iterable
from flask import current_app, render_template_string


def send_email(to: str | Iterable[str], subject: str, body: str, html: str = None) -> bool:
    """Send an email using Flask-Mail or fallback to logging.

    Args:
        to: Single recipient email or list of emails
        subject: Email subject line
        body: Plain text email body
        html: Optional HTML email body

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    if isinstance(to, str):
        recipients = [to]
    else:
        recipients = list(to)
    
    # Check if mail is suppressed (development mode)
    if current_app.config.get('MAIL_SUPPRESS_SEND', True):
        current_app.logger.info(
            "[EMAIL SUPPRESSED] to=%s subject=%s body=%s",
            ", ".join(recipients),
            subject,
            body[:200]
        )
        return True
    
    # Try to send with Flask-Mail
    try:
        from agrifarma.extensions import mail
        from flask_mail import Message
        
        if not mail:
            raise ImportError("Flask-Mail not available")
        
        msg = Message(
            subject=subject,
            recipients=recipients,
            body=body,
            html=html,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@agrifarma.local')
        )
        
        mail.send(msg)
        current_app.logger.info(
            "[EMAIL SENT] to=%s subject=%s",
            ", ".join(recipients),
            subject
        )
        return True
        
    except Exception as e:
        current_app.logger.error(
            "[EMAIL FAILED] to=%s subject=%s error=%s",
            ", ".join(recipients),
            subject,
            str(e)
        )
        return False


def send_password_reset_email(user_email: str, reset_url: str, user_name: str = None) -> bool:
    """Send password reset email with styled template.

    Args:
        user_email: Recipient email address
        reset_url: Full URL for password reset
        user_name: Optional user name for personalization

    Returns:
        bool: True if sent successfully
    """
    subject = "AgriFarma - Password Reset Request"
    
    # Plain text version
    body = f"""
Hello{' ' + user_name if user_name else ''},

You requested a password reset for your AgriFarma account.

Click the link below to reset your password:
{reset_url}

This link will expire in 24 hours.

If you did not request this reset, please ignore this email.

Best regards,
The AgriFarma Team
"""
    
    # HTML version
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #2d7a3e 0%, #1a4d26 100%); color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; border-top: none; }}
        .button {{ display: inline-block; padding: 12px 30px; background: #2d7a3e; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌾 AgriFarma</h1>
        </div>
        <div class="content">
            <h2>Password Reset Request</h2>
            <p>Hello{' ' + user_name if user_name else ''},</p>
            <p>You requested a password reset for your AgriFarma account.</p>
            <p>Click the button below to reset your password:</p>
            <center>
                <a href="{reset_url}" class="button">Reset Password</a>
            </center>
            <p><small>Or copy this link: {reset_url}</small></p>
            <p><strong>This link will expire in 24 hours.</strong></p>
            <p>If you did not request this reset, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>© 2025 AgriFarma - Farmers' Digital Hub</p>
        </div>
    </div>
</body>
</html>
"""
    
    return send_email(user_email, subject, body, html)


def send_order_confirmation_email(user_email: str, order_id: int, total_amount: float, user_name: str = None) -> bool:
    """Send order confirmation email.

    Args:
        user_email: Recipient email
        order_id: Order ID number
        total_amount: Total order amount
        user_name: Optional user name

    Returns:
        bool: True if sent successfully
    """
    subject = f"AgriFarma - Order Confirmation #{order_id}"
    
    body = f"""
Hello{' ' + user_name if user_name else ''},

Thank you for your order on AgriFarma!

Order #: {order_id}
Total Amount: Rs. {total_amount:.2f}

We will process your order and send you updates on shipping.

Thank you for supporting local agriculture!

Best regards,
The AgriFarma Team
"""
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #2d7a3e 0%, #1a4d26 100%); color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; border-top: none; }}
        .order-box {{ background: white; padding: 20px; border: 2px solid #2d7a3e; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌾 AgriFarma</h1>
        </div>
        <div class="content">
            <h2>Order Confirmation</h2>
            <p>Hello{' ' + user_name if user_name else ''},</p>
            <p>Thank you for your order! We've received your order and will process it shortly.</p>
            <div class="order-box">
                <h3>Order Details</h3>
                <p><strong>Order Number:</strong> #{order_id}</p>
                <p><strong>Total Amount:</strong> Rs. {total_amount:.2f}</p>
            </div>
            <p>We will send you updates on your order status and shipping information.</p>
            <p>Thank you for supporting local agriculture!</p>
        </div>
        <div class="footer">
            <p>© 2025 AgriFarma - Farmers' Digital Hub</p>
        </div>
    </div>
</body>
</html>
"""
    
    return send_email(user_email, subject, body, html)


def send_consultant_contact_email(consultant_email: str, sender_name: str, sender_email: str, message: str) -> bool:
    """Send message from user to consultant.

    Args:
        consultant_email: Consultant's email
        sender_name: Name of person sending message
        sender_email: Email of sender
        message: Message content

    Returns:
        bool: True if sent successfully
    """
    subject = f"AgriFarma - New Message from {sender_name}"
    
    body = f"""
You have received a new message on AgriFarma.

From: {sender_name} ({sender_email})

Message:
{message}

---
Reply directly to this email to respond to {sender_name}.
"""
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #2d7a3e 0%, #1a4d26 100%); color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; border-top: none; }}
        .message-box {{ background: white; padding: 20px; border-left: 4px solid #2d7a3e; margin: 20px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌾 AgriFarma</h1>
        </div>
        <div class="content">
            <h2>New Message</h2>
            <p>You have received a new message on AgriFarma.</p>
            <p><strong>From:</strong> {sender_name} ({sender_email})</p>
            <div class="message-box">
                <p>{message.replace(chr(10), '<br>')}</p>
            </div>
            <p><small>Reply directly to this email to respond to {sender_name}.</small></p>
        </div>
        <div class="footer">
            <p>© 2025 AgriFarma - Farmers' Digital Hub</p>
        </div>
    </div>
</body>
</html>
"""
    
    return send_email(consultant_email, subject, body, html)
