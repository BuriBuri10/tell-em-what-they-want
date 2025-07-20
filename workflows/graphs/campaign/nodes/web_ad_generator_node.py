from langchain_core.runnables import RunnableLambda
from core.chain import ChainAccess
from workflows.state import GraphState
from logs.logging_config import logger


class WebAdGeneratorNode:
    """
    Generates ad content tailored for website or landing page placements.
    """

    def __init__(self):
        """
        Initializes the WebAdGeneratorNode with a web-optimized ad generation chain.
        """
        self.chain: RunnableLambda = ChainAccess.get_orchestrator().build(
            prompt_map={"default": RunnableLambda(lambda x: x["input"])},
            structured_output=None
        )["default"]

        logger.info("WebAdGeneratorNode initialized.")

    async def process(self, state: GraphState) -> GraphState:
        """
        Generates headline + body copy suitable for website or landing page.

        Args:
            state (GraphState): Current graph state.

        Returns:
            GraphState: Updated state with website ad content.
        """
        try:
            prompt = f"""
            You are a copywriter designing ads for a landing page.

            Based on the following information, create:
            - A strong headline (max 10 words)
            - A 2–3 sentence persuasive body copy
            - A call-to-action (CTA) line

            --- Campaign Objective ---
            {state.campaign_objective}

            --- Target Persona ---
            {state.user_persona}

            Make it sound benefit-driven and web-optimized.
            Output should be in the format:
            Headline: ...
            Body: ...
            CTA: ...
            """

            result = await self.chain.ainvoke({"input": prompt})
            state.generated_ad = result.content.strip()

            logger.info("Web ad content generated.")

        except Exception as e:
            logger.error(f"WebAdGeneratorNode failed: {str(e)}")

        return state


# Manual test block
if __name__ == "__main__":
    import asyncio

    async def test():
        test_state = GraphState(
            campaign_objective="Promote a new line of ergonomic office furniture",
            user_persona="Remote tech workers aged 25-40 seeking comfort and productivity"
        )

        node = WebAdGeneratorNode()
        updated_state = await node.process(test_state)

        print("\n✅ Generated Web Ad Content:\n")
        print(updated_state.generated_ad_content)

    asyncio.run(test())
