from workflows.state import GraphState
from logs.logging_config import logger


class CheckExternalLogsNode:
    """
    Determines if external user logs are present in the state.
    Based on this, the LangGraph will branch conditionally:
    - 'with_logs': both analytics and segmentation will run
    - 'without_logs': only segmentation will run
    """

    def __init__(self):
        logger.info("CheckExternalLogsNode initialized.")

    def process(self, state: GraphState) -> str:
        """
        Checks for presence of external_user_logs and returns routing tag.

        Args:
            state (GraphState): Current workflow state.

        Returns:
            str: 'with_logs' if external logs are present, else 'without_logs'.
        """
        if state.external_user_logs:
            logger.info("External logs found. Routing to analytics and segmentation.")
            # return "with_logs"
            return {"has_external_logs": True}

        else:
            logger.info("No external logs. Routing to segmentation only.")
            # return "without_logs"
            return {"has_external_logs": False}  # ✅ Valid

