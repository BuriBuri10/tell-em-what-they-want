from langchain_core.runnables import RunnableLambda
from core.chain import ChainAccess
from workflows.state import GraphState
from logs.logging_config import logger


class ComplianceCheckNode:
    """
    Node that performs a compliance check on the generated ad content.
    Ensures the ad follows legal, ethical, and brand guidelines.
    """

    def __init__(self):
        """
        Initializes the chain that simulates or invokes a compliance validation check.
        """
        self.chain: RunnableLambda = ChainAccess.get_orchestrator().build(
            prompt_map={"default": RunnableLambda(lambda x: x["input"])},
            structured_output=None
        )["default"]

        logger.info("ComplianceCheckNode initialized with inline compliance prompt.")

    async def process(self, state: GraphState) -> GraphState:
        """
        Checks if the ad copy meets compliance standards.

        Args:
            state (GraphState): The current graph state, including ad content.

        Returns:
            GraphState: Updated graph state with compliance_check_passed flag.
        """
        try:
            ad_content = state.generated_ad or ""

            prompt_text = f"""
            Review the following ad content for compliance with legal, ethical,
            and brand guidelines:

            --- Ad Content Start ---
            {ad_content}
            --- Ad Content End ---

            Respond with "compliant" or "non-compliant".
            """.strip()

            result = await self.chain.ainvoke({"input": prompt_text})
            outcome = result.content.strip().lower()

            state.compliance_check_passed = outcome == "compliant"

            logger.info(f"ComplianceCheckNode result: {outcome}")

        except Exception as e:
            logger.error(f"Compliance check failed: {str(e)}")
            state.compliance_check_passed = False

        return state


# Manual test runner
if __name__ == "__main__":
    import asyncio

    async def test():
        from workflows.state import GraphState

        test_state = GraphState(
            generated_ad="Introducing EcoSoothe, our plant-based skin solution. No harsh chemicals."
        )

        node = ComplianceCheckNode()
        updated_state = await node.process(test_state)

        print(f"\nCompliance check passed: {updated_state.compliance_check_passed}")

    asyncio.run(test())
