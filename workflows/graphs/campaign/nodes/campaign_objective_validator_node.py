# from langchain_core.runnables import RunnableLambda
# from core.chain import ChainAccess
# from workflows.state import GraphState
# from logs.logging_config import logger


# class CampaignObjectiveValidatorNode:
#     """
#     Validates whether the campaign objective is clear and well-aligned with the user persona.
#     Routes to refinement if vague or mismatched.
#     """

#     def __init__(self):
#         """
#         Initializes the objective validation chain.
#         Prompt is constructed inline dynamically during execution.
#         """
#         self.chain: RunnableLambda = ChainAccess.get_orchestrator().build(
#             prompt_map={"default": RunnableLambda(lambda x: x["input"])},
#             structured_output=None
#         )["default"]

#         logger.info("CampaignObjectiveValidatorNode initialized.")

#     async def process(self, state: GraphState) -> GraphState:
#         """
#         Checks if the campaign objective is aligned with the user persona.

#         Args:
#             state (GraphState): Graph state with user_persona and campaign_objective.

#         Returns:
#             GraphState: Updated state with validation flag set.
#         """
#         try:
#             if not state.user_persona or not state.campaign_objective:
#                 raise ValueError("Missing user_persona or campaign_objective.")

#             prompt_text = f"""
#             Review the following campaign objective and determine if it aligns clearly with the user persona.

#             Persona Description:
#             {state.user_persona.get("description", "N/A")}

#             Campaign Objective:
#             {state.campaign_objective}

#             Answer with one word only: "Valid" if appropriate and actionable, or "Invalid" if vague or misaligned.
#             """.strip()

#             result = await self.chain.ainvoke({"input": prompt_text})
#             verdict = result.content.strip().lower()

#             if verdict == "valid":
#                 state.objective_is_valid = True
#             else:
#                 state.objective_is_valid = False

#             logger.info(f"Objective validation result: {verdict}")

#         except Exception as e:
#             logger.error(f"Failed to validate campaign objective: {str(e)}")
#             state.objective_is_valid = False

#         return state


# # Manual test runner
# if __name__ == "__main__":
#     import asyncio

#     async def test():
#         test_state = GraphState(
#             user_persona={
#                 "description": "Young tech enthusiasts who are early adopters of wearable technology.",
#                 "age_range": "20-30",
#                 "interests": "gadgets, fitness, mobile apps"
#             },
#             campaign_objective="Launch a loyalty campaign."
#         )

#         validator = CampaignObjectiveValidatorNode()
#         updated_state = await validator.process(test_state)

#         print(f"Objective is valid: {updated_state.objective_is_valid}")

#     asyncio.run(test())


from langchain_core.runnables import RunnableLambda
from core.chain import ChainAccess
from workflows.state import GraphState
from logs.logging_config import logger


class CampaignObjectiveValidatorNode:
    """
    Validates whether the campaign objective is clear and well-aligned with the user persona.
    Routes to refinement if vague or misaligned.
    """

    def __init__(self):
        """
        Initializes the objective validation chain using a placeholder prompt,
        as dynamic prompt text is composed in the processing step.
        """
        self.chain: RunnableLambda = ChainAccess.get_orchestrator().build(
            prompt_map={"default": RunnableLambda(lambda x: x["input"])},
            structured_output=None
        )["default"]

        logger.info("CampaignObjectiveValidatorNode initialized.")

    async def process(self, state: GraphState) -> GraphState:
        """
        Executes validation logic to assess if campaign objective is aligned with persona.

        Args:
            state (GraphState): Contains user_persona and campaign_objective.

        Returns:
            GraphState: Updated with objective_is_valid flag (True/False).
        """
        # NOTE: introduce this dummy while introducing subgraphs
        state.user_persona = {"description": "Young professional interested in tech and fitness"}
        state.campaign_objective = "Promote the new AI-powered smartwatch to Gen Z users"

        try:
            if not state.user_persona or not state.campaign_objective:
                raise ValueError("Missing user_persona or campaign_objective.")

            prompt_text = f"""
            Review the following campaign objective and determine if it aligns clearly with the user persona.

            Persona Description:
            {state.user_persona.get("description", "N/A")}

            Campaign Objective:
            {state.campaign_objective}

            Answer with one word only: "Valid" if appropriate and actionable, or "Invalid" if vague or misaligned.
            """.strip()

            result = await self.chain.ainvoke({"input": prompt_text})
            verdict = result.content.strip().lower()

            state.objective_is_valid = verdict == "valid"
            logger.info(f"Objective validation result: {verdict}")

        except Exception as e:
            logger.error(f"Objective validation failed: {str(e)}")
            state.objective_is_valid = False

        return state


# Manual test runner
if __name__ == "__main__":
    import asyncio

    async def test():
        test_state = GraphState(
            user_persona={
                "description": "Young tech enthusiasts who are early adopters of wearable technology.",
                "age_range": "20-30",
                "interests": "gadgets, fitness, mobile apps"
            },
            campaign_objective="Launch a loyalty campaign."
        )

        validator = CampaignObjectiveValidatorNode()
        updated_state = await validator.process(test_state)
        print(f"Objective is valid: {updated_state.objective_is_valid}")

    asyncio.run(test())
