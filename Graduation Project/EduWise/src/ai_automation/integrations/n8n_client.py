"""Send authenticated events to an n8n webhook."""

import os
from typing import Any
from urllib.parse import urlsplit

import requests


class N8nDispatchError(RuntimeError):
    """The workflow did not confirm receipt of the event."""


class N8nClient:
    def __init__(
        self,
        alert_webhook_url: str | None = None,
        homework_webhook_url: str | None = None,
        timeout: float = 8.0,
        token: str | None = None,
    ) -> None:
        self.alert_webhook_url = alert_webhook_url or os.getenv("N8N_WEBHOOK_URL")
        self.homework_webhook_url = homework_webhook_url or os.getenv("N8N_HOMEWORK_WEBHOOK_URL")
        self.timeout = timeout
        self.token = token or os.getenv("N8N_WEBHOOK_TOKEN")

    def _post(self, url: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        if not url or not self.token:
            raise N8nDispatchError("n8n webhook URL or token is not configured")
        destination = urlsplit(url)
        if (
            not destination.hostname or destination.username or destination.password
            or (destination.scheme != "https" and not (
                destination.scheme == "http"
                and destination.hostname in {"localhost", "127.0.0.1", "::1"}
            ))
        ):
            raise N8nDispatchError("n8n webhook URL must use HTTPS or loopback HTTP")
        try:
            response = requests.post(
                url,
                json=payload,
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=self.timeout,
                allow_redirects=False,
            )
            if not 200 <= response.status_code < 300:
                raise N8nDispatchError(f"n8n webhook returned HTTP {response.status_code}")
            acknowledgement = response.json()
        except (requests.RequestException, ValueError):
            raise N8nDispatchError("n8n webhook could not be reached or returned invalid JSON") from None
        if not isinstance(acknowledgement, dict):
            raise N8nDispatchError("n8n webhook returned an invalid acknowledgement")
        return acknowledgement

    def send_alert(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not payload.get("event_id"):
            raise ValueError("Alert event_id is required")
        result = self._post(self.alert_webhook_url, {"event_id": payload["event_id"]})
        if result.get("status") != "accepted" or result.get("event_id") != payload["event_id"]:
            raise N8nDispatchError("n8n webhook did not acknowledge the submitted alert event")
        return result

    def trigger_homework_grade(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Dispatch to a separately configured, custom homework webhook."""
        if missing := {"student_id", "assignment_code"}.difference(payload):
            raise ValueError(f"Missing homework payload keys: {', '.join(sorted(missing))}")
        return self._post(self.homework_webhook_url, payload)
