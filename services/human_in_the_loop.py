from typing import Optional
from models.ad_model import Ad

class HumanValidationService:
    """
    Handles manual review, approval, or rejection of AI-generated ads.

    This service acts as a gatekeeper before ads are finalized,
    allowing human validators to:
    - Approve or reject generated ads.
    - Add reviewer comments.
    - Trigger regeneration if required.
    """

    def __init__(self):
        """
        Initializes in-memory validation storage for demonstration/testing.
        Structure: {ad_id: {"status": "approved"/"rejected"/"pending", "comments": str}}
        """
        self._validation_db = {}

    def submit_for_review(self, ad: Ad) -> None:
        """
        Marks an ad as pending review by default.

        Args:
            ad (Ad): The ad object submitted for human validation.
        """
        self._validation_db[ad.id] = {"status": "pending", "comments": ""}

    def review_ad(
        self,
        ad_id: str,
        approved: bool,
        comments: Optional[str] = None
    ) -> bool:
        """
        Marks an ad as approved or rejected by a human reviewer.

        Args:
            ad_id (str): Unique identifier of the ad.
            approved (bool): Review decision; True = approve, False = reject.
            comments (Optional[str]): Optional feedback or suggestions.

        Returns:
            bool: True if review was recorded, False if ad not found.
        """
        if ad_id not in self._validation_db:
            return False

        self._validation_db[ad_id]["status"] = "approved" if approved else "rejected"
        self._validation_db[ad_id]["comments"] = comments or ""
        return True

    def get_review_status(self, ad_id: str) -> Optional[dict]:
        """
        Retrieves the review status and comments for a given ad.

        Args:
            ad_id (str): Unique identifier of the ad.

        Returns:
            Optional[dict]: Dict containing `status` and `comments`, or None if not found.
        """
        return self._validation_db.get(ad_id)
