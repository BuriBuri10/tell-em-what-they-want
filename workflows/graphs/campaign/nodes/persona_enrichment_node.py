from langchain_core.runnables import RunnableLambda
from core.chain import ChainAccess
from workflows.state import GraphState
from logs.logging_config import logger


class PersonaEnrichmentNode:
    """
    Enriches a weak or generic persona using campaign context and inferred traits.
    Triggered when the persona quality check fails.
    """

    def __init__(self):
        """
        Initializes the PersonaEnrichmentNode with a refinement chain.
        """
        self.chain: RunnableLambda = ChainAccess.get_orchestrator().build(
            prompt_map={"default": RunnableLambda(lambda x: x["input"])},
            structured_output=None,
        )["default"]

        logger.info("PersonaEnrichmentNode initialized.")

    async def process(self, state: GraphState) -> GraphState:
        """
        Enhances the current user persona by inferring richer demographic, behavioral, and psychographic traits.

        Args:
            state (GraphState): The current workflow state.

        Returns:
            GraphState: Updated with enriched persona data.
        """
        try:
            prompt = f"""
            The following user persona appears generic or incomplete:

            Current Persona: "{state.user_persona}"

            Campaign Objective: "{state.campaign_objective}"

            Please enrich this persona by inferring missing attributes such as:
            - Age or age range
            - Location or region
            - Interests and hobbies
            - Preferred social platforms
            - Typical buying behavior

            Only return the enriched persona description. Avoid explanation or bullet points.
            """.strip()

            result = await self.chain.ainvoke({"input": prompt})
            enriched_persona = result.content.strip()
            
            state.user_persona = {"description": enriched_persona}  # ✅ now a valid dict
            # state.user_persona = enriched_persona

            logger.info(f"Enriched Persona: {enriched_persona}")

        except Exception as e:
            logger.error(f"PersonaEnrichmentNode failed: {str(e)}")

        return state


# Manual test runner
if __name__ == "__main__":
    import asyncio

    async def test():
        test_state = GraphState(
            user_persona="Tech-savvy young adult",
            campaign_objective="Drive awareness for new smartphone accessories",
        )

        node = PersonaEnrichmentNode()
        updated_state = await node.process(test_state)

        print(f"\nEnriched Persona: {updated_state.user_persona}")

    asyncio.run(test())
