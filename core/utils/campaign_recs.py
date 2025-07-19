# core/prompts/report_saver.py

import os
from datetime import datetime
from workflows.state import GraphState
from logs.logging_config import logger

class CampaignReportSaver:
    @staticmethod
    def save(state: GraphState, user_id: str, query: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"campaign_outputs/{user_id}_{timestamp}.txt"
        os.makedirs("campaign_outputs", exist_ok=True)

        report = f"""📊 CAMPAIGN REPORT
                ─────────────────────────
                User ID: {user_id}
                Timestamp: {timestamp}
                Campaign Query: {query}

                User Segment: {state.user_segment or 'N/A'}
                Campaign Objective: {state.campaign_objective or 'N/A'}
                Recommendation: {state.campaign_recommendation or 'N/A'}
                Generated Ad Copy: {state.generated_ad or 'N/A'}
                Human Feedback: {state.ad_feedback or 'No feedback yet'}

                Recommendation:
                {state.campaign_recommendation or 'N/A'}

                Generated Ad Copy:
                {state.generated_ad or 'N/A'}

                Human Feedback:
                {state.ad_feedback or 'No feedback yet'}
                """
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)

        logger.info(f"Campaign report saved: {filename}")
