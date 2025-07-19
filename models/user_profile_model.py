# from pydantic import BaseModel, Field
# from typing import Optional, Dict

# class UserProfile(BaseModel):
#     user_id: str = Field(..., description="Unique identifier for the user")
#     name: str = Field(..., description="User's full name")
#     email: str = Field(..., description="User's email address")
#     preferences: Optional[Dict] = Field(default_factory=dict, description="User preferences or metadata")

#     class Config:
#         orm_mode = True

from pydantic import BaseModel, Field
from typing import List, Optional


class UserProfile(BaseModel):
    """
    Represents user metadata used for segmentation.
    """
    user_id: str
    age: Optional[int]
    gender: Optional[str]
    interests: List[str]
    purchase_history: List[str]
    location: Optional[str] = None

