# # strategy_node.py

from langchain_core.runnables import RunnableLambda
from core.chain import ChainAccess
from workflows.state import GraphState
from logs.logging_config import logger


class StrategyNode:
    """
    Node that formulates a campaign objective based on user persona.
    """

    def __init__(self):
        """
        Initializes the campaign strategy generation chain.
        """
        self.chain: RunnableLambda = ChainAccess.get_orchestrator().build(
            prompt_map={"default": RunnableLambda(lambda x: x["input"])},
            structured_output=None
        )["default"]

        logger.info("StrategyNode initialized.")

    async def process(self, state: GraphState) -> GraphState:
        """
        Generates a campaign objective tailored to the user persona.

        Args:
            state (GraphState): Workflow state containing user persona.

        Returns:
            GraphState: Updated state with campaign objective.
        """
        try:
            user_persona = state.user_persona
            if not user_persona:
                raise ValueError("User persona is missing.")

            prompt_text = f"""
            Based on the following user persona, define a high-level campaign objective:

            User Persona:
            {user_persona}

            Instructions:
            - Suggest a concise and actionable campaign goal.
            - Align the goal with the user's demographics, interests, and motivations.
            - Use a brand-aware tone suitable for marketing planning.

            Respond with just the objective sentence.
            """.strip()

            result = await self.chain.ainvoke({"input": prompt_text})
            state.campaign_objective = result.content
            logger.info("Campaign objective generated successfully.")

        except Exception as e:
            logger.error(f"Strategy generation failed: {str(e)}")
            state.campaign_objective = "Raise awareness about our product among young users."

        return state


# Manual test runner
if __name__ == "__main__":
    import asyncio

    async def test():
        from workflows.state import GraphState

        test_state = GraphState(
            user_persona={
                "age_range": "25-34",
                "interests": "fitness, wearable tech, lifestyle productivity",
                "description": "Health-conscious tech enthusiasts who follow fitness trends and use smartwatches."
            }
        )

        strategy_node = StrategyNode()
        updated_state = await strategy_node.process(test_state)

        print(f"\nGenerated Campaign Objective:\n{updated_state.campaign_objective}")

    asyncio.run(test())
