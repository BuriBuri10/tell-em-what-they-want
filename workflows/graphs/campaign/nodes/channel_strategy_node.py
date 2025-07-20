from langchain_core.runnables import RunnableLambda
from core.chain import ChainAccess
from workflows.state import GraphState
from logs.logging_config import logger


class ChannelStrategyNode:
    """
    Determines which platform-specific ad generation path to route to:
    Email, Social Media, or Web.
    """

    def __init__(self):
        """
        Initializes the routing chain.
        """
        self.chain: RunnableLambda = ChainAccess.get_orchestrator().build(
            prompt_map={"default": RunnableLambda(lambda x: x["input"])},
            structured_output=None,
        )["default"]

        logger.info("ChannelStrategyNode initialized.")

    async def process(self, state: GraphState) -> GraphState:
        """
        Chooses the most suitable channel for ad generation based on persona and constraints.

        Args:
            state (GraphState): The current workflow state.

        Returns:
            GraphState: Updated with `preferred_channel` value.
        """
        try:
            prompt = f"""
            Given the following details, recommend the best channel for ad delivery.
            Choose from: email, social, or web.

            Persona: {state.user_persona}
            Constraints: {state.channel_constraints or 'None'}
            Campaign Objective: {state.campaign_objective}

            Only respond with one of: "email", "social", or "web".
            """.strip()

            result = await self.chain.ainvoke({"input": prompt})
            decision = result.content.strip().lower()

            if decision in {"email", "social", "web"}:
                state.preferred_channel = decision
            else:
                state.preferred_channel = "web"  # default fallback

            logger.info(f"ChannelStrategyNode selected: {state.preferred_channel}")

        except Exception as e:
            logger.error(f"ChannelStrategyNode failed: {str(e)}")
            state.preferred_channel = "web"

        return state


# Manual test runner
if __name__ == "__main__":
    import asyncio

    async def test():
        test_state = GraphState(
            campaign_objective="Drive traffic to the product landing page",
            user_persona="Tech-savvy students and gamers",
            channel_constraints="No email"
        )

        node = ChannelStrategyNode()
        updated_state = await node.process(test_state)

        print(f"\nPreferred Channel: {updated_state.preferred_channel}")

    asyncio.run(test())
