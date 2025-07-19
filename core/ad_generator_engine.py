"""
AdGenerator module responsible for generating personalized ad copy
based on user segment, strategy, and product details using LLMs.
"""

from typing import Dict, Any
from dataclasses import dataclass

from core.chain import ChainAccess, ProviderPromptConfig
from core.llm_manager import LLMManager
from models.ad_model import AdCreative
from logs.logging_config import logger

from pydantic import BaseModel


@dataclass
class AdInput:
    """
    Input schema for generating an ad.
    """
    user_segment: str
    strategy: str
    product_details: str

class AdOutput(BaseModel):
    ad_text: str

class AdGenerator:
    """
    Uses LLMs to generate persuasive, personalized ad copy based on campaign strategy.
    """

    def __init__(self):
        self.chain_orchestrator = ChainAccess.get_orchestrator()

        # Provider-specific prompt configurations
        self.prompt_map = {
            "openai": ProviderPromptConfig(
                system_prompt="You are an expert ad copywriter for digital marketing.",
                human_prompt=(
                    "Generate a compelling ad based on the following inputs:\n"
                    "- User segment: {user_segment}\n"
                    "- Marketing strategy: {strategy}\n"
                    "- Product details: {product_details}\n\n"
                    "Make the tone engaging and aligned with digital marketing best practices."
                )
            ),
            "anthropic": ProviderPromptConfig(
                system_prompt="You are a world-class creative marketer writing digital ads.",
                human_prompt=(
                    "Please craft an engaging advertisement using the data below:\n"
                    "Segment: {user_segment}\n"
                    "Strategy: {strategy}\n"
                    "Product: {product_details}\n\n"
                    "The ad should resonate with the target group and drive conversions."
                )
            ),
            "groq": ProviderPromptConfig(
                system_prompt="You specialize in high-performance persuasive marketing copy.",
                human_prompt=(
                    "generate an ad that is short, punchy, and highly engaging.\n\n"
                    "Respond ONLY with a valid JSON object exactly like this:\n"
                    "{\"ad_text\": \"Your generated ad here\"}\n"
                    "Do NOT include any extra text or explanation outside the JSON."
                    )
                ),
            "gemini": ProviderPromptConfig(
                system_prompt="You are a creative AI trained to generate marketing ads.",
                human_prompt=(
                    "Generate a highly engaging marketing ad using the following context:\n"
                    "- Segment: {user_segment}\n"
                    "- Strategy: {strategy}\n"
                    "- Product: {product_details}"
                    "Respond with a JSON object like this:\n"
                    "{\n  \"ad_text\": \"Your generated ad here\"\n}"
                )
            )
        }

    def generate(self, ad_input: AdInput, provider: str = "groq") -> AdCreative:
        """
        Generates ad copy for a given campaign configuration using the specified provider.

        Args:
            ad_input (AdInput): Structured input with segment, strategy, and product details.
            provider (str): LLM provider name.

        Returns:
            AdOutput: Generated ad with headline and body text.
        """
        if provider not in self.prompt_map:
            raise ValueError(f"Unsupported provider for ad generation: {provider}")

        logger.info(f"Generating ad using provider '{provider}' for segment: {ad_input.user_segment}")

        chain = self.chain_orchestrator.build(
            prompt_map={provider: self.prompt_map[provider]},
            temperature=0.7,
            response_model=AdOutput
        )

        chain_input: Dict[str, Any] = {
            "user_segment": ad_input.user_segment,
            "strategy": ad_input.strategy,
            "product_details": ad_input.product_details
        }

        try:
            output = chain.invoke(chain_input)
            return output
        except Exception as e:
            logger.error(f"Ad generation failed: {e}")
            raise
