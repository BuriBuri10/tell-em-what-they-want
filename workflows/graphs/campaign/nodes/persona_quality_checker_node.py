from langchain_core.runnables import RunnableLambda
from core.chain import ChainAccess
from workflows.state import GraphState
from logs.logging_config import logger


class PersonaQualityCheckerNode:
    """
    Checks the quality of the user persona.
    Flags if the persona is too shallow or lacks essential attributes.
    """

    def __init__(self):
        """
        Initializes the persona quality checking chain with an inline dynamic prompt.
        """
        self.chain: RunnableLambda = ChainAccess.get_orchestrator().build(
            prompt_map={"default": RunnableLambda(lambda x: x["input"])},
            structured_output=None
        )["default"]

        logger.info("PersonaQualityCheckerNode initialized.")

    async def process(self, state: GraphState) -> GraphState:
        """
        Evaluates whether the user persona contains sufficient information.

        Args:
            state (GraphState): Graph state containing the user_persona.

        Returns:
            GraphState: Updated state with `persona_is_enriched` flag set.
        """
        try:
            if not state.user_persona or not isinstance(state.user_persona, dict):
                raise ValueError("user_persona must be a populated dictionary.")

            persona_description = state.user_persona.get("description", "")
            age = state.user_persona.get("age_range", "")
            interests = state.user_persona.get("interests", "")

            prompt_text = f"""
            Evaluate the completeness of the following user persona:

            Description: {persona_description}
            Age Range: {age}
            Interests: {interests}

            Criteria:
            - Includes demographic details (e.g., age, region)
            - Mentions at least one interest or behavioral trait
            - Mentions platform/channel or preference

            Respond with "Good" if enriched, otherwise "Poor".
            """.strip()

            result = await self.chain.ainvoke({"input": prompt_text})
            verdict = result.content.strip().lower()

            state.persona_is_enriched = verdict == "good"
            logger.info(f"Persona quality check result: {verdict}")

        except Exception as e:
            logger.error(f"Persona quality check failed: {str(e)}")
            state.persona_is_enriched = False

        return state


# Manual test runner
if __name__ == "__main__":
    import asyncio

    async def test():
        test_state = GraphState(
            user_persona={
                "description": "Professionals in their 30s active on LinkedIn and into productivity tools.",
                "age_range": "30-40",
                "interests": "business, time management, apps"
            }
        )

        checker = PersonaQualityCheckerNode()
        updated_state = await checker.process(test_state)

        print(f"Persona is enriched: {updated_state.persona_is_enriched}")

    asyncio.run(test())
