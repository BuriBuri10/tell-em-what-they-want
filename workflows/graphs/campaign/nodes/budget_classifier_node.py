from langchain_core.runnables import RunnableLambda
from core.chain import ChainAccess
from workflows.state import GraphState
from logs.logging_config import logger


class BudgetClassifierNode:
    """
    Classifies the campaign budget level to influence downstream strategy decisions.
    """

    def __init__(self):
        """
        Initializes the budget classification chain with an inline prompt.
        """
        self.chain: RunnableLambda = ChainAccess.get_orchestrator().build(
            prompt_map={"default": RunnableLambda(lambda x: x["input"])},
            structured_output=None
        )["default"]

        logger.info("BudgetClassifierNode initialized.")

    async def process(self, state: GraphState) -> GraphState:
        """
        Determines whether the campaign budget is 'budget' or 'premium'.

        Args:
            state (GraphState): Graph state containing budget_hint or related clues.

        Returns:
            GraphState: Updated state with budget_class set.
        """
        try:
            budget_hint = state.budget_hint or "No specific budget mentioned."

            prompt_text = f"""
            Classify the following marketing campaign's budget as either 'budget' or 'premium'.

            Hint: {budget_hint}

            Criteria:
            - Use 'budget' for minimal spend, low-touch campaigns.
            - Use 'premium' for high-touch, high-effort, or influencer-driven campaigns.
            - If unclear, assume 'budget'.

            Respond with only one word: 'budget' or 'premium'.
            """.strip()

            result = await self.chain.ainvoke({"input": prompt_text})
            verdict = result.content.strip().lower()

            if verdict not in ["budget", "premium"]:
                logger.warning(f"Unexpected budget classification: {verdict}")
                verdict = "budget"

            state.budget_class = verdict
            logger.info(f"Budget classified as: {verdict}")

        except Exception as e:
            logger.error(f"Budget classification failed: {str(e)}")
            state.budget_class = "budget"

        return state


# Manual test runner
if __name__ == "__main__":
    import asyncio

    async def test():
        test_state = GraphState(
            budget_hint="Client requested a luxury campaign with celebrity endorsements."
        )

        classifier = BudgetClassifierNode()
        updated_state = await classifier.process(test_state)

        print(f"Budget classification: {updated_state.budget_class}")

    asyncio.run(test())
