from langchain_core.runnables import RunnableLambda
from core.chain import ChainAccess
from workflows.state import GraphState
from logs.logging_config import logger


class EmailAdGeneratorNode:
    """
    Generates email-specific ad content based on campaign objective and persona.
    """

    def __init__(self):
        """
        Initializes the EmailAdGeneratorNode with an email-focused generation chain.
        """
        self.chain: RunnableLambda = ChainAccess.get_orchestrator().build(
            prompt_map={"default": RunnableLambda(lambda x: x["input"])},
            structured_output=None
        )["default"]

        logger.info("EmailAdGeneratorNode initialized.")

    async def process(self, state: GraphState) -> GraphState:
        """
        Generates an email-formatted ad copy.

        Args:
            state (GraphState): Current campaign state.

        Returns:
            GraphState: Updated state with email ad content.
        """
        try:
            prompt = f"""
            You are a marketing assistant.

            Create a persuasive email campaign for the following:

            --- Objective ---
            {state.campaign_objective}

            --- Target Persona ---
            {state.user_persona}

            The email should include:
            - A catchy subject line
            - An engaging opening
            - A main body explaining the value
            - A clear call-to-action

            Format as plain text email content.
            """

            result = await self.chain.ainvoke({"input": prompt})
            state.generated_ad = result.content.strip()

            logger.info("Email ad content generated.")

        except Exception as e:
            logger.error(f"EmailAdGeneratorNode failed: {str(e)}")

        return state


if __name__ == "__main__":
    import asyncio

async def test():
    test_state = GraphState(
        campaign_objective="Raise awareness about eco-friendly travel options",
        user_persona={
            "description": "Young urban professional who values sustainability and enjoys social media.",
            "preferences": ["eco-friendly products", "sustainable lifestyle choices"],
            "demographics": {
                "age": "25-35",
                "location": "urban"
            }
        }
    )

    node = SocialAdGeneratorNode()
    updated_state = await node.process(test_state)

    print("\n✅ Generated Social Media Ad:\n")
    print(updated_state.generated_ad)
