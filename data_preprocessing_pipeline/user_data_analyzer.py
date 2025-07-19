# data_preprocessing_pipeline/user_data_analyzer.py

from typing import List, Dict, Any
import logging
from collections import Counter

from logs.logging_config import logger


class UserDataAnalyzer:
    """
    Analyzes raw user data to extract high-level behavioral features.

    This includes activity frequency, interests, engagement patterns,
    and content preferences, which can inform downstream segmentation
    and recommendation models.
    """

    def __init__(self):
        pass

    def analyze_user_logs(self, user_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Performs basic statistical and behavioral analysis on user logs.

        Args:
            user_logs (List[Dict]): A list of user interaction events.

        Returns:
            Dict: A dictionary of summarized user features.
        """
        if not user_logs:
            logger.warning("No user logs provided for analysis.")
            return {}

        timestamps = [log["timestamp"] for log in user_logs if "timestamp" in log]
        actions = [log["action"] for log in user_logs if "action" in log]
        topics = [log.get("topic") for log in user_logs if "topic" in log]

        analysis = {
            "total_events": len(user_logs),
            "active_hours": self._analyze_active_hours(timestamps),
            "top_actions": self._get_top_items(actions, top_n=3),
            "top_topics": self._get_top_items(topics, top_n=3),
        }

        logger.info("User data analysis complete.")
        return analysis

    def _analyze_active_hours(self, timestamps: List[str]) -> List[int]:
        """
        Extracts hours of user activity from timestamp strings.

        Args:
            timestamps (List[str]): List of ISO 8601 timestamp strings.

        Returns:
            List[int]: Sorted list of most active hours in the day.
        """
        from datetime import datetime

        hour_counter = Counter()
        for ts in timestamps:
            try:
                dt = datetime.fromisoformat(ts)
                hour_counter[dt.hour] += 1
            except Exception as e:
                logger.debug(f"Invalid timestamp skipped: {ts} - {e}")

        most_active_hours = [hour for hour, _ in hour_counter.most_common(3)]
        return sorted(most_active_hours)

    def _get_top_items(self, items: List[str], top_n: int = 3) -> List[str]:
        """
        Returns the most frequently occurring items in a list.

        Args:
            items (List[str]): Items to count frequency of.
            top_n (int): Number of top items to return.

        Returns:
            List[str]: Top `n` most common items.
        """
        counter = Counter(item for item in items if item)
        return [item for item, _ in counter.most_common(top_n)]
