from langchain_core.runnables import RunnableLambda
from core.chain import ChainAccess
from workflows.state import GraphState
from logs.logging_config import logger


class MultiVariantTestNode:
    """
    Node that decides whether A/B or multivariate testing is needed for the ad.
    Useful for optimizing campaigns based on hypotheses or user input.
    """

    def __init__(self):
        """
        Initializes the decision chain using a basic prompt.
        """
        self.chain: RunnableLambda = ChainAccess.get_orchestrator().build(
            prompt_map={"default": RunnableLambda(lambda x: x["input"])},
            structured_output=None,
        )["default"]

        logger.info("MultiVariantTestNode initialized.")

    async def process(self, state: GraphState) -> GraphState:
        """
        Determines if A/B testing or multi-variant testing should be conducted

        Args:
            state (GraphState): The current state of the workflow.

        Returns:
            GraphState: Updated with `multi_variant_required` boolean.
        """
        try:
            prompt = f"""
            Evaluate the following campaign context and determine whether 
            multivariate (A/B) testing is required:

            Campaign Objective: {state.campaign_objective}
            Persona Details: {state.user_persona}
            Budget Tier: {state.budget_hint}
            Constraints: {state.channel_constraints or 'None'}

            Respond only with "yes" or "no".
            """.strip()

            result = await self.chain.ainvoke({"input": prompt})
            decision = result.content.strip().lower()

            state.multi_variant_required = decision == "yes"

            logger.info(f"MultiVariantTestNode decision: {decision}")

        except Exception as e:
            logger.error(f"MultiVariantTestNode failed: {str(e)}")
            state.multi_variant_required = False

        return state


# Manual test runner
if __name__ == "__main__":
    import asyncio

    async def test():
        test_state = GraphState(
            campaign_objective="Test which subject line leads to higher engagement",
            user_persona={"summary": "Young professionals in marketing roles"},
            budget_tier="premium",
        )

        node = MultiVariantTestNode()
        updated_state = await node.process(test_state)

        print(f"\nMulti-variant required: {updated_state.multi_variant_required}")

    asyncio.run(test())
