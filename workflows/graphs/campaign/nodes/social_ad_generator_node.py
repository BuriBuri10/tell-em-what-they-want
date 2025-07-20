# from langchain_core.runnables import RunnableLambda
# from core.chain import ChainAccess
# from workflows.state import GraphState
# from logs.logging_config import logger


# class SocialAdGeneratorNode:
#     """
#     Generates social media-specific ad content tailored to a given campaign and persona.
#     """

#     def __init__(self):
#         """
#         Initializes the SocialAdGeneratorNode with a social-media-focused generation chain.
#         """
#         self.chain: RunnableLambda = ChainAccess.get_orchestrator().build(
#             prompt_map={"default": RunnableLambda(lambda x: x["input"])},
#             structured_output=None
#         )["default"]

#         logger.info("SocialAdGeneratorNode initialized.")

#     async def process(self, state: GraphState) -> GraphState:
#         """
#         Generates content optimized for social media ads.

#         Args:
#             state (GraphState): Current graph state.

#         Returns:
#             GraphState: Updated state with social ad content.
#         """
#         try:
#             prompt = f"""
#             You're a digital marketing expert.

#             Create a short and catchy social media ad based on:

#             --- Campaign Objective ---
#             {state.campaign_objective}

#             --- Target Audience Persona ---
#             {state.user_persona}

#             Guidelines:
#             - Keep it under 280 characters
#             - Include an emoji or two
#             - Use a conversational tone
#             - Include a call-to-action

#             Output should be one single post in plain text.
#             """

#             result = await self.chain.ainvoke({"input": prompt})
#             state.generated_ad = result.strip()

#             logger.info("Social media ad content generated.")

#         except Exception as e:
#             logger.error(f"SocialAdGeneratorNode failed: {str(e)}")

#         return state


# # Manual test block
# if __name__ == "__main__":
#     import asyncio

#     async def test():
#         test_state = GraphState(
#             campaign_objective="Raise awareness about eco-friendly travel options",
#             user_persona="Young urban professionals interested in sustainable lifestyle choices"
#         )

#         node = SocialAdGeneratorNode()
#         updated_state = await node.process(test_state)

#         print("\n✅ Generated Social Media Ad:\n")
#         print(updated_state.generated_ad_content)

#     asyncio.run(test())


from langchain_core.runnables import RunnableLambda
from core.chain import ChainAccess
from workflows.state import GraphState
from logs.logging_config import logger


class SocialAdGeneratorNode:
    """
    Generates social media-specific ad content tailored to a given campaign and persona.
    """

    def __init__(self):
        """
        Initializes the SocialAdGeneratorNode with a social-media-focused generation chain.
        """
        self.chain: RunnableLambda = ChainAccess.get_orchestrator().build(
            prompt_map={"default": RunnableLambda(lambda x: x["input"])},
            structured_output=None
        )["default"]

        logger.info("SocialAdGeneratorNode initialized.")

    async def process(self, state: GraphState) -> GraphState:
        """
        Generates a social media-friendly ad copy.

        Args:
            state (GraphState): Current campaign state.

        Returns:
            GraphState: Updated state with social ad content.
        """
        try:
            prompt = f"""
            You're a digital marketing expert.

            Create a short and catchy social media ad based on:

            --- Campaign Objective ---
            {state.campaign_objective}

            --- Target Audience Persona ---
            {state.user_persona}

            Guidelines:
            - Keep it under 280 characters
            - Include an emoji or two
            - Use a conversational tone
            - Include a call-to-action

            Output should be one single post in plain text.
            """

            result = await self.chain.ainvoke({"input": prompt})
            state.generated_ad = result.content.strip()

            logger.info("Social media ad content generated.")

        except Exception as e:
            logger.error(f"SocialAdGeneratorNode failed: {str(e)}")

        return state


# Manual test block
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

    asyncio.run(test())
