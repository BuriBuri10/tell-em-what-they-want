"""
Implements the recommendation logic for suggesting campaign strategies,
offers, or content themes based on user segment and behavior.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from pydantic import BaseModel

from logs.logging_config import logger


@dataclass
class Recommendation:
    """
    Represents a recommended campaign idea.
    """
    title: str
    description: str
    strategy_type: str
    confidence: float

class RecommendationOutputSchema(BaseModel):
    recommendations: List[Recommendation]

class RecommendationEngine:
    """
    Suggests relevant campaign strategies based on user segment
    and behavioral signals.
    """

    def __init__(self):
        logger.info("RecommendationEngine initialized.")

        # Simulated strategy knowledge base (could be replaced with vector search)
        self.strategy_database = {
            "bargain_hunters": [
                Recommendation(
                    title="Flash Discount Campaign",
                    description="Offer limited-time 30% off on popular items.",
                    strategy_type="discount",
                    confidence=0.92,
                ),
                Recommendation(
                    title="BOGO Offers",
                    description="Buy-one-get-one deals for frequently browsed categories.",
                    strategy_type="deal",
                    confidence=0.88,
                )
            ],
            "loyal_customers": [
                Recommendation(
                    title="Loyalty Rewards Push",
                    description="Showcase loyalty points redemption options.",
                    strategy_type="reward",
                    confidence=0.90,
                ),
                Recommendation(
                    title="Anniversary Thank You",
                    description="Send personalized messages and early access to new arrivals.",
                    strategy_type="personal_touch",
                    confidence=0.86,
                )
            ],
            "explorers": [
                Recommendation(
                    title="New Arrivals Showcase",
                    description="Highlight newest products tailored to user’s browsing history.",
                    strategy_type="curation",
                    confidence=0.87,
                ),
                Recommendation(
                    title="Trend Alert Campaign",
                    description="Notify about trending products in their interest area.",
                    strategy_type="trend",
                    confidence=0.83,
                )
            ]
        }

    def recommend(self, segment: str, behavior: Dict[str, Any]) -> List[Recommendation]:
        """
        Generates top recommended strategies for a given user segment.

        Args:
            segment (str): The user segment label (e.g., 'bargain_hunters').
            behavior (dict): Additional behavior analytics (clicks, cart events, etc.).

        Returns:
            List[Recommendation]: Ranked list of recommended strategies.
        """
        logger.debug(f"Generating recommendations for segment: {segment}")
        recommendations = self.strategy_database.get(segment, [])

        # Simple behavior-aware boost (optional)
        if behavior.get("high_cart_abandon_rate"):
            logger.debug("Boosting urgency-based campaigns due to cart abandonment.")
            recommendations.append(
                Recommendation(
                    title="Cart Recovery Promo",
                    description="Send 15% off coupon for items left in cart.",
                    strategy_type="recovery",
                    confidence=0.80,
                )
            )

        return sorted(recommendations, key=lambda r: r.confidence, reverse=True)
