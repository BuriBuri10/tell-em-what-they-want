# # workflows/graphs/campaign/nodes/human_review_node.py

# from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
# from pydantic import BaseModel, Field
# from core.chain import ChainAccess
# from core.chain import ProviderPromptConfig
# from logs.logging_config import logger
# from workflows.state import GraphState
# from workflows.graphs.campaign.prompts.human_in_the_loop_prompt import (
#     OPENAI_SYSTEM_PROMPT,
#     OPENAI_HUMAN_PROMPT,
#     GROQ_SYSTEM_PROMPT,
#     GROQ_HUMAN_PROMPT,
# )


# class HumanReviewDecision(BaseModel):
#     """
#     Structured output model for determining if human review is needed.

#     Attributes:
#         require_review (bool): Whether the campaign/ad should be routed to a human.
#     """
#     require_review: bool = Field(..., description="True if human validation is needed")


# class HumanReviewRouter:
#     """
#     Node responsible for determining whether generated output should be routed to a human reviewer.
#     """

#     def __init__(self):
#         """
#         Initializes a chain to evaluate content review needs based on provider-specific prompts.
#         """
#         chain_builder = ChainAccess.get_orchestrator()
#         prompt_map = {
#             # "openai": ProviderPromptConfig(system_prompt=OPENAI_SYSTEM_PROMPT, human_prompt=OPENAI_HUMAN_PROMPT),
#             "groq": ProviderPromptConfig(system_prompt=GROQ_SYSTEM_PROMPT, human_prompt=GROQ_HUMAN_PROMPT)
#         }
#         self.chain = chain_builder.build(
#             prompt_map=prompt_map,
#             response_model=HumanReviewDecision
#         )
#         # prompt = ChatPromptTemplate.from_messages([
#         #     SystemMessagePromptTemplate.from_template(GROQ_SYSTEM_PROMPT),
#         #     HumanMessagePromptTemplate.from_template(GROQ_HUMAN_PROMPT),
#         # ])

#         self.chain = ChainAccess.get_orchestrator().build(
#             prompt_map={"default": prompt},
#             structured_output=HumanReviewDecision)["default"]

#         logger.info("HumanReviewRouter initialized successfully")

#     async def process(self, state: GraphState) -> GraphState:
#         """
#         Decides whether the ad/campaign output needs human validation.

#         Args:
#             state (GraphState): Current state containing generated ad or campaign.

#         Returns:
#             GraphState: Updated with human_review_required flag.
#         """
#         input_content = state.generated_ad or state.generated_campaign
#         if not input_content:
#             logger.warning("No content available for human review decision. Skipping.")
#             state.human_review_required = False
#             return state

#         try:
#             response: HumanReviewDecision = await self.chain.ainvoke({"content": input_content})
#             state.human_review_required = response.require_review
#             logger.info(f"Human review required: {response.require_review}")

#         except Exception as e:
#             logger.error(f"Human review decision failed: {e}")
#             state.human_review_required = False

#         return state


# if __name__ == "__main__":
#     import asyncio
#     from workflows.state import GraphState

#     async def test_human_review():
#         # Example content to test
#         sample_state = GraphState(generated_ad="Buy 2 get 1 free on all electronics this week only!")
        
#         node = HumanReviewRouter()
#         updated_state = await node.process(sample_state)
        
#         print("Human Review Required:", updated_state.human_review_required)

#     asyncio.run(test_human_review())




# # workflows/graphs/campaign/nodes/human_review_node.py

# from langchain_core.runnables import RunnableLambda
# from pydantic import BaseModel, Field
# from core.chain import ChainAccess
# from logs.logging_config import logger
# from workflows.state import GraphState


# class HumanReviewDecision(BaseModel):
#     """
#     Structured output model for determining if human review is needed.

#     Attributes:
#         require_review (bool): Whether the campaign/ad should be routed to a human.
#     """
#     require_review: bool = Field(..., description="True if human validation is needed")


# class HumanReviewRouter:
#     """
#     Node responsible for determining whether generated output should be routed to a human reviewer.
#     """

#     def __init__(self):
#         """
#         Initializes a review decision chain with prompt defined inline.
#         """
#         self.chain = ChainAccess.get_orchestrator().build(
#             prompt_map={
#                 "default": RunnableLambda(lambda x: f"""
#                 You are an advertising compliance assistant.

#                 Given the following content, decide whether a human review is necessary based on potential risks like misleading claims, sensitive topics, or inappropriate language.

#                 Content:
#                 {x['content']}

#                 Respond in the following JSON format:
#                 {{"require_review": true}} or {{"require_review": false}}
#                 """)
#             },
#             structured_output=HumanReviewDecision
#             )["default"]  # <-- hashtag: replaced hardcoded prompt injection

#         logger.info("HumanReviewRouter initialized successfully with inline prompt.")  # <-- hashtag: added log

#     async def process(self, state: GraphState) -> GraphState:
#         """
#         Decides whether the ad/campaign output needs human validation.

#         Args:
#             state (GraphState): Current state containing generated ad or campaign.

#         Returns:
#             GraphState: Updated with human_review_required flag.
#         """
#         input_content = state.generated_ad or state.generated_campaign
#         if not input_content:
#             logger.warning("No content available for human review decision. Skipping.")
#             state.human_review_required = False
#             return state

#         try:
#             response: HumanReviewDecision = await self.chain.ainvoke({"content": input_content})
#             state.human_review_required = response.require_review
#             logger.info(f"Human review required: {response.require_review}")
#         except Exception as e:
#             logger.error(f"Human review decision failed: {e}")
#             state.human_review_required = False

#         return state


# # Manual test runner  # <-- hashtag: added test block
# if __name__ == "__main__":
#     import asyncio

#     async def test():
#         from workflows.state import GraphState

#         test_state = GraphState(
#             generated_ad="Limited time offer! Buy one, get one free on all prescription meds!"
#         )

#         node = HumanReviewRouter()
#         updated_state = await node.process(test_state)

#         print("Human Review Required:", updated_state.human_review_required)

#     asyncio.run(test())



# workflows/graphs/campaign/nodes/human_review_node.py

from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel, Field
from core.chain import ChainAccess
from logs.logging_config import logger
from workflows.state import GraphState


class HumanReviewDecision(BaseModel):
    """
    Structured output model for determining if human review is needed.

    Attributes:
        require_review (bool): Whether the campaign/ad should be routed to a human.
    """
    require_review: bool = Field(..., description="True if human validation is needed")


class HumanReviewRouter:
    """
    Node responsible for determining whether generated output should be routed to a human reviewer.
    """

    def __init__(self):
        """
        Initializes a review decision chain with prompt defined inline.
        """
        self.chain = ChainAccess.get_orchestrator().build(
            prompt_map={
                "default": RunnableLambda(lambda x: f"""
                You are an advertising compliance assistant.

                Given the following content, decide whether a human review is necessary based on potential risks like misleading claims, sensitive topics, or inappropriate language.

                Content:
                {x['content']}

                Respond in the following JSON format:
                {{ "require_review": true }} or {{ "require_review": false }}

                Do NOT return quotes around true or false. Return native JSON boolean values only.
                """)  # <-- hashtag: Updated inline prompt with strict boolean format instruction
            },
            structured_output=HumanReviewDecision
        )["default"]  # <-- hashtag: Extracted the default runnable from orchestrator response

        logger.info("HumanReviewRouter initialized successfully with inline prompt.")  # <-- hashtag: Added success log


    async def process(self, state: GraphState) -> GraphState:
        """
        Decides whether the ad/campaign output needs human validation.

        Args:
            state (GraphState): Current state containing generated ad or campaign.

        Returns:
            GraphState: Updated with human_review_required flag.
        """
        # input_content = state.generated_ad or state.generated_campaign
        # if not input_content:
        #     logger.warning("No content available for human review decision. Skipping.")
        #     state.human_review_required = True
        #     return state

        # try:
        #     response: HumanReviewDecision = await self.chain.ainvoke({"content": input_content})
        #     state.human_review_required = response.require_review
        #     logger.info(f"Human review required: {response.require_review}")
        # except Exception as e:
        #     logger.error(f"Human review decision failed: {e}")  # <-- hashtag: Captures tool_use_failed errors
        #     state.human_review_required = True

        # return state
        # async def process(self, state: GraphState) -> GraphState:

        """
        Force human review for the generated ad.
        """
        ad_text = state.generated_ad or ""
        if not ad_text:
            logger.warning("No ad text found. Forcing human review.")
            state.requires_human_review = True
            return state

        # Force human review regardless of LLM output
        state.requires_human_review = True
        logger.info("Human review forced: True")

        try:
            user_feedback = input("📝 Please provide your feedback on the ad (or press Enter to skip): ").strip()
        except EOFError:
            user_feedback = ""

        if user_feedback:
            state.ad_feedback = user_feedback
            logger.info(f"Captured human feedback: {user_feedback}")
        else:
            logger.warning("No feedback provided for the ad.")

        return state


# Manual test runner  # <-- hashtag: Added __main__ test block
if __name__ == "__main__":
    import asyncio

    async def test():
        from workflows.state import GraphState

        test_state = GraphState(
            generated_ad="Limited time offer! Buy one, get one free on all prescription meds!"
        )

        node = HumanReviewRouter()
        updated_state = await node.process(test_state)

        print("Human Review Required:", updated_state.requires_human_review)

    asyncio.run(test())
