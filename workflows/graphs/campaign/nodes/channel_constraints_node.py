from langchain_core.runnables import RunnableLambda
from core.chain import ChainAccess
from workflows.state import GraphState
from logs.logging_config import logger


class ChannelConstraintsNode:
    """
    Validates and extracts any channel or media constraints from user input.
    """

    def __init__(self):
        """
        Initializes the constraint extraction chain using an inline prompt.
        """
        self.chain: RunnableLambda = ChainAccess.get_orchestrator().build(
            prompt_map={"default": RunnableLambda(lambda x: x["input"])},
            structured_output=None
        )["default"]

        logger.info("ChannelConstraintsNode initialized.")

    async def process(self, state: GraphState) -> GraphState:
        """
        Extracts and flags constraints such as platform or media exclusions/preferences.

        Args:
            state (GraphState): Graph state containing raw user instructions or constraints.

        Returns:
            GraphState: Updated state with channel_constraints and flag for constraint awareness.
        """
        try:
            raw_constraints = state.channel_instructions or "No constraints were provided."

            prompt_text = f"""
            Analyze the following campaign instructions and identify any platform or media constraints:

            Instructions: {raw_constraints}

            Examples of constraints:
            - Only Instagram
            - Exclude TikTok
            - No video content
            - Use only text-based posts

            If any constraints are found, list them as bullet points. If none, return "No constraints".

            Format your response clearly.
            """.strip()

            result = await self.chain.ainvoke({"input": prompt_text})
            parsed_constraints = result.content.strip()

            has_constraints = parsed_constraints.lower() != "no constraints"

            # state.channel_constraints = parsed_constraints
            state.channel_constraints = {
                "raw_text": parsed_constraints,
                "parsed_constraints": []  # or whatever structure you're extracting
            }

            state.constraints_found = has_constraints

            logger.info(f"Constraints extracted: {parsed_constraints}")

        except Exception as e:
            logger.error(f"Constraint extraction failed: {str(e)}")
            state.channel_constraints = "No constraints"
            state.constraints_found = False

        return state


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
