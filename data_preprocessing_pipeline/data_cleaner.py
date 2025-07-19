# data_preprocessing_pipeline/data_cleaner.py

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class DataCleaner:
    """
    Utility class to perform cleaning and validation on raw user data.

    This includes removing duplicates, filtering invalid fields,
    normalizing text content, and sanitizing malformed records.
    """

    def __init__(self):
        pass

    def clean_user_logs(self, user_logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Cleans and filters a list of user log dictionaries.

        Args:
            user_logs (List[Dict]): Raw user logs from source.

        Returns:
            List[Dict]: Sanitized user logs.
        """
        if not user_logs:
            logger.warning("No user logs provided for cleaning.")
            return []

        cleaned_logs = []
        for entry in user_logs:
            if not self._is_valid_log(entry):
                logger.debug(f"Skipping invalid log entry: {entry}")
                continue

            cleaned_entry = {
                "user_id": entry["user_id"],
                "timestamp": entry["timestamp"],
                "action": self._normalize_text(entry["action"]),
                "topic": self._normalize_text(entry.get("topic", "")),
                "meta": entry.get("meta", {})
            }

            cleaned_logs.append(cleaned_entry)

        logger.info(f"Cleaned {len(cleaned_logs)} valid user logs.")
        return cleaned_logs

    def _is_valid_log(self, log: Dict[str, Any]) -> bool:
        """
        Checks whether a log entry contains the required fields.

        Args:
            log (Dict): A user log record.

        Returns:
            bool: True if valid, False otherwise.
        """
        required_fields = ["user_id", "timestamp", "action"]
        return all(field in log and isinstance(log[field], str) for field in required_fields)

    def _normalize_text(self, text: str) -> str:
        """
        Lowercases and removes non-alphanumeric characters from text.

        Args:
            text (str): Raw text input.

        Returns:
            str: Cleaned text string.
        """
        text = text.lower()
        return re.sub(r"[^a-z0-9\s\-_/]", "", text).strip()
