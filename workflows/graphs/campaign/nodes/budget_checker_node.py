from langchain_core.runnables import RunnableLambda
from core.chain import ChainAccess
from workflows.state import GraphState
from logs.logging_config import logger


class BudgetCheckNode:
    """
    Node that verifies if the campaign has sufficient remaining budget
    to proceed with ad generation.
    """

    def __init__(self):
        """
        Initializes the chain for checking budget constraints.
        """
        self.chain: RunnableLambda = ChainAccess.get_orchestrator().build(
            prompt_map={"default": RunnableLambda(lambda x: x["input"])},
            structured_output=None
        )["default"]

        logger.info("BudgetCheckNode initialized with inline prompt chain.")

    async def process(self, state: GraphState) -> GraphState:
        """
        Checks if the current campaign has sufficient budget to continue.

        Args:
            state (GraphState): Current graph state with budget info.

        Returns:
            GraphState: Updated state with budget verification outcome.
        """
        try:
            current_budget = state.budget or 0.0

            prompt_text = f"""
            The current campaign budget is {current_budget} USD.

            Decide whether this budget is sufficient to proceed with ad generation.
            - If it's above $1000, consider it sufficient.
            - Otherwise, consider it insufficient and flag it.

            Respond with "sufficient" or "insufficient" only.
            """.strip()

            result = await self.chain.ainvoke({"input": prompt_text})
            outcome = result.content.strip().lower()

            state.budget_check_passed = outcome == "sufficient"

            logger.info(f"BudgetCheckNode result: {outcome}")

        except Exception as e:
            logger.error(f"Budget check failed: {str(e)}")
            state.budget_check_passed = False

        return state


# Manual test runner
if __name__ == "__main__":
    import asyncio

    async def test():
        from workflows.state import GraphState

        test_state = GraphState(
            budget=850.0  # Try 1500.0 for sufficient case
        )

        node = BudgetCheckNode()
        updated_state = await node.process(test_state)

        print(f"\nBudget check passed: {updated_state.budget_check_passed}")

    asyncio.run(test())
