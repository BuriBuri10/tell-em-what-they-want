from typing import Dict, List, Optional
from models.campaign_model import Campaign
from models.user_profile_model import UserProfile


class CampaignService:
    """
    Service layer responsible for managing marketing campaigns.

    Responsibilities:
    - Associate campaigns with specific users.
    - Retrieve all or latest campaigns for a given user.
    - Update campaign records with feedback or changes.
    """

    def __init__(self):
        """
        Initializes the in-memory campaign database.
        Structure: {user_id: [Campaign, Campaign, ...]}
        """
        self._campaign_db: Dict[str, List[Campaign]] = {}

    def save_campaign_for_user(self, user_id: str, campaign: Campaign) -> None:
        """
        Persists a new campaign associated with a specific user.

        Args:
            user_id (str): Unique identifier of the user.
            campaign (Campaign): The campaign object to store.
        """
        if user_id not in self._campaign_db:
            self._campaign_db[user_id] = []
        self._campaign_db[user_id].append(campaign)

    def get_campaigns_for_user(self, user_id: str) -> List[Campaign]:
        """
        Retrieves all campaigns created for a specific user.

        Args:
            user_id (str): Unique identifier of the user.

        Returns:
            List[Campaign]: A list of Campaign instances. Empty if none exist.
        """
        return self._campaign_db.get(user_id, [])

    def get_latest_campaign(self, user_id: str) -> Optional[Campaign]:
        """
        Retrieves the most recently created campaign for a user.

        Args:
            user_id (str): Unique identifier of the user.

        Returns:
            Optional[Campaign]: Latest Campaign instance, or None if unavailable.
        """
        campaigns = self._campaign_db.get(user_id, [])
        return campaigns[-1] if campaigns else None

    def update_campaign_with_feedback(
        self, user_id: str, campaign_id: str, feedback: str
    ) -> bool:
        """
        Updates an existing campaign with user feedback.

        Args:
            user_id (str): Unique identifier of the user.
            campaign_id (str): Unique ID of the campaign to update.
            feedback (str): Feedback string to append to the campaign.

        Returns:
            bool: True if update was successful, False otherwise.
        """
        campaigns = self._campaign_db.get(user_id, [])
        for campaign in campaigns:
            if campaign.id == campaign_id:
                campaign.feedback = feedback
                return True
        return False
