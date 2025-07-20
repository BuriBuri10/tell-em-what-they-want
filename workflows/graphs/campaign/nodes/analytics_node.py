from workflows.state import GraphState
from data_preprocessing_pipeline.user_data_analyzer import UserDataAnalyzer
from logs.logging_config import logger


class AnalyticsNode:
    """
    Node that analyzes external user logs using statistical or ML techniques.
    This supplements or replaces traditional segmentation based on internal persona.
    """

    def __init__(self):
        self.analyzer = UserDataAnalyzer()
        logger.info("AnalyticsNode initialized. Ready to process external user logs.")

    async def process(self, state: GraphState) -> GraphState:
        """
        Conditionally performs external user log analysis and adds inferred user segment.

        Args:
            state (GraphState): The current graph state containing optional external_user_logs.

        Returns:
            GraphState: Updated graph state with `user_segment` derived from external logs.
        """
        try:
            if not state.external_user_logs:
                logger.info("No external user logs provided. Skipping analytics node.")
                return state

            logger.info("Running ML analytics on external_user_logs...")
            segment = self.analyzer.analyze_user_logs(state.external_user_logs)

            if segment:
                state.user_segment = segment
                logger.info(f"AnalyticsNode completed. Inferred segment: '{segment}'")
            else:
                logger.warning("AnalyticsNode returned empty segment.")

        except Exception as e:
            logger.error(f"AnalyticsNode failed: {str(e)}")

        return state


# Optional manual test
if __name__ == "__main__":
    import asyncio
    from workflows.state import GraphState

    async def test():
        test_logs = [
            {"timestamp": "2025-07-18T10:45:00", "action": "click", "topic": "fitness"},
            {"timestamp": "2025-07-18T11:00:00", "action": "scroll", "topic": "tech"}
        ]

        test_state = GraphState(external_user_logs=test_logs)

        node = AnalyticsNode()
        updated_state = await node.process(test_state)
        print("Predicted Segment:\n", updated_state.user_segment)

    asyncio.run(test())


# from workflows.state import GraphState
# from logs.logging_config import logger
# from data_preprocessing_pipeline.user_data_analyzer import UserDataAnalyzer


# class AnalyticsNode:
#     """
#     Node that performs machine learning-based user segmentation
#     using external user interaction logs (e.g., clickstream, past campaigns).
#     """

#     def __init__(self):
#         logger.info("AnalyticsNode initialized. Ready to process external user logs.")

#     async def process(self, state: GraphState) -> GraphState:
#         """
#         Processes external user logs (if provided) to generate a user segment
#         via ML analysis like clustering.

#         Args:
#             state (GraphState): Current workflow state containing optional external_user_logs.

#         Returns:
#             GraphState: Updated state with user_segment based on analytics.
#         """
#         try:
#             if not state.external_user_logs:
#                 logger.info("No external_user_logs found. Skipping AnalyticsNode.")
#                 return state

#             logger.info("Running ML analytics on external_user_logs...")

#             # Analyze logs using ML (e.g., KMeans clustering)
#             analyzer = UserDataAnalyzer()
#             logs = state.external_user_logs
#             user_segment = analyzer.analyze_user_logs(logs)

#             # Update the state
#             state.user_segment = user_segment
#             logger.info(f"AnalyticsNode completed. Inferred segment: '{user_segment}'")

#         except Exception as e:
#             logger.error(f"AnalyticsNode failed: {str(e)}")
#             state.user_segment = "general_audience"  # Fallback

#         return state


# # Manual test runner
# if __name__ == "__main__":
#     import asyncio

#     async def test():
#         test_state = GraphState(
#             external_user_logs=[
#                 {"clicks": 15, "time_spent": 120, "interests": ["fitness", "tech"]},
#                 {"clicks": 5, "time_spent": 45, "interests": ["health", "gadgets"]},
#                 # ... simulated log entries
#             ]
#         )

#         analytics = AnalyticsNode()
#         updated_state = await analytics.process(test_state)

#         print(f"\nPredicted Segment:\n{updated_state.user_segment}")

#     asyncio.run(test())
