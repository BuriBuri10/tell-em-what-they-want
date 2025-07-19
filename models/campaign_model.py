# from models.user_profile_model import UserProfile
# from typing import Dict

# # In-memory mock store for now
# USER_DB: Dict[str, UserProfile] = {}

# class UserService:
#     def create_or_update_user(self, user_input: UserProfile) -> UserProfile:
#         USER_DB[user_input.user_id] = user_input
#         return user_input

#     def get_user_by_id(self, user_id: str) -> UserProfile | None:
#         return USER_DB.get(user_id)
    

from pydantic import BaseModel, Field
from typing import List, Optional


class Campaign(BaseModel):
    """
    Represents a marketing campaign and its related targeting metadata.
    """
    id: str
    name: str
    objective: str
    audience_segment_ids: List[str]
    budget: float
    start_date: str
    end_date: Optional[str] = None

