# workflows/graphs/campaign/nodes/human_review_node.py

from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel, Field
from typing import Optional

from logs.logging_config import logger
from workflows.state import GraphState
from core.utils.review_scorer import simple_human_review_score


class HumanReviewDecision(BaseModel):
    """
    Structured output model for determining if human review is needed.

    Attributes:
        require_review (bool): Whether the campaign/ad should be routed to a human.
    """
    require_review: bool = Field(..., description="True if human validation is needed")


class HumanReviewRouter:
    def __init__(self):
        self.feedback_event = asyncio.Event()
        self._feedback = None
        self._decision = None

    def receive_feedback(self, feedback: str, revision: bool):
        self._feedback = feedback
        self._decision = revision
        self.feedback_event.set()

    async def wait_for_feedback(self, prompt: str):
        with open("human_prompt.txt", "w") as f:
            f.write(prompt)

        self.feedback_event.clear()
        await self.feedback_event.wait()
        return self._feedback, self._decision

    async def process(self, state: GraphState) -> GraphState:
        try:
            ad_texts = state.ad_variants or [state.generated_ad]
            ad_texts = [ad for ad in ad_texts if ad]

            if not ad_texts:
                logger.warning("No ads found for review. Skipping human review step.")
                return state

            reviewed_ads = []
            for ad in ad_texts:
                logger.info(f"Reviewing ad variant: {ad}")
                score = simple_human_review_score(ad)
                reviewed_ads.append({"ad": ad, "score": score})

            state.reviewed_ads = reviewed_ads
            state.requires_human_review = True

            # Pausing and waiting for human feedback via UI
            logger.info("Waiting for human feedback via web UI...")
            feedback, revision = await self.wait_for_feedback(ad_texts[0])

            state.ad_feedback = feedback
            state.requires_revision = revision
            logger.info(f"Feedback received: {feedback}, revision: {revision}")

        except Exception as e:
            logger.error(f"HumanReviewNode failed: {e}")

        return state


# class HumanReviewRouter:
#     """
#     Node responsible for performing human scoring and optionally collecting human feedback.
#     """

#     def __init__(self):
#         """
#         Initializes inline scoring and logs readiness.
#         """
#         self.chain = RunnableLambda(lambda x: x["input"])  # Placeholder logic
#         logger.info("HumanReviewRouter initialized successfully with fallback chain.")

#     async def process(self, state: GraphState) -> GraphState:
#         """
#         Scores ad variants and flags them for human review.
#         Optionally captures feedback via user input.

#         Args:
#             state (GraphState): Current workflow state.

#         Returns:
#             GraphState: Updated with reviewed ads and feedback.
#         """
#         try:
#             # Use ad_variants if present, fallback to single generated_ad
#             ad_texts = state.ad_variants or [state.generated_ad]
#             ad_texts = [ad for ad in ad_texts if ad]
#             if not ad_texts:
#                 logger.warning("No ads found for review. Skipping human review step.")
#                 return state  # or raise a custom exception / handle accordingly

#             reviewed_ads = []
#             for ad in ad_texts:
#                 logger.info(f"Reviewing ad variant: {ad}")
#                 score = simple_human_review_score(ad)
#                 reviewed_ads.append({"ad": ad, "score": score})

#             state.reviewed_ads = reviewed_ads  # <-- #️⃣ Captures scores
#             state.requires_human_review = True  # <-- #️⃣ Forces human routing
#             logger.info("Human Review Forced....")

#             # Ad feedback
#             try:
#                 user_feedback = input("Please provide your feedback on the ad (or press Enter to approve as-is): ").strip()
#             except EOFError:
#                 user_feedback = ""

#             if user_feedback:
#                 state.ad_feedback = user_feedback
#                 logger.info(f"Captured human feedback: {user_feedback}")

#                 try:
#                     decision = input("Wanna to proceed with your feedback for revision? (y/n): ").strip().lower()
#                 except EOFError:
#                     decision = "y"

#                 if decision == "y":
#                     state.requires_revision = True
#                     logger.info("Marked for revision based on feedback.")
#                 else:
#                     state.requires_revision = False
#                     logger.info("Feedback captured but ad approved as-is.")
#             else:
#                 logger.info("No feedback provided. Proceeding without revision.")
#                 state.requires_revision = False

#         except Exception as e:
#             logger.error(f"HumanReviewNode failed: {e}")

#         return state


# Manual test runner
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
        print("Reviewed Ads:", updated_state.reviewed_ads)
        print("Feedback:", updated_state.ad_feedback)

    asyncio.run(test())





#---------------------------------------------------------------------------------------------------------------------------------

# from langchain_core.runnables import RunnableLambda
# from workflows.state import GraphState
# from pydantic import BaseModel, Field
# from core.utils.review_scorer import simple_human_review_score
# from logs.logging_config import logger

# class HumanReviewDecision(BaseModel):
#     """
#     Structured output model for determining if human review is needed.

#     Attributes:
#         require_review (bool): Whether the campaign/ad should be routed to a human.
#     """
#     require_review: bool = Field(..., description="True if human validation is needed")

# class HumanReviewRouter:
#     """
#     Collects human feedback for ad variants and scores them.
#     """

#     def __init__(self):
#         self.chain: RunnableLambda = RunnableLambda(lambda x: x["input"])
#         logger.info("HumanReviewNode initialized.")

#     async def process(self, state: GraphState) -> GraphState:
#         try:
#             # <<< CHANGED >>> use variants if available, else fallback to original
#             ad_texts = state.ad_variants or [state.generated_ad]  # <<< CHANGED >>>

#             reviewed_ads = []
#             for ad in ad_texts:
#                 logger.info(f"Reviewing ad variant: {ad}")

#                 # <<< CHANGED >>> simulate or perform human review
#                 review_score = simple_human_review_score(ad)  # <<< CHANGED >>>
#                 reviewed_ads.append({"ad": ad, "score": review_score})

#             state.reviewed_ads = reviewed_ads  # <<< CHANGED >>>
#             # state.human_review_required = any(ad["score"] < 0.6 for ad in reviewed_ads)
#             state.requires_human_review = True
#             logger.info("Human review completed for ad variants.")

#         except Exception as e:
#             logger.error(f"HumanReviewNode failed: {str(e)}")

#         return state



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
#                 {{ "require_review": true }} or {{ "require_review": false }}

#                 Do NOT return quotes around true or false. Return native JSON boolean values only.
#                 """)  # <-- hashtag: Updated inline prompt with strict boolean format instruction
#             },
#             structured_output=HumanReviewDecision
#         )["default"]  # <-- hashtag: Extracted the default runnable from orchestrator response

#         logger.info("HumanReviewRouter initialized successfully with inline prompt.")  # <-- hashtag: Added success log


#     async def process(self, state: GraphState) -> GraphState:
#         """
#         Decides whether the ad/campaign output needs human validation.

#         Args:
#             state (GraphState): Current state containing generated ad or campaign.

#         Returns:
#             GraphState: Updated with human_review_required flag.
#         """
#         # input_content = state.generated_ad or state.generated_campaign
#         # if not input_content:
#         #     logger.warning("No content available for human review decision. Skipping.")
#         #     state.human_review_required = True
#         #     return state

#         # try:
#         #     response: HumanReviewDecision = await self.chain.ainvoke({"content": input_content})
#         #     state.human_review_required = response.require_review
#         #     logger.info(f"Human review required: {response.require_review}")
#         # except Exception as e:
#         #     logger.error(f"Human review decision failed: {e}")  # <-- hashtag: Captures tool_use_failed errors
#         #     state.human_review_required = True

#         # return state
#         # async def process(self, state: GraphState) -> GraphState:

#         """
#         Force human review for the generated ad.
#         """
#         ad_text = state.generated_ad or ""
#         if not ad_text:
#             logger.warning("No ad text found. Forcing human review.")
#             state.requires_human_review = True
#             return state

#         # Force human review regardless of LLM output
#         state.requires_human_review = True
#         logger.info("Human review forced: True")

#         try:
#             user_feedback = input("📝 Please provide your feedback on the ad (or press Enter to skip): ").strip()
#         except EOFError:
#             user_feedback = ""

#         if user_feedback:
#             state.ad_feedback = user_feedback
#             logger.info(f"Captured human feedback: {user_feedback}")
#         else:
#             logger.warning("No feedback provided for the ad.")

#         return state


# # Manual test runner  # <-- hashtag: Added __main__ test block
# if __name__ == "__main__":
#     import asyncio

#     async def test():
#         from workflows.state import GraphState

#         test_state = GraphState(
#             generated_ad="Limited time offer! Buy one, get one free on all prescription meds!"
#         )

#         node = HumanReviewRouter()
#         updated_state = await node.process(test_state)

#         print("Human Review Required:", updated_state.requires_human_review)

#     asyncio.run(test())

























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












