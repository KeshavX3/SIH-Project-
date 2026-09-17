"""
HeatGuard AI — Notification Provider
======================================

Abstraction layer for alert delivery.
Supports mock (prototype) and extensible live providers.

PROTOTYPE BEHAVIOR:
  All notifications are simulated — logged and recorded in database.
  No actual SMS/WhatsApp/Email is sent.

To add a real provider:
  1. Implement NotificationProvider subclass
  2. Set NOTIFICATION_MODE=live in environment
  3. Add provider credentials to .env
"""
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class NotificationProvider(ABC):
    """Abstract notification provider interface."""

    @abstractmethod
    def send_sms(self, to: str, message: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def send_whatsapp(self, to: str, message: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def send_email(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        pass


class MockNotificationProvider(NotificationProvider):
    """
    Mock notification provider for SIH prototype demonstration.
    
    Simulates all notification types without requiring external credentials.
    All notifications are logged and recorded as 'simulated' in the database.
    """

    def send_sms(self, to: str, message: str) -> Dict[str, Any]:
        logger.info(f"[SIMULATED SMS] To: {to} | Message: {message[:80]}...")
        return {
            "provider": "MockNotificationProvider",
            "type": "SMS",
            "to": to,
            "message_preview": message[:100],
            "simulated": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "SIMULATED_SENT",
            "note": "Prototype mode — no actual SMS sent. Configure Twilio for live delivery.",
        }

    def send_whatsapp(self, to: str, message: str) -> Dict[str, Any]:
        logger.info(f"[SIMULATED WhatsApp] To: {to} | Message: {message[:80]}...")
        return {
            "provider": "MockNotificationProvider",
            "type": "WhatsApp",
            "to": to,
            "message_preview": message[:100],
            "simulated": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "SIMULATED_SENT",
            "note": "Prototype mode — configure WhatsApp Business API for live delivery.",
        }

    def send_email(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        logger.info(f"[SIMULATED Email] To: {to} | Subject: {subject}")
        return {
            "provider": "MockNotificationProvider",
            "type": "Email",
            "to": to,
            "subject": subject,
            "body_preview": body[:100],
            "simulated": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "SIMULATED_SENT",
            "note": "Prototype mode — configure SMTP/SendGrid for live delivery.",
        }


class LiveTwilioProvider(NotificationProvider):
    """
    Live Twilio SMS/WhatsApp provider.
    Requires TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables.
    Not instantiated in demo mode.
    """

    def __init__(self):
        import os
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.from_number = os.getenv("TWILIO_FROM_NUMBER", "")
        if not self.account_sid or not self.auth_token:
            raise ValueError("Twilio credentials not configured")

    def send_sms(self, to: str, message: str) -> Dict[str, Any]:
        try:
            from twilio.rest import Client
            client = Client(self.account_sid, self.auth_token)
            msg = client.messages.create(body=message, from_=self.from_number, to=to)
            return {"status": "SENT", "sid": msg.sid, "type": "SMS"}
        except Exception as e:
            logger.error(f"Twilio SMS failed: {e}")
            return {"status": "FAILED", "error": str(e)}

    def send_whatsapp(self, to: str, message: str) -> Dict[str, Any]:
        try:
            from twilio.rest import Client
            client = Client(self.account_sid, self.auth_token)
            msg = client.messages.create(
                body=message,
                from_=f"whatsapp:{self.from_number}",
                to=f"whatsapp:{to}"
            )
            return {"status": "SENT", "sid": msg.sid, "type": "WhatsApp"}
        except Exception as e:
            logger.error(f"Twilio WhatsApp failed: {e}")
            return {"status": "FAILED", "error": str(e)}

    def send_email(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        # Email through Twilio SendGrid — implement when needed
        return {"status": "NOT_IMPLEMENTED", "note": "Email requires SendGrid configuration"}


def get_notification_provider() -> NotificationProvider:
    """Factory function — returns appropriate provider based on config."""
    import os
    mode = os.getenv("NOTIFICATION_MODE", "mock")
    if mode == "live":
        try:
            return LiveTwilioProvider()
        except Exception as e:
            logger.warning(f"Live provider failed ({e}), falling back to mock")
    return MockNotificationProvider()
