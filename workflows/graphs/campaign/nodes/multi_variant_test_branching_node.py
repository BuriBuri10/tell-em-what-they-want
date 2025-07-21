from langchain_core.runnables import RunnableLambda
from core.chain import ChainAccess
from workflows.state import GraphState
from logs.logging_config import logger


class ABTestingNode:
    """
    Creates multiple ad variants for A/B or multivariate testing.
    """

    def __init__(self):
        """
        Initializes the MultiVariantTestNode with a multi-variant generation prompt.
        """
        self.chain: RunnableLambda = ChainAccess.get_orchestrator().build(
            prompt_map={"default": RunnableLambda(lambda x: x["input"])},
            structured_output=None
        )["default"]

        logger.info("MultiVariantTestNode initialized.")

    async def process(self, state: GraphState) -> GraphState:
        """
        Generates A/B ad variants for testing performance.

        Args:
            state (GraphState): Current campaign state.

        Returns:
            GraphState: Updated state with generated ad variants.
        """
        try:
            prompt = f"""
            Based on the following campaign context:

            --- Objective ---
            {state.campaign_objective}

            --- Target Persona ---
            {state.user_persona}

            --- Original Ad Content ---
            {state.generated_ad}

            Generate 2 alternative versions of this ad content for A/B testing. 
            Ensure they maintain the same intent but vary in tone, hook, or CTA.
            Respond in a numbered list.
            """.strip()

            result = await self.chain.ainvoke({"input": prompt})
            variants = result.content.strip().split("\n")

            state.ad_variants = [variant for variant in variants if variant.strip()]
            logger.info("Multi-variant test content generated.")

        except Exception as e:
            logger.error(f"MultiVariantTestNode failed: {str(e)}")

        return state


# Manual test block
if __name__ == "__main__":
    import asyncio

    async def test():
        test_state = GraphState(
            campaign_objective="Increase app downloads for a fitness tracker",
            user_persona="Millennial tech-savvy fitness enthusiasts",
            generated_ad_content="Track your workouts and crush your goals with our new app!",
        )

        node = ABTestingNode()
        updated_state = await node.process(test_state)

        print("\nAd Variants Generated:\n")
        for variant in updated_state.ad_variants:
            print(variant)

    asyncio.run(test())
