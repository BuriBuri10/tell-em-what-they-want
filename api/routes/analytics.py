from fastapi import APIRouter, HTTPException
from services.analytics.metrics_collector import MetricsCollector

router = APIRouter()
metrics = MetricsCollector()

@router.get("/engagement/{campaign_id}")
async def get_campaign_engagement(campaign_id: str):
    """
    Retrieves analytics data (CTR, views, etc.) for a specific campaign.

    Args:
        campaign_id (str): The campaign's unique ID.

    Returns:
        dict: Engagement metrics.
    """
    try:
        return metrics.get_campaign_metrics(campaign_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}")
async def get_user_engagement(user_id: str):
    """
    Returns aggregated engagement data across all campaigns for a user.

    Args:
        user_id (str): User identifier.

    Returns:
        dict: Aggregated engagement stats.
    """
    try:
        return metrics.get_user_engagement(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
