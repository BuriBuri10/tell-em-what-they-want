from langchain_core.runnables import RunnableLambda
from core.chain import ChainAccess
from workflows.state import GraphState
from logs.logging_config import logger


class ComplianceRevisionNode:
    """
    Regenerates ad content to meet compliance and brand safety requirements.
    """

    def __init__(self):
        """
        Initializes the ComplianceRevisionNode with a regeneration prompt.
        """
        self.chain: RunnableLambda = ChainAccess.get_orchestrator().build(
            prompt_map={"default": RunnableLambda(lambda x: x["input"])},
            structured_output=None
        )["default"]

        logger.info("ComplianceRevisionNode initialized.")

    async def process(self, state: GraphState) -> GraphState:
        """
        Revises the generated ad copy to meet legal and brand compliance.

        Args:
            state (GraphState): The current workflow state.

        Returns:
            GraphState: Updated state with revised ad content.
        """
        try:
            prompt = f"""
            The following ad content may not meet compliance standards:

            --- Original Ad Content ---
            {state.generated_ad_content}

            --- Campaign Objective ---
            {state.campaign_objective}

            --- Persona ---
            {state.user_persona}

            Please revise this ad copy to ensure it is legally compliant and aligns with brand guidelines.
            Avoid sensitive claims, be truthful, and respect platform-specific ad policies.
            """.strip()

            result = await self.chain.ainvoke({"input": prompt})
            revised_content = result.content.strip()

            state.generated_ad_content = revised_content
            logger.info("Compliance revision completed successfully.")

        except Exception as e:
            logger.error(f"ComplianceRevisionNode failed: {str(e)}")

        return state


# Manual test block
if __name__ == "__main__":
    import asyncio

    async def test():
        test_state = GraphState(
            campaign_objective="Promote weight loss supplement to young adults",
            user_persona="Health-conscious individuals in their 20s and 30s",
            generated_ad_content="Lose 10 kg in 7 days with our miracle pills!",
        )

        node = ComplianceRevisionNode()
        updated_state = await node.process(test_state)

        print("\n✅ Revised Ad Content:\n", updated_state.generated_ad_content)

    asyncio.run(test())
