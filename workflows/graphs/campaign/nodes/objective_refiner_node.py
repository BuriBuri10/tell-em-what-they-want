from langchain_core.runnables import RunnableLambda
from core.chain import ChainAccess
from workflows.state import GraphState
from logs.logging_config import logger


class ObjectiveRefinerNode:
    """
    Refines a vague or misaligned campaign objective based on the persona.
    Triggered when the initial campaign objective validation fails.
    """

    def __init__(self):
        """
        Initializes the ObjectiveRefinerNode with a fallback chain.
        """
        self.chain: RunnableLambda = ChainAccess.get_orchestrator().build(
            prompt_map={"default": RunnableLambda(lambda x: x["input"])},
            structured_output=None,
        )["default"]

        logger.info("ObjectiveRefinerNode initialized.")

    async def process(self, state: GraphState) -> GraphState:
        """
        Refines the campaign objective using persona context.

        Args:
            state (GraphState): The current workflow state.

        Returns:
            GraphState: Updated with a refined objective.
        """
        try:
            prompt = f"""
            The following campaign objective may be unclear or misaligned:

            Original Objective: "{state.campaign_objective}"

            Given this user persona:
            {state.user_persona}

            Please rewrite the objective to be specific, actionable, and aligned with the persona's traits.
            Only return the improved objective, without additional explanation.
            """.strip()

            result = await self.chain.ainvoke({"input": prompt})
            refined_objective = result.content.strip()

            state.campaign_objective = refined_objective

            logger.info(f"Refined Objective: {refined_objective}")

        except Exception as e:
            logger.error(f"ObjectiveRefinerNode failed: {str(e)}")

        return state


# Manual test runner
if __name__ == "__main__":
    import asyncio

    async def test():
        test_state = GraphState(
            user_persona="25-year-old female tech enthusiast, shops online frequently, follows fashion influencers on Instagram.",
            campaign_objective="Promote product",
        )

        node = ObjectiveRefinerNode()
        updated_state = await node.process(test_state)

        print(f"\nRefined Objective: {updated_state.campaign_objective}")

    asyncio.run(test())
