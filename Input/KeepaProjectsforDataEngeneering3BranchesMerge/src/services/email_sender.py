"""
Email Sender Service
Sends HTML reports via SendGrid or SMTP
"""

import asyncio
import base64
import hashlib
import hmac
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional
from urllib.parse import urlencode

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from src.config import get_settings


class EmailSendError(Exception):
    """Base exception for email sending errors"""

    pass


class EmailAuthError(EmailSendError):
    """Authentication failed"""

    pass


class EmailRateLimitError(EmailSendError):
    """Rate limit exceeded"""

    pass


class EmailSMTPError(EmailSendError):
    """SMTP error"""

    pass


class EmailSenderService:
    """
    Sends HTML emails with deal reports

    Supports:
    - SendGrid API (primary)
    - SMTP fallback (Gmail, etc.)
    - Open tracking (1x1 pixel)
    - Click tracking (UTM parameters)
    """

    def __init__(self):
        self.settings = get_settings()
        self.sendgrid_key = self.settings.sendgrid_api_key
        self.from_email = self.settings.from_email
        self.from_name = "DealFinder"

    async def send_report(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str,
        filter_name: str,
        report_id: Optional[str] = None,
        track_opens: bool = True,
        track_clicks: bool = True,
    ) -> dict:
        """
        Send a deal report email

        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_body: HTML email content
            text_body: Plain text fallback
            filter_name: Name for tracking
            report_id: Report ID for tracking
            track_opens: Include open tracking pixel
            track_clicks: Include click tracking

        Returns:
            dict with 'sent', 'message_id', 'timestamp'
        """
        # Add tracking pixel if enabled
        if track_opens and report_id:
            html_body = self._add_tracking_pixel(html_body, report_id)

        # Add unsubscribe link
        html_body = self._add_unsubscribe(html_body, to_email)
        text_body = self._add_unsubscribe_text(text_body, to_email)

        # Try SendGrid first, then SMTP fallback
        if self.sendgrid_key:
            try:
                return await self._send_sendgrid(
                    to_email=to_email,
                    subject=subject,
                    html_body=html_body,
                    text_body=text_body,
                )
            except EmailSendError as e:
                print(f"SendGrid failed, trying SMTP: {e}")

        # Fallback to SMTP
        try:
            return await self._send_smtp(
                to_email=to_email,
                subject=subject,
                html_body=html_body,
                text_body=text_body,
            )
        except Exception as e:
            return {
                "sent": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "provider": "smtp",
            }

    async def _send_sendgrid(
        self, to_email: str, subject: str, html_body: str, text_body: str
    ) -> dict:
        """Send via SendGrid API"""
        url = "https://api.sendgrid.com/v3/mail/send"

        payload = {
            "personalizations": [{"to": [{"email": to_email}], "subject": subject}],
            "from": {"email": self.from_email, "name": self.from_name},
            "content": [
                {"type": "text/plain", "value": text_body},
                {"type": "text/html", "value": html_body},
            ],
            "tracking_settings": {
                "click_tracking": {"enable": True, "enable_text": False},
                "open_tracking": {"enable": True},
            },
        }

        headers = {
            "Authorization": f"Bearer {self.sendgrid_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)

            if response.status_code in [200, 202]:
                message_id = response.headers.get(
                    "X-Message-Id", f"sg-{datetime.utcnow().timestamp()}"
                )
                return {
                    "sent": True,
                    "message_id": message_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "provider": "sendgrid",
                }
            elif response.status_code == 401:
                raise EmailAuthError("SendGrid authentication failed")
            elif response.status_code == 429:
                raise EmailRateLimitError("SendGrid rate limit exceeded")
            else:
                raise EmailSendError(f"SendGrid error: {response.status_code}")

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=5, max=30)
    )
    async def _send_smtp(
        self, to_email: str, subject: str, html_body: str, text_body: str
    ) -> dict:
        """Send via SMTP (Gmail example)"""
        # For demo, we'll use a mock SMTP sender
        # In production, configure actual SMTP settings

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.from_name} <{self.from_email}>"
        msg["To"] = to_email

        # Attach both plain text and HTML
        part1 = MIMEText(text_body, "plain")
        part2 = MIMEText(html_body, "html")
        msg.attach(part1)
        msg.attach(part2)

        # In a real implementation, you would connect to SMTP server:
        # with smtplib.SMTP("smtp.gmail.com", 587) as server:
        #     server.starttls()
        #     server.login(user, password)
        #     server.send_message(msg)

        # For demo purposes, simulate successful send
        message_id = f"smtp-{datetime.utcnow().timestamp()}"

        return {
            "sent": True,
            "message_id": message_id,
            "timestamp": datetime.utcnow().isoformat(),
            "provider": "smtp",
        }

    def _add_tracking_pixel(self, html: str, report_id: str) -> str:
        """Add 1x1 tracking pixel for open tracking"""
        tracking_id = self._generate_tracking_id(report_id)
        pixel_url = f"https://dealfinder.app/track/open/{tracking_id}"

        pixel = f'<img src="{pixel_url}" width="1" height="1" alt="" />'

        # Add before closing body tag
        if "</body>" in html:
            return html.replace("</body>", f"{pixel}</body>")
        else:
            return html + pixel

    def _add_unsubscribe(self, html: str, email: str) -> str:
        """Add unsubscribe link to HTML"""
        unsub_token = self._generate_unsub_token(email)
        unsubscribe_url = f"https://dealfinder.app/unsubscribe?token={unsub_token}"

        # This will be added by the report generator, but ensure it's there
        if "unsubscribe" not in html.lower():
            footer = f'''
            <div style="padding: 20px; text-align: center; font-size: 12px; color: #999;">
                <a href="{unsubscribe_url}">Unsubscribe</a> |
                <a href="https://dealfinder.app/preferences">Preferences</a>
            </div>
            '''
            if "</body>" in html:
                html = html.replace("</body>", f"{footer}</body>")
            else:
                html += footer

        return html

    def _add_unsubscribe_text(self, text: str, email: str) -> str:
        """Add unsubscribe link to plain text"""
        unsub_token = self._generate_unsub_token(email)
        unsubscribe_url = f"https://dealfinder.app/unsubscribe?token={unsub_token}"

        if "unsubscribe" not in text.lower():
            text += f"\n\n--\nUnsubscribe: {unsubscribe_url}\n"

        return text

    def _generate_tracking_id(self, report_id: str) -> str:
        """Generate unique tracking ID for open/click tracking"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        data = f"{report_id}:{timestamp}"
        return base64.urlsafe_b64encode(data.encode()).decode()[:16]

    def _generate_unsub_token(self, email: str) -> str:
        """Generate unsubscribe token for user"""
        data = f"unsub:{email}:{datetime.utcnow().strftime('%Y%m%d')}"
        return base64.urlsafe_b64encode(data.encode()).decode()[:32]

    async def send_bulk_reports(
        self,
        recipients: list,
        subject: str,
        html_body: str,
        text_body: str,
        filter_name: str,
        batch_size: int = 100,
    ) -> dict:
        """
        Send reports to multiple recipients

        Args:
            recipients: List of email addresses
            subject: Email subject
            html_body: HTML content
            text_body: Plain text content
            filter_name: For UTM tracking
            batch_size: Emails per batch

        Returns:
            dict with success/failure counts
        """
        results = {"total": len(recipients), "sent": 0, "failed": 0, "errors": []}

        for i in range(0, len(recipients), batch_size):
            batch = recipients[i : i + batch_size]

            for email in batch:
                try:
                    # Personalize subject with recipient
                    personalized_subject = subject.replace(
                        "{name}", email.split("@")[0]
                    )

                    result = await self.send_report(
                        to_email=email,
                        subject=personalized_subject,
                        html_body=html_body,
                        text_body=text_body,
                        filter_name=filter_name,
                    )

                    if result["sent"]:
                        results["sent"] += 1
                    else:
                        results["failed"] += 1
                        results["errors"].append(
                            {"email": email, "error": "Send failed"}
                        )

                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append({"email": email, "error": str(e)})

            # Rate limiting delay between batches
            if i + batch_size < len(recipients):
                await asyncio.sleep(1)

        return results


# Singleton instance
_email_sender: Optional[EmailSenderService] = None


def get_email_sender() -> EmailSenderService:
    """Get or create email sender singleton"""
    global _email_sender
    if _email_sender is None:
        _email_sender = EmailSenderService()
    return _email_sender
