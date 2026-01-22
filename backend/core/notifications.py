"""
Notification System for Alerts.

Sends alerts via webhooks with retry logic.
"""

import asyncio
from typing import Optional

import httpx

from backend.config import settings
from backend.core.alerts import Alert


class WebhookNotifier:
    """
    Send alerts to external webhooks.

    Features:
    - Async HTTP POST requests
    - Retry logic with exponential backoff
    - Timeout handling
    - Error logging
    """

    def __init__(
        self,
        webhook_url: Optional[str] = None,
        timeout: int = 10,
        max_retries: int = 3,
    ):
        """
        Initialize webhook notifier.

        Args:
            webhook_url: Target webhook URL (default from config)
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        self.webhook_url = webhook_url or settings.ALERT_WEBHOOK_URL
        self.timeout = timeout
        self.max_retries = max_retries

        if self.webhook_url:
            print(f"✓ Webhook notifier enabled: {self.webhook_url}")

    async def send_alert(self, alert: Alert) -> bool:
        """
        Send alert to webhook.

        Args:
            alert: Alert object to send

        Returns:
            True if sent successfully
        """
        if not self.webhook_url:
            return False

        payload = {
            "alert_id": alert.id,
            "alert_type": alert.alert_type,
            "severity": alert.severity.value,
            "message": alert.message,
            "timestamp": alert.timestamp.isoformat(),
            "track_ids": alert.track_ids,
            "frame_id": alert.frame_id,
            "metadata": alert.metadata,
        }

        async with httpx.AsyncClient() as client:
            for attempt in range(self.max_retries):
                try:
                    response = await client.post(
                        self.webhook_url,
                        json=payload,
                        timeout=self.timeout,
                    )
                    response.raise_for_status()
                    print(f"✓ Alert {alert.id} sent to webhook successfully")
                    return True

                except httpx.HTTPStatusError as e:
                    print(f"⚠️  Webhook HTTP error (attempt {attempt + 1}/{self.max_retries}): {e}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff

                except httpx.RequestError as e:
                    print(f"⚠️  Webhook request error (attempt {attempt + 1}/{self.max_retries}): {e}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(2 ** attempt)

                except Exception as e:
                    print(f"⚠️  Unexpected webhook error: {e}")
                    break

        print(f"❌ Failed to send alert {alert.id} after {self.max_retries} attempts")
        return False

    def send_alert_sync(self, alert: Alert) -> bool:
        """
        Synchronous wrapper for send_alert.

        Args:
            alert: Alert to send

        Returns:
            True if sent successfully
        """
        if not self.webhook_url:
            return False

        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.send_alert(alert))
        except RuntimeError:
            # If no event loop, create one
            return asyncio.run(self.send_alert(alert))


class EmailNotifier:
    """
    Email notification system (placeholder for future implementation).
    """

    def __init__(self, smtp_server: str = None, smtp_port: int = 587):
        """Initialize email notifier."""
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        raise NotImplementedError(
            "Email notifications not yet implemented. Use webhooks for now."
        )

    def send_alert(self, alert: Alert):
        """Send alert via email."""
        raise NotImplementedError()


def create_webhook_callback(webhook_url: str = None):
    """
    Create a callback function for alert webhook notifications.

    Args:
        webhook_url: Optional webhook URL override

    Returns:
        Callback function
    """
    notifier = WebhookNotifier(webhook_url=webhook_url)

    def callback(alert: Alert):
        """Webhook callback."""
        if notifier.webhook_url:
            notifier.send_alert_sync(alert)

    return callback
