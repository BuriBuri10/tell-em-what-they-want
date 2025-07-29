from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableLambda

from core.chain import ChainAccess
from workflows.state import GraphState
from logs.logging_config import logger


class ChannelConstraintsSchema(BaseModel):
    constraints: str = Field(..., description="Channel-specific constraints for campaign delivery.")


class ChannelConstraintsNode:
    """
    Determines and documents channel-specific constraints based on the enriched persona
    and campaign context.
    """

    def __init__(self):
        """
        Initializes the node with a structured output chain for constraint extraction.
        """
        self.chain: RunnableLambda = ChainAccess.get_orchestrator().build(
            prompt_map={"default": RunnableLambda(lambda x: x["input"])},
            structured_output=ChannelConstraintsSchema
        )["default"]

        logger.info("ChannelConstraintsNode initialized.")

    async def process(self, state: GraphState) -> GraphState:
        """
        Analyzes enriched user persona and campaign objectives to derive channel constraints.

        Args:
            state (GraphState): Current workflow state.

        Returns:
            GraphState: Updated with channel-specific constraints.
        """
        try:
            user_persona = state.user_persona
            # user_persona = state.user_persona.get("description", "a generic customer")
            objective = state.campaign_objective or "drive general awareness and engagement"

            prompt = f"""
            You are a digital marketing compliance strategist.

            Based on the following inputs:
            - Campaign Objective: "{objective}"
            - Enriched User Persona: "{user_persona}"

            Determine the most critical **channel-specific delivery constraints**. 
            Include legal, technical, content-format, and targeting limitations across:
            - Social Media (e.g., Instagram, LinkedIn, TikTok)
            - Email Marketing
            - Web or Display Ads
            - SMS or Push Notifications (if applicable)

            Return channel-specific constraints as plain text, without markdown formatting, bullet points, or special characters like asterisks.
            Structure the output as simple numbered or plain sentences suitable for a JSON field.
            """.strip()

            result: ChannelConstraintsSchema = await self.chain.ainvoke({"input": prompt})
            state.channel_constraints = {"constraints": result.constraints.strip()}

            logger.info("Channel constraints generated.")
        except Exception as e:
            logger.error(f"ChannelConstraintsNode failed: {str(e)}")
            state.channel_constraints = {
                "constraints": "No specific constraints identified. Default platform rules will apply."
            }

        return state

# from langchain_core.runnables import RunnableLambda
# from core.chain import ChainAccess
# from workflows.state import GraphState
# from logs.logging_config import logger


# class ChannelConstraintsNode:
#     """
#     Validates and extracts any channel or media constraints from user input.
#     """

#     def __init__(self):
#         """
#         Initializes the constraint extraction chain using an inline prompt.
#         """
#         self.chain: RunnableLambda = ChainAccess.get_orchestrator().build(
#             prompt_map={"default": RunnableLambda(lambda x: x["input"])},
#             structured_output=None
#         )["default"]

#         logger.info("ChannelConstraintsNode initialized.")

#     async def process(self, state: GraphState) -> GraphState:
#         """
#         Extracts and flags constraints such as platform or media exclusions/preferences.

#         Args:
#             state (GraphState): Graph state containing raw user instructions or constraints.

#         Returns:
#             GraphState: Updated state with channel_constraints and flag for constraint awareness.
#         """
#         try:
#             # raw_constraints = state.channel_instructions or "No constraints were provided."

#             prompt_text = f"""
#             Analyze the following campaign instructions and identify any platform or media constraints:

#             Examples of constraints:
#             - Only Instagram
#             - Exclude TikTok
#             - No video content
#             - Use only text-based posts

#             If any constraints are found, list them as bullet points. If none, return "No constraints".

#             Format your response clearly.
#             """.strip()

#             result = await self.chain.ainvoke({"input": prompt_text})
#             parsed_constraints = result.content.strip()

#             has_constraints = parsed_constraints.lower() != "no constraints"

#             # state.channel_constraints = parsed_constraints
#             state.channel_constraints = {
#                 "raw_text": parsed_constraints,
#                 "parsed_constraints": []  # or whatever structure you're extracting
#             }

#             state.constraints_found = has_constraints

#             logger.info(f"Constraints extracted: {parsed_constraints}")

#         except Exception as e:
#             logger.error(f"Constraint extraction failed: {str(e)}")
#             state.channel_constraints = "No constraints"
#             state.constraints_found = False

#         return state


# Manual test runner
if __name__ == "__main__":
    import asyncio

    async def test():
        test_state = GraphState(
            channel_instructions="Client wants to avoid TikTok and video formats, only use LinkedIn."
        )

        validator = ChannelConstraintsNode()
        updated_state = await validator.process(test_state)

        print(f"Constraints Found: {updated_state.constraints_found}")
        print(f"Extracted Constraints:\n{updated_state.channel_constraints}")

    asyncio.run(test())
