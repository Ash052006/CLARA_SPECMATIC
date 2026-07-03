import logging
import os

os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

from transformers import pipeline


logger = logging.getLogger(__name__)


class LLMManager:

    def __init__(self):

        self.classifier = None
        self._load_classifier()

    def _load_classifier(self):
        try:
            self.classifier = pipeline(
                "zero-shot-classification",
                model="valhalla/distilbart-mnli-12-3",
                local_files_only=True,
            )
        except Exception as exc:
            logger.warning(
                "Unable to load zero-shot classifier locally; using rule-based fallback. %s",
                exc,
            )
            self.classifier = None

    def understand(self, message):

        text = message.lower()

        # -------------------------
        # Holiday Intent
        # -------------------------

        if "holiday" in text:

            return {
                "user_message": message,
                "intent": "holiday",
                "confidence": 1.0
            }

        # -------------------------
        # Calendar Query Intent
        # -------------------------

        if (
            "what events" in text
            or "what meetings" in text
            or "my schedule" in text
            or "calendar" in text
        ):

            return {
                "user_message": message,
                "intent": "calendar_query",
                "confidence": 1.0
            }

        # -------------------------
        # Email Reply Intent
        # -------------------------

        if (
            "reply to" in text
            or "reply email" in text
        ):

            return {
                "user_message": message,
                "intent": "email_reply",
                "confidence": 1.0
            }

        # -------------------------
        # Email Query Intent
        # -------------------------

        if (
            "latest emails" in text
            or "read emails" in text
            or "my emails" in text
            or "inbox" in text
            or "latest email" in text
        ):

            return {
                "user_message": message,
                "intent": "email_query",
                "confidence": 1.0
            }

        # -------------------------
        # Calendar Delete Intent
        # -------------------------

        if (
            "cancel" in text
            or "delete" in text
            or "remove" in text
        ):

            return {
                "user_message": message,
                "intent": "calendar_delete",
                "confidence": 1.0
            }

        # -------------------------
        # Calendar Update Intent
        # -------------------------

        if any(
            word in text
            for word in [
                "update",
                "move",
                "reschedule",
                "change"
            ]
        ):

            return {
                "user_message": message,
                "intent": "calendar_update",
                "confidence": 1.0
            }

        # -------------------------
        # Email Search Intent
        # -------------------------

        if (
            "find email" in text
            or "search email" in text
            or "emails from" in text
        ):

            return {
                "user_message": message,
                "intent": "email_search",
                "confidence": 1.0
            }

        # -------------------------
        # Zero-Shot Classification
        # -------------------------

        result = self.classifier(
            message,
            [
                "meeting",
                "holiday",
                "calendar_query",
                "calendar_delete",
                "calendar_update",
                "email",
                "email_query",
                "email_search",
                "email_reply",
                "reminder",
                "search",
                "note"
            ]
        )

        return {

            "user_message": message,

            "intent":
            result["labels"][0],

            "confidence":
            round(
                result["scores"][0],
                2
            )
        }