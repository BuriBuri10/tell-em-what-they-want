from langchain_core.runnables import RunnableLambda
from core.chain import ChainAccess
from workflows.state import GraphState
from logs.logging_config import logger


class FallbackPersonaNode:
    """
    Fallback node to handle cases where persona enrichment fails or user data is too sparse.
    Provides a generic, platform-agnostic persona to proceed with campaign logic.
    """

    def __init__(self):
        """
        Initializes the FallbackPersonaNode with a basic persona template chain.
        """
        self.chain: RunnableLambda = ChainAccess.get_orchestrator().build(
            prompt_map={"default": RunnableLambda(lambda x: x["input"])},
            structured_output=None,
        )["default"]

        logger.info("FallbackPersonaNode initialized.")

    async def process(self, state: GraphState) -> GraphState:
        """
        Injects a generic fallback persona into the state if personalization is not feasible.

        Args:
            state (GraphState): The current graph state.

        Returns:
            GraphState: Updated with a default persona for continuation.
        """
        try:
            prompt = f"""
            The campaign lacks a well-defined user persona. Based on the campaign objective:

            Objective: "{state.campaign_objective}"

            Generate a safe, broadly-targeted generic persona that can be used across platforms.
            Avoid any personal or risky assumptions. Write as a plain sentence, not a list.
            """.strip()

            result = await self.chain.ainvoke({"input": prompt})
            fallback_persona = result.content.strip()

            state.user_persona = {"description": fallback_persona}  # ✅ Wrapped in a dict
            logger.info(f"Fallback Persona Applied: {fallback_persona}")

        except Exception as e:
            logger.error(f"FallbackPersonaNode failed: {str(e)}")

        return state


# Manual test runner
if __name__ == "__main__":
    import asyncio

    async def test():
        test_state = GraphState(
            # user_persona="",
            user_persona = {"description": "do it"},
            campaign_objective="Promote sustainable packaging solutions"
        )

        node = FallbackPersonaNode()
        updated_state = await node.process(test_state)

        print(f"\nFallback Persona: {updated_state.user_persona}")

    asyncio.run(test())
