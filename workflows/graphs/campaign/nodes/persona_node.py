from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableLambda
from core.chain import ChainAccess
from workflows.state import GraphState
from logs.logging_config import logger


class PersonaSchema(BaseModel):
    description: str = Field(..., description="Structured user persona description.")


class UserPersonaNode:
    """
    Node responsible for generating a structured user persona based on the user segment.
    """

    def __init__(self):
        """
        Initializes the UserPersonaNode with a simple prompt-based chain.
        """
        self.chain: RunnableLambda = ChainAccess.get_orchestrator().build(
            prompt_map={"default": RunnableLambda(lambda x: x["input"])},
            structured_output=PersonaSchema
        )["default"]

        logger.info("UserPersonaNode initialized with persona generation chain.")

    async def process(self, state: GraphState) -> GraphState:
        """
        Generates a user persona from the user segment and updates the state.

        Args:
            state (GraphState): Current workflow state.

        Returns:
            GraphState: Updated with the generated user persona.
        """
        try:
            prompt = """
            You are a senior marketing strategist tasked with creating a detailed user persona for campaign planning.

            Please generate a structured persona representing a typical digital user based on general online behavior patterns.

            Your output must be a clear and concise 'single sentence' that captures:
            - The user's 'age range' (e.g., 25-34)
            - Their 'primary interests or hobbies'
            - Their typical 'online behavior' (e.g., time spent on platforms, content preferences)
            - Their 'communication tone preferences' (e.g., formal, casual, witty)

            Ensure the description is natural and professional, suitable for presentation in an executive campaign brief.

            Do not mention that this is a generated persona or reference yourself.

            Example:
            "A tech-savvy individual aged 25-34 who enjoys fitness and personal finance, frequently engages with video content on mobile platforms, and responds well to direct, conversational messaging."
            """.strip()

            result: PersonaSchema = await self.chain.ainvoke({"input": prompt})
            state.user_persona = {"description": result.description.strip()}
            logger.info(f"User persona generated: {state.user_persona['description']}")

        except Exception as e:
            logger.error(f"UserPersonaNode failed: {str(e)}")
            state.user_persona = {
                "description": "A generic user with broad interests and standard online behavior."
            }

        return state
