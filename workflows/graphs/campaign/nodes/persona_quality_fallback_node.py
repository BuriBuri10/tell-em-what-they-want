from langchain_core.runnables import RunnableLambda
from core.chain import ChainAccess
from workflows.state import GraphState
from logs.logging_config import logger


class PersonaQualityCheckNode:
    """
    Fallback node to re-validate or double-check if the persona is usable
    before proceeding to recommendation. This provides a safety net in the
    flow after segmentation or enrichment.
    """

    def __init__(self):
        """
        Initializes the fallback persona quality checker.
        """
        self.chain: RunnableLambda = ChainAccess.get_orchestrator().build(
            prompt_map={"default": RunnableLambda(lambda x: x["input"])},
            structured_output=None,
        )["default"]

        logger.info("PersonaQualityCheckNode initialized.")

    async def process(self, state: GraphState) -> GraphState:
        """
        Determines whether the persona is good enough to proceed.

        Args:
            state (GraphState): The current state of the graph.

        Returns:
            GraphState: Updated with `fallback_persona_ok` boolean.
        """
        try:
            prompt = f"""
            You are performing a final check on a user persona for a marketing campaign.

            Persona: {state.user_persona}
            Objective: {state.campaign_objective}

            Is the persona sufficiently detailed and useful for targeting?
            Respond with only "yes" or "no".
            """.strip()

            result = await self.chain.ainvoke({"input": prompt})
            decision = result.content.strip().lower()

            state.fallback_persona_ok = decision == "yes"

            logger.info(f"PersonaQualityCheckNode decision: {decision}")

        except Exception as e:
            logger.error(f"PersonaQualityCheckNode failed: {str(e)}")
            state.fallback_persona_ok = False

        return state


# Manual test runner
if __name__ == "__main__":
    import asyncio

    async def test():
        test_state = GraphState(
            user_persona="30-year-old urban male, income ₹10L, interested in sneakers and football.",
            campaign_objective="Promote new sportswear product line",
        )

        node = PersonaQualityCheckNode()
        updated_state = await node.process(test_state)

        print(f"\nFallback Persona OK? {updated_state.fallback_persona_ok}")

    asyncio.run(test())
