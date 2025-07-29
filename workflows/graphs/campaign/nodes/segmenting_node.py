import asyncio
from pydantic import BaseModel, Field
from typing import Literal

from core.chain import ChainAccess
from workflows.state import GraphState
from logs.logging_config import logger


class SegmentOutput(BaseModel):
    """
    Structured output schema for customer segmentation.
    """
    segment: Literal["budget", "standard", "premium"] = Field(
        ..., description="Predicted user segment: budget | standard | premium"
    )


class UserSegmenter:
    """
    Node responsible for classifying users into segments using an LLM chain.
    """

    def __init__(self):
        """
        Initializes the user segmentation chain.
        """
        self.chain = ChainAccess.get_orchestrator().build(
            prompt_map={
                "default": self._build_prompt
            },
            structured_output=SegmentOutput,
        )["default"]

        logger.info("UserSegmenter initialized with structured prompt.")

    def _build_prompt(self, inputs: dict) -> str:
        """
        Creates the input prompt dynamically from user query.
        """
        query = inputs.get("input", "")
        return f"""
                You are an expert in customer segmentation.

                Classify the user based on the following query into one of three segments:
                - "budget"
                - "standard"
                - "premium"

                ONLY respond in 'valid JSON' exactly like this (STRICTLY without any explanation):

                {{
                "segment": "budget"
                }}

                User Query: {query}
                """.strip()

    async def process(self, state: GraphState) -> GraphState:
        """
        Runs user segmentation using the LLM.
        """
        query = state.query or state.vdb_query
        if not query:
            logger.warning("No input found for segmentation. Defaulting to 'standard'.")
            state.user_segment = "standard"
            state.campaign_objective = "Promote general-purpose products to average customers"  # >>> temporary objective fallback
            state.segmenter_ready = False
            return state

        try:
            result: SegmentOutput = await self.chain.ainvoke({"input": query})

            if result and result.segment in ["budget", "standard", "premium"]:
                state.user_segment = result.segment
                logger.info(f"Predicted segment: {result.segment}")
            else:
                logger.warning(f"Invalid or missing segment. Defaulting to 'standard'.")
                state.user_segment = "standard"
            
            # >>> TEMP: placeholder campaign objective based on segment
            segment_objectives = {
                "budget": "Promote affordable value-for-money deals",                      # >>>
                "standard": "Promote general-purpose products to average customers",        # >>>
                "premium": "Promote high-end exclusive products for premium buyers",        # >>>
                }  # >>>
            state.campaign_objective = segment_objectives.get(                             # >>>
                state.user_segment, "Promote general-purpose products to average customers" # >>>
                )  # >>>

            state.segmenter_ready = True

        except Exception as e:
            logger.error(f"Segmentation failed: {e}")
            state.user_segment = "standard"
            state.campaign_objective = "Promote general-purpose products to average customers"  # >>> fallback objective
            state.segmenter_ready = False

        return state
    

if __name__ == "__main__":

    async def test():
        # sample_inputs = [
        #     "I'm looking for affordable eco-friendly products",
        #     "I'm interested in premium skincare routines",
        #     "Just browsing for general deals"
        # ]

        sample_input = "suberb quality tech products"

        segmenter = UserSegmenter()
        # for q in sample_inputs:
        state = GraphState(query=sample_input, vdb_query=sample_input, conversation_history=[])
        updated_state = await segmenter.process(state)
        print(f"Input: {sample_input} -> Segment: {updated_state.user_segment}")
        print(f"Campaign Objective -> {updated_state.campaign_objective}")  # >>> added output for campaign objective

    asyncio.run(test())













# import asyncio
# from pydantic import BaseModel, Field
# from typing import Literal

# from core.chain import ChainAccess, ProviderPromptConfig
# from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
# from workflows.state import GraphState
# from workflows.graphs.campaign.prompts.segment_prompt import (
#     GROQ_SYSTEM_PROMPT,
#     GROQ_HUMAN_PROMPT,
# )
# from logs.logging_config import logger


# class SegmentOutput(BaseModel):
#     """
#     Structured output schema for customer segmentation.

#     Attributes:
#         segment (Literal["budget", "standard", "premium"]): Predicted user segment label.
#     """
#     segment: Literal["budget", "standard", "premium"] = Field(
#         ..., description="Predicted user segment: budget | standard | premium"
#     )


# class UserSegmenter:
#     """
#     Node responsible for classifying users into segments using an LLM chain.
#     """
#     def __init__(self):
#         # prompt = ChatPromptTemplate.from_messages([
#         #     ("system", GROQ_SYSTEM_PROMPT),
#         #     ("human", GROQ_HUMAN_PROMPT)
#         # ])

#         prompt = ChatPromptTemplate.from_messages([
#             SystemMessagePromptTemplate.from_template(GROQ_SYSTEM_PROMPT),
#             HumanMessagePromptTemplate.from_template(GROQ_HUMAN_PROMPT),
#         ])

#         self.chain = ChainAccess.get_orchestrator().build(
#             prompt_map={"default": prompt},
#             structured_output=SegmentOutput
#         )["default"]
#     # def __init__(self):
#     #     """
#     #     Initializes the user segmentation chain using system/human prompts per provider.
#     #     """
#     #     chain_builder = ChainAccess.get_orchestrator()

#     #     # prompt_map = {
#     #     #     # "openai": ProviderPromptConfig(system=OPENAI_SYSTEM_PROMPT, human=OPENAI_HUMAN_PROMPT),
#     #     #     "groq": ProviderPromptConfig(system_prompt=GROQ_SYSTEM_PROMPT, human_prompt=GROQ_HUMAN_PROMPT)
#     #     # }

#     #     # self.chain = chain_builder.build(prompt_map=prompt_map, response_model=SegmentOutput)
#     #     self.chain = ChainAccess.get_orchestrator().build(
#     #         prompt_map={
#     #             "default": self.prompts.default_prompt
#     #             },
#     #         structured_output=SegmentOutput)["default"]
#     #     logger.info("UserSegmenter initialized successfully.")

#     async def process(self, state: GraphState) -> GraphState:
#         """
#         Runs user segmentation on the query inside the NodeState.

#         Args:
#             state (NodeState): Current workflow state containing the user query or metadata.

#         Returns:
#             NodeState: Updated state with predicted segment.
#         """
#         query = state.query
#         if not query:
#             logger.warning("No input found for segmentation. Defaulting to 'standard'.")
#             state.segment = "standard"
#             return state

#         try:
#             # result: SegmentOutput = await self.chain.ainvoke({"input": query})
#             result: SegmentOutput = await self.chain.ainvoke({
#                 "user_profile": query,
#                 "segments": ["budget", "standard", "premium"]
# })
#             if isinstance(result.segment, str) and result.segment in ["budget", "standard", "premium"]:
#                 state.segment = result.segment
#                 logger.info(f"Predicted segment: {result.segment}")
#             else:
#                 logger.warning(f"Invalid segment prediction received: {result}")
#                 state.segment = "standard"

#             state.segmenter_ready = True

#         except Exception as e:
#             logger.error(f"Segmentation failed: {e}")
#             state.segment = "standard"
#             state.segmenter_ready = False

#         return state

