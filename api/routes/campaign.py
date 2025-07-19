from fastapi import APIRouter, HTTPException
from models.campaign_model import CampaignRequest, CampaignResponse
from services.campaign_service import CampaignService

router = APIRouter()
campaign_service = CampaignService()

@router.post("/generate", response_model=CampaignResponse)
async def generate_campaign(request: CampaignRequest):
    """
    Generates a personalized marketing campaign based on the request.

    Args:
        request (CampaignRequest): Campaign input data including user_id, goal, product, etc.

    Returns:
        CampaignResponse: Structured campaign content.
    """
    try:
        campaign = campaign_service.generate_campaign(request)
        return campaign
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/history")
async def get_campaign_history(user_id: str):
    """
    Fetches campaign history for a given user.

    Args:
        user_id (str): Unique user ID.

    Returns:
        List[CampaignResponse]: Previous campaigns.
    """
    try:
        return campaign_service.get_campaign_history(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
