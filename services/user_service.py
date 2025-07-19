from typing import Dict, Optional
from models.user_profile_model import UserProfile


class UserService:
    """
    Service to manage user profiles, history, and personalization settings.

    Provides functionality to:
    - Create or update user profiles
    - Fetch user data for targeting
    - Store basic interaction history
    """

    def __init__(self):
        """
        Initializes in-memory user storage.
        Structure: {user_id: UserProfile}
        """
        self._user_db: Dict[str, UserProfile] = {}

    def create_or_update_user(self, profile: UserProfile) -> None:
        """
        Creates a new user or updates an existing user profile.

        Args:
            profile (UserProfile): User profile object containing preferences and metadata.
        """
        self._user_db[profile.user_id] = profile

    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Fetches a user profile by user ID.

        Args:
            user_id (str): Unique identifier of the user.

        Returns:
            Optional[UserProfile]: User profile object if found, else None.
        """
        return self._user_db.get(user_id)

    def delete_user(self, user_id: str) -> bool:
        """
        Deletes a user profile from the system.

        Args:
            user_id (str): Unique identifier of the user.

        Returns:
            bool: True if deletion was successful, False if user not found.
        """
        if user_id in self._user_db:
            del self._user_db[user_id]
            return True
        return False
