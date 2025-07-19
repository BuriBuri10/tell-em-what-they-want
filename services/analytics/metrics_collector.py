# services/analytics/metrics_collector.py

from datetime import datetime
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Collects and logs key metrics related to campaign performance.

    This can be extended to support storage in external systems
    such as databases, Prometheus, or analytics dashboards.
    """

    def __init__(self):
        self.metrics_store: Dict[str, Dict[str, float]] = {}

    def log_click_through_rate(self, campaign_id: str, impressions: int, clicks: int):
        """
        Logs and stores click-through rate (CTR) for a campaign.

        Args:
            campaign_id (str): Unique identifier for the campaign.
            impressions (int): Number of times the ad was shown.
            clicks (int): Number of clicks on the ad.
        """
        if impressions == 0:
            logger.warning(f"No impressions recorded for campaign {campaign_id}")
            return

        ctr = (clicks / impressions) * 100
        self._store_metric(campaign_id, "ctr", ctr)
        logger.info(f"[{campaign_id}] CTR logged: {ctr:.2f}%")

    def log_conversion_rate(self, campaign_id: str, visitors: int, conversions: int):
        """
        Logs and stores conversion rate for a campaign.

        Args:
            campaign_id (str): Unique identifier for the campaign.
            visitors (int): Number of visitors after clicking.
            conversions (int): Number of conversions (e.g., purchases, sign-ups).
        """
        if visitors == 0:
            logger.warning(f"No visitors recorded for campaign {campaign_id}")
            return

        conversion_rate = (conversions / visitors) * 100
        self._store_metric(campaign_id, "conversion_rate", conversion_rate)
        logger.info(f"[{campaign_id}] Conversion rate logged: {conversion_rate:.2f}%")

    def _store_metric(self, campaign_id: str, metric_name: str, value: float):
        """
        Internal method to store a metric in memory.

        Args:
            campaign_id (str): The campaign identifier.
            metric_name (str): The name of the metric (e.g., 'ctr').
            value (float): The value of the metric.
        """
        if campaign_id not in self.metrics_store:
            self.metrics_store[campaign_id] = {}

        self.metrics_store[campaign_id][metric_name] = value
        logger.debug(f"[{campaign_id}] Stored metric '{metric_name}': {value:.2f}")

    def get_metric(self, campaign_id: str, metric_name: str) -> Optional[float]:
        """
        Retrieves a stored metric for a given campaign.

        Args:
            campaign_id (str): The campaign identifier.
            metric_name (str): The name of the metric to retrieve.

        Returns:
            Optional[float]: The metric value or None if not found.
        """
        return self.metrics_store.get(campaign_id, {}).get(metric_name)
