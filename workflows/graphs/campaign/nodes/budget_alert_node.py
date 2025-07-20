from langchain_core.runnables import RunnableLambda
from core.chain import ChainAccess
from workflows.state import GraphState
from logs.logging_config import logger


class BudgetAlertNode:
    """
    Triggers when the campaign budget is insufficient.
    Generates a human-readable alert or recommendation for corrective action.
    """

    def __init__(self):
        """
        Initializes the BudgetAlertNode with a basic response chain.
        """
        self.chain: RunnableLambda = ChainAccess.get_orchestrator().build(
            prompt_map={"default": RunnableLambda(lambda x: x["input"])},
            structured_output=None
        )["default"]

        logger.info("BudgetAlertNode initialized.")

    async def process(self, state: GraphState) -> GraphState:
        """
        Appends a budget alert message to the state.

        Args:
            state (GraphState): The current workflow state.

        Returns:
            GraphState: Updated state with alert message.
        """
        try:
            prompt = f"""
            The campaign budget seems insufficient to execute the planned strategy effectively.

            Objective: {state.campaign_objective}
            Persona: {state.user_persona}

            Provide a brief, polite recommendation for next steps—e.g., scale back targeting,
            increase budget, or consider alternate channels.
            """.strip()

            result = await self.chain.ainvoke({"input": prompt})
            alert_message = result.content.strip()

            state.alerts.append(alert_message)
            logger.warning(f"Budget Alert Triggered: {alert_message}")

        except Exception as e:
            logger.error(f"BudgetAlertNode failed: {str(e)}")

        return state


# Manual test block
if __name__ == "__main__":
    import asyncio

    async def test():
        test_state = GraphState(
            campaign_objective="Launch summer discount offer for eco-friendly shoes",
            user_persona="Young urban professionals interested in sustainability",
            alerts=[]
        )

        node = BudgetAlertNode()
        updated_state = await node.process(test_state)

        print("\nBudget Alert:", updated_state.alerts[-1])

    asyncio.run(test())
