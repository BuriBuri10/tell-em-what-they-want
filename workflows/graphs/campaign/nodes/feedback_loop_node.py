from langchain_core.runnables import RunnableLambda
from core.chain import ChainAccess
from workflows.state import GraphState
from logs.logging_config import logger


class FeedbackLoopNode:
    """
    Node responsible for processing post-campaign feedback using LLM.
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
        Processes ad feedback and uses LLM to decide whether campaign iteration is required.

        Args:
            state (GraphState): Current graph state containing ad feedback.

        Returns:
            GraphState: Updated graph state with feedback processing status.
        """
        try:
            feedback = state.ad_feedback

            if not feedback:
                logger.warning("No feedback provided for the ad.")
                state.ad_feedback = "No feedback received."
                state.feedback_ready = False
                return state

            # Construct inline prompt
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

            # Optionally store this result
            state.feedback_analysis = result.content

            # # FIX: Ensure we extract the response correctly
            # if isinstance(result, str):
            #     state.feedback_analysis = result
            # elif hasattr(result, "content"):
            #     state.feedback_analysis = result.content
            # else:
            #     state.feedback_analysis = str(result)

            state.feedback_ready = True
            logger.info("Feedback processed and analyzed successfully.")

        except Exception as e:
            logger.error(f"Feedback processing failed: {str(e)}")
            state.feedback_analysis = "Unable to analyze feedback at this time."
            state.feedback_ready = False

        return state


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
