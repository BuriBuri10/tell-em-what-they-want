import os
from pathlib import Path
from typing import Any, Dict, Optional
# from workflows.graphs.campaign.prompts.recommendation_prompt import OPENAI_HUMAN_PROMPT
from logs.logging_config import logger


class AdPromptBuilder:
    """
    Loads and renders prompt templates from Python modules
    specifically for ad generation use cases.
    """

    def __init__(self, base_dir: str = "workflows/graphs"):
        self.base_dir = Path(base_dir)

    def render_prompt(
        self,
        campaign_type: str,
        prompt_file: str,
        variables: Dict[str, Any]
    ) -> str:
        """
        Renders a given prompt template by loading the Python module and formatting it.

        Args:
            campaign_type (str): The type or name of the campaign graph folder.
            prompt_file (str): The name of the prompt file (Python file without `.py`).
            variables (Dict[str, Any]): A dictionary of variables to pass to the template.

        Returns:
            str: The rendered prompt string.
        """
        try:
            module_path = f"workflows.graphs.{campaign_type}.prompts.{prompt_file.replace('.py', '')}"
            prompt_module = __import__(module_path, fromlist=[""])

            system_prompt = getattr(prompt_module, "OPENAI_SYSTEM_PROMPT", "")
            human_prompt = getattr(prompt_module, "OPENAI_HUMAN_PROMPT", "").format(**variables)

            logger.info(f"Loaded prompt module: {prompt_file} for campaign: {campaign_type}")
            return f"{system_prompt.strip()}\n\n{human_prompt.strip()}"
        except Exception as e:
            logger.error(f"Failed to load or render prompt '{prompt_file}': {e}")
            raise e


class RecommendationPromptBuilder:
    """
    Loads and renders prompt templates from Python modules
    specifically for marketing strategy recommendation use cases.
    """

    def __init__(self, base_dir: str = "workflows/graphs"):
        self.base_dir = Path(base_dir)

    # class RecommendationPromptBuilder:
    # @staticmethod
    # def render_prompt(segment: Optional[str] = None, user_profile: Optional[str] = None) -> str:
    #     return f"Generate a marketing strategy for a user in the '{segment}' segment.\n\nUser profile:\n{user_profile}"
    
    class RecommendationPromptBuilder:
        """
        Loads and renders prompt templates from Python modules
        specifically for marketing strategy recommendation use cases.
        """

    def __init__(self, base_dir: str = "workflows/graphs"):
        self.base_dir = Path(base_dir)

    # def render_prompt(
    #     self,
    #     campaign_type: str,
    #     prompt_file: str,
    #     variables: Dict[str, Any]
    # ) -> str:
    #     """
    #     Renders a given prompt template by loading the Python module and formatting it.

    #     Args:
    #         campaign_type (str): The type or name of the campaign graph folder.
    #         prompt_file (str): The name of the prompt file (Python file without `.py`).
    #         variables (Dict[str, Any]): A dictionary of variables to pass to the template.

    #     Returns:
    #         str: The rendered prompt string.
    #     """
    #     try:
    #         module_path = f"workflows.graphs.{campaign_type}.prompts.{prompt_file.replace('.py', '')}"
    #         prompt_module = __import__(module_path, fromlist=[""])

    #         system_prompt = getattr(prompt_module, "OPENAI_SYSTEM_PROMPT", "")
    #         human_prompt = getattr(prompt_module, "OPENAI_HUMAN_PROMPT", "").format(**variables)

    #         logger.info(f"Loaded prompt module: {prompt_file} for campaign: {campaign_type}")
    #         return f"{system_prompt.strip()}\n\n{human_prompt.strip()}"
    #     except Exception as e:
    #         logger.error(f"Failed to load or render prompt '{prompt_file}': {e}")
    #         raise e

    @staticmethod
    def render_prompt(user_profile: str, campaign_goal: str) -> str:
        """
        Renders a marketing recommendation prompt using the static template.

        Args:
            user_profile (str): The user persona description.
            campaign_goal (str): The marketing campaign's objective.

        Returns:
            str: The fully rendered prompt string.
        """
        return OPENAI_HUMAN_PROMPT.format(
            user_persona=user_profile,
            campaign_objective=campaign_goal
        )

    @staticmethod
    def render_simple_prompt(segment: Optional[str] = None, user_profile: Optional[str] = None) -> str:
        return f"Generate a marketing strategy for a user in the '{segment}' segment.\n\nUser profile:\n{user_profile}"

