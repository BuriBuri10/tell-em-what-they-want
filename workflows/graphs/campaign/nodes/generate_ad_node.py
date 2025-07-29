from langchain_core.runnables import RunnableLambda
from core.chain import ChainAccess
from workflows.state import GraphState
from logs.logging_config import logger
from core.ad_generator_engine import AdOutput
from core.utils.campaign_recs import CampaignReportSaver


class GenerateAdNode:
    """
    Node responsible for generating an advertisement copy using strategy, user segment, and product details.
    """

    def __init__(self):
        self.chain: RunnableLambda = ChainAccess.get_orchestrator().build(
            prompt_map={"default": RunnableLambda(lambda x: x["input"])},
            structured_output=AdOutput
        )["default"]
        logger.info("GenerateAdNode initialized with inline prompt chain.")

    async def process(self, state: GraphState) -> GraphState:
        """
        Generates a personalized advertisement based on user segment, strategy, and product details.
        Saves the generated ad into a campaign report before human review.

        Args:
            state (GraphState): The current workflow state.

        Returns:
            GraphState: Updated state with generated ad content and flags.
        """
        try:
            if not state.user_segment or not state.strategy:
                logger.debug(f"user_segment: {state.user_segment}, strategy: {state.strategy}")
                logger.warning("Missing user segment or campaign recommendation; falling back to defaults.")
                state.user_segment = state.user_segment or "standard segment"
                state.strategy = state.strategy or "general awareness"
                state.product_details = state.product_details or "a great product"

            # Construct structured output-compatible prompt
            prompt_text = f"""
                            You are an AI copywriter tasked with writing a compelling ad. Remove those asterisks from the response.
                            Keep it professional.

                            User Segment:
                            {state.user_segment}

                            Marketing Strategy:
                            {state.strategy}

                            Product Details:
                            {state.product_details}

                            Generate an ad content in a JSON format compatible with this schema:
                            {{
                            "ad_content": "The main ad copy as a single string"
                            }}

                            Make it engaging and tailored to the segment and strategy.
                                        """.strip()

            result: AdOutput = await self.chain.ainvoke({"input": prompt_text})

            state.generated_ad = result.ad_text
            state.ad_generation_ready = True
            logger.info("Ad successfully generated.")

            CampaignReportSaver.save(state, user_id=state.user_id, query=state.query)

        except Exception as e:
            logger.error(f"Ad generation failed: {e}")
            state.generated_ad = "We couldn't generate an ad at the moment."
            state.ad_generation_ready = False
        
        return state







# # import asyncio
# # from pydantic import BaseModel, Field
# # from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
# # from core.chain import ChainAccess, ProviderPromptConfig
# # from core.prompt_templates import AdPromptBuilder
# # from core.ad_generator import AdGenerator, AdInput
# # from logs.logging_config import logger
# # from workflows.state import GraphState
# # from workflows.graphs.campaign.prompts.ad_prompt import (
# #     OPENAI_SYSTEM_PROMPT,
# #     OPENAI_HUMAN_PROMPT,
# #     GROQ_SYSTEM_PROMPT,
# #     GROQ_HUMAN_PROMPT
# # )


# # class GenerateAdNode:
# #     """
# #     Node responsible for generating personalized ad content
# #     using structured LLM output based on a user segment and campaign context.
# #     """
# #     @staticmethod
# #     # def build_prompt(user_segment: str, campaign_recommendation: str) -> str:
# #     #     return (
# #     #         f"You are an expert ad copywriter.\n\n"
# #     #         f"Segment: {user_segment}\n"
# #     #         f"Campaign Strategy:\n{campaign_recommendation}\n\n"
# #     #         f"Write a persuasive and engaging ad copy for the above campaign and segment."
# #     #     )
# #     def build_prompt(user_segment: str, campaign_recommendation: str) -> dict:
# #         return {
# #             "segment": user_segment,
# #             "campaign": campaign_recommendation
# #         }
    
# #     def __init__(self):
# #         """
# #         Initializes the ad generation chain using ChainManager and prompt templates for each provider.
# #         """
# #         # prompt_map = {
# #         #     # "openai": ProviderPromptConfig(system_prompt=OPENAI_SYSTEM_PROMPT, human_prompt=OPENAI_HUMAN_PROMPT),
# #         #     "groq": ProviderPromptConfig(system_prompt=GROQ_SYSTEM_PROMPT, human_prompt=GROQ_HUMAN_PROMPT)
# #         # }

# #         # self.chain = ChainAccess.get_orchestrator().build(
# #         #     prompt_map=prompt_map,
# #         #     response_model=AdGenerator
# #         # )
# #         prompt = ChatPromptTemplate.from_messages([
# #             SystemMessagePromptTemplate.from_template(GROQ_SYSTEM_PROMPT),
# #             HumanMessagePromptTemplate.from_template(GROQ_HUMAN_PROMPT),
# #         ])

# #         self.chain = ChainAccess.get_orchestrator().build(
# #             prompt_map={"default": prompt},
# #             structured_output=AdInput
# #         )["default"]

# #         logger.info("GenerateAdNode initialized successfully with ad generation chain.")

# #     async def process(self, state: GraphState) -> GraphState:
# #         """
# #         Generates an ad based on the user segment and campaign theme.

# #         Args:
# #             state (GraphState): Current graph state containing segment and recommendation

# #         Returns:
# #             GraphState: Updated state with the generated ad
# #         """
# #         try:
# #             user_segment = state.user_segment
# #             campaign_recommendation = state.campaign_recommendation

# #             if not user_segment or not campaign_recommendation:
# #                 logger.warning("Missing user segment or campaign recommendation; falling back to defaults.")
# #                 user_segment = user_segment or "general audience"
# #                 campaign_recommendation = campaign_recommendation or "standard offer"
            
# #             # prompt_input = AdPromptBuilder.build_prompt(
# #             prompt_input = self.build_prompt(
# #                 user_segment,
# #                 campaign_recommendation
# #             )

# #             ad_result: AdGenerator = await self.chain.ainvoke(prompt_input)

# #             state.generated_ad = ad_result.ad_text
# #             state.ad_generation_ready = True

# #             logger.info("Ad successfully generated.")

# #         except Exception as e:
# #             logger.error(f"Ad generation failed: {e}")
# #             state.generated_ad = "We're sorry, we're unable to generate an ad at the moment."
# #             state.ad_generation_ready = False

# #         return state


# # # Manual test entrypoint
# # if __name__ == "__main__":

# #     async def test():
# #         from workflows.state import GraphState

# #         sample_state = GraphState(
# #             user_segment="budget-conscious millennial",
# #             campaign_recommendation="20% off on sustainable products",
# #             conversation_history=[],
# #             query=""
# #         )

# #         generator = GenerateAdNode()
# #         updated_state = await generator.process(sample_state)
# #         print(f"Generated Ad: {updated_state.generated_ad}")

# #     asyncio.run(test())





