from langchain_core.runnables import RunnableLambda
from core.chain import ChainAccess
from workflows.state import GraphState
from logs.logging_config import logger


class FeedbackLoopNode:
    """
    Node responsible for processing reviewed ad variants and analyzing feedback using LLM.
    """

    def __init__(self):
        """
        Initializes the feedback loop node with an inline prompt chain.
        """
        self.chain: RunnableLambda = ChainAccess.get_orchestrator().build(
            prompt_map={"default": RunnableLambda(lambda x: x["input"])},
            structured_output=None
        )["default"]

        logger.info("FeedbackLoopNode initialized with inline prompt chain.")

    async def process(self, state: GraphState) -> GraphState:
        """
        Processes ad feedback and selects the best ad variant. Also analyzes user feedback
        to decide if further changes are necessary.

        Args:
            state (GraphState): Current graph state containing ad feedback.

        Returns:
            GraphState: Updated graph state with final ad and feedback analysis.
        """
        try:
            # Step 1: Handle reviewed ads and select best one
            reviewed_ads = state.reviewed_ads or [{"ad": state.generated_ad, "score": 1.0}]
            best_ad = max(reviewed_ads, key=lambda x: x["score"])
            state.final_ad = best_ad["ad"]
            logger.info(f"Selected final ad after feedback loop: {state.final_ad}")

            # Step 2: Analyze textual feedback
            feedback = state.ad_feedback

            if not feedback:
                logger.warning("No feedback provided for the ad.")
                state.ad_feedback = "No feedback received."
                state.feedback_analysis = "No feedback provided to analyze."
                state.feedback_ready = False
                return state

            prompt_text = f"""
            Analyze the following user feedback on a digital ad campaign and determine:
            - If the tone, message, or content type needs adjustment
            - Whether a follow-up action is recommended
            - What part of the ad was effective or ineffective

            Feedback:
            {feedback}

            Respond with clear next steps or note if no changes are needed.
            """.strip()

            result = await self.chain.ainvoke({"input": prompt_text})

            # ✅ Save feedback interpretation
            state.feedback_analysis = result.content if hasattr(result, "content") else str(result)
            state.feedback_ready = True
            logger.info("Feedback processed and analyzed successfully.")

        except Exception as e:
            logger.error(f"FeedbackLoopNode failed: {str(e)}")
            state.feedback_analysis = "Unable to analyze feedback at this time."
            state.feedback_ready = False

        return state

# from workflows.state import GraphState
# from logs.logging_config import logger
# from langchain_core.runnables import RunnableLambda
# from core.chain import ChainAccess


# class FeedbackLoopNode:
#     """
#     Selects the top-performing ad from reviewed variants.
#     """
#     def __init__(self):
#         """
#         Initializes the feedback loop node with an inline prompt chain.
#         """
#         self.chain: RunnableLambda = ChainAccess.get_orchestrator().build(
#             prompt_map={"default": RunnableLambda(lambda x: x["input"])},
#             structured_output=None
#         )["default"]

#         logger.info("FeedbackLoopNode initialized with inline prompt chain.")


#     async def process(self, state: GraphState) -> GraphState:
#         """
#         Processes ad feedback and uses LLM to decide whether campaign iteration is required.

#         Args:
#             state (GraphState): Current graph state containing ad feedback.

#         Returns:
#             GraphState: Updated graph state with feedback processing status.
#         """
#         try:
#             # <<< CHANGED >>> ensure reviewed_ads is present
#             reviewed_ads = state.reviewed_ads or [{"ad": state.generated_ad, "score": 1.0}]  # <<< CHANGED >>>

#             # <<< CHANGED >>> pick ad with the highest score
#             best_ad = max(reviewed_ads, key=lambda x: x["score"])  # <<< CHANGED >>>

#             state.final_ad = best_ad["ad"]  # <<< CHANGED >>>
#             logger.info(f"Selected final ad after feedback loop: {state.final_ad}")

#         except Exception as e:
#             logger.error(f"FeedbackLoopNode failed: {str(e)}")

#         return state
    












# from langchain_core.runnables import RunnableLambda
# from core.chain import ChainAccess
# from workflows.state import GraphState
# from logs.logging_config import logger


# class FeedbackLoopNode:
#     """
#     Node responsible for processing post-campaign feedback using LLM.
#     """

#     def __init__(self):
#         """
#         Initializes the feedback loop node with an inline prompt chain.
#         """
#         self.chain: RunnableLambda = ChainAccess.get_orchestrator().build(
#             prompt_map={"default": RunnableLambda(lambda x: x["input"])},
#             structured_output=None
#         )["default"]

#         logger.info("FeedbackLoopNode initialized with inline prompt chain.")

#     async def process(self, state: GraphState) -> GraphState:
#         """
#         Processes ad feedback and uses LLM to decide whether campaign iteration is required.

#         Args:
#             state (GraphState): Current graph state containing ad feedback.

#         Returns:
#             GraphState: Updated graph state with feedback processing status.
#         """
#         try:
#             feedback = state.ad_feedback

#             if not feedback:
#                 logger.warning("No feedback provided for the ad.")
#                 state.ad_feedback = "No feedback received."
#                 state.feedback_ready = False
#                 return state

#             # Construct inline prompt
#             prompt_text = f"""
#             Analyze the following user feedback on a digital ad campaign and determine:
#             - If the tone, message, or content type needs adjustment
#             - Whether a follow-up action is recommended
#             - What part of the ad was effective or ineffective

#             Feedback:
#             {feedback}

#             Respond with clear next steps or note if no changes are needed.
#             """.strip()

#             result = await self.chain.ainvoke({"input": prompt_text})

#             # Optionally store this result
#             state.feedback_analysis = result.content

#             # # FIX: Ensure we extract the response correctly
#             # if isinstance(result, str):
#             #     state.feedback_analysis = result
#             # elif hasattr(result, "content"):
#             #     state.feedback_analysis = result.content
#             # else:
#             #     state.feedback_analysis = str(result)

#             state.feedback_ready = True
#             logger.info("Feedback processed and analyzed successfully.")

#         except Exception as e:
#             logger.error(f"Feedback processing failed: {str(e)}")
#             state.feedback_analysis = "Unable to analyze feedback at this time."
#             state.feedback_ready = False

#         return state


# Manual test runner
if __name__ == "__main__":
    import asyncio

    async def test():
        test_state = GraphState(
            ad_feedback="The visuals are great, but the message lacks emotional connection.",
            query="",
            conversation_history=[]
        )

        node = FeedbackLoopNode()
        updated_state = await node.process(test_state)

        print(f"\nFeedback Analysis:\n{updated_state.feedback_analysis}")
        print(f"Ready: {updated_state.feedback_ready}")

    asyncio.run(test())
