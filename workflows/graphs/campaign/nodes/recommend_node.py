# recommend_node.py

from langchain_core.runnables import RunnableLambda
from core.chain import ChainAccess
from workflows.state import GraphState
from logs.logging_config import logger


class RecommendNode:
    """
    Node that generates a personalized marketing strategy recommendation
    based on the user persona and campaign objective.
    """

    def __init__(self):
        """
        Initializes the recommendation generation chain without predefined prompt.
        Prompt is constructed inline at runtime and passed dynamically.
        """
        self.chain: RunnableLambda = ChainAccess.get_orchestrator().build(
            prompt_map={"default": RunnableLambda(lambda x: x["input"])},
            structured_output=None
        )["default"]


        logger.info("RecommendNode initialized with inline prompt chain.")

    async def process(self, state: GraphState) -> GraphState:
        """
        Generates a tailored marketing recommendation based on user persona and campaign goal.

        Args:
            state (GraphState): Current graph state containing user persona and campaign objective.

        Returns:
            GraphState: Updated state with generated campaign recommendation.
        """
        # NOTE: introduce these two while introducing subgraphs
        # state.user_persona = {"description": "Young professional interested in tech and fitness"}
        # state.campaign_objective = "Promote the new AI-powered smartwatch to Gen Z users"

        try:
            user_segment = state.user_segment or "general audience"
            # user_persona = state.user_persona
            # campaign_objective = state.campaign_objective

            if not user_segment:
                raise ValueError("Missing user persona or campaign objective.")

            # Construct prompt inline
            prompt_text = f"""
            Given the following user persona and campaign objective, generate a personalized marketing strategy:

            User Segment:
            {user_segment}

            Instructions:
            - Suggest a marketing strategy that resonates with the user's interests, behavior, and demographic.
            - Recommend ideal content formats (e.g., video, carousel, story).
            - Identify the best-performing social platforms for this audience.
            - Include tone, messaging guidelines, and any relevant CTA suggestions.

            Respond in a structured, concise, and professional tone.
            """.strip()

            result: str = await self.chain.ainvoke({"input": prompt_text})

            state.campaign_recommendation = result.content
            state.strategy = result.content  # Set strategy explicitly
            state.product_details = state.campaign_objective or "our latest offering"
            state.recommendation_ready = True

            logger.info(f"Campaign recommendation generated successfully.")

        except Exception as e:
            logger.error(f"Recommendation generation failed: {str(e)}")
            state.campaign_recommendation = "Use our most popular strategy template for now."
            state.recommendation_ready = False

        return state


# Manual test runner
if __name__ == "__main__":
    import asyncio

    async def test():
        from workflows.state import GraphState

        test_state = GraphState(
            # user_persona="Tech-savvy millennials who value sustainability and use Instagram and YouTube heavily.",
            user_persona={
                            "age_range": "25-34",
                            "interests": "technology, gadgets, fitness",
                            "description": "Tech-savvy millennials who use Instagram and YouTube heavily."
                        },
            campaign_objective="Promote a new eco-friendly gadget for daily productivity."
        )

        recommender = RecommendNode()
        updated_state = await recommender.process(test_state)

        print(f"\nRecommendation:\n{updated_state.campaign_recommendation}")

    asyncio.run(test())



# # recommend_node.py

# import asyncio
# from pydantic import BaseModel, Field

# from core.chain import ChainAccess, ProviderPromptConfig
# from core.prompt_templates import RecommendationPromptBuilder
# from core.recommendation_engine import RecommendationOutputSchema
# from logs.logging_config import logger
# from workflows.state import GraphState
# from workflows.graphs.campaign.prompts.recommendation_prompt import (
#     OPENAI_SYSTEM_PROMPT,
#     OPENAI_HUMAN_PROMPT,
#     GROQ_SYSTEM_PROMPT,
#     GROQ_HUMAN_PROMPT,
# )


# class RecommendNode:
#     """
#     Node responsible for generating a campaign recommendation
#     based on the user's segment or profile.
#     """

#     def __init__(self):
#         """
#         Initializes the recommendation generation chain using ChainManager
#         and structured prompt configurations for each LLM provider.
#         """
#         prompt_map = {
#             # "openai": ProviderPromptConfig(system_prompt=OPENAI_SYSTEM_PROMPT, human_prompt=OPENAI_HUMAN_PROMPT),
#             "groq": ProviderPromptConfig(system_prompt=GROQ_SYSTEM_PROMPT, human_prompt=GROQ_HUMAN_PROMPT)
#         }

#         self.chain = ChainAccess.get_orchestrator().build(
#             prompt_map=prompt_map,
#             response_model=RecommendationOutputSchema
#         )
#         logger.info("RecommendNode initialized successfully with recommendation generation chain.")

#     async def process(self, state: GraphState) -> GraphState:
#         """
#         Generates a tailored campaign recommendation based on user segmentation.

#         Args:
#             state (GraphState): Current state containing user segment information

#         Returns:
#             GraphState: Updated state with campaign recommendation
#         """
#         try:
#             user_segment = state.user_segment or "general audience"

#             prompt_input = RecommendationPromptBuilder.render_prompt(
#                 # # segment=user_segment
#                 # campaign_type="campaign",  # folder name in `workflows/graphs`
#                 # prompt_file="recommendation_prompt",
#                 # variables={
#                 #     "user_persona": state.user_profile,
#                 #     "campaign_objective": state.campaign_goal
#                 # }
#                 user_profile=state.user_profile,
#                 campaign_goal=state.campaign_goal
#             )

#             recommendation: RecommendationOutputSchema = await self.chain.ainvoke(prompt_input)

#             state.campaign_recommendation = recommendation.recommendation_text
#             state.recommendation_ready = True

#             logger.info(f"Generated campaign recommendation: {recommendation.recommendation_text}")

#         except Exception as e:
#             logger.error(f"Recommendation generation failed: {e}")
#             state.campaign_recommendation = "Use our most popular promotion strategy."
#             state.recommendation_ready = False

#         return state


# # Manual test block
# if __name__ == "__main__":

#     async def test():
#         sample_state = GraphState(
#             user_segment="eco-conscious Gen Z",
#             query="",
#             conversation_history=[]
#         )

#         recommender = RecommendNode()
#         updated_state = await recommender.process(sample_state)
#         print(f"Recommendation: {updated_state.campaign_recommendation}")

#     asyncio.run(test())


