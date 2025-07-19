# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
# from models.user_profile_model import UserProfile
# from services.user_service import UserService

# router = APIRouter()
# user_service = UserService()

# # Request model for creating/updating a user
# class UserInput(BaseModel):
#     user_id: str
#     name: str
#     email: str
#     preferences: dict

# @router.post("/", response_model=UserProfile)
# def create_or_update_user(user_input: UserInput):
#     try:
#         user = user_service.create_or_update_user(user_input)
#         return user
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.get("/{user_id}", response_model=UserProfile)
# def get_user(user_id: str):
#     try:
#         user = user_service.get_user_by_id(user_id)
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")
#         return user
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


from fastapi import APIRouter, HTTPException
from models.user_profile_model import UserProfile
from services.user_service import UserService

router = APIRouter()
user_service = UserService()

@router.post("/create", response_model=UserProfile)
async def create_user_profile(user_data: UserProfile):
    """
    Creates or updates a user profile.

    Args:
        user_data (UserProfile): Incoming user profile data.

    Returns:
        UserProfile: Saved user profile.
    """
    try:
        result = user_service.save_user_profile(user_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}", response_model=UserProfile)
async def get_user_profile(user_id: str):
    """
    Retrieves a user profile by ID.

    Args:
        user_id (str): Unique user identifier.

    Returns:
        UserProfile: The requested user profile.
    """
    try:
        result = user_service.get_user_profile(user_id)
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

