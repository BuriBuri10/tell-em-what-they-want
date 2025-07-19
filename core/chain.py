from threading import Lock
from typing import Optional, Dict

from langchain.chains.base import Chain
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from core.llm_manager import LLMManager
from logs.logging_config import logger
from pydantic import BaseModel


class ProviderPromptConfig(BaseModel):
    """
    Configuration model for LLM prompt structure per provider.
    """
    system_prompt: str
    human_prompt: str

# class ProviderPromptConfig:
#     """
#     Defines a structured container for system and human prompts per provider.
#     """

#     def __init__(self, system_prompt: str, human_prompt: str):
#         self.system_prompt = system_prompt
#         self.human_prompt = human_prompt


class ChainOrchestrator:
    """
    Orchestrates the construction of provider-aware LLM chains with optional fallbacks.
    """

    # def build(
    #     self,
    #     prompt_map: Dict[str, ProviderPromptConfig],
    #     temperature: float = 0.0,
    #     model_options: Optional[Dict[str, any]] = None,
    #     response_model: Optional[BaseModel] = None,
    # ) -> Chain:
    #     """
    #     Constructs an LLM chain with fallback support across providers.

    #     Args:
    #         prompt_map: Ordered map of provider identifiers to their prompts.
    #         temperature: LLM temperature for randomness control.
    #         model_options: Additional parameters for the LLM engine.
    #         response_model: Optional Pydantic model to enforce output structure.

    #     Returns:
    #         Chain: A composed LLM chain with fallback logic.
    #     """
    #     providers = list(prompt_map.keys())
    #     head = providers[0]
    #     tail = providers[1:]

    #     base_chain = self._build_single_chain(
    #         provider=head,
    #         prompt_config=prompt_map[head],
    #         temperature=temperature,
    #         model_options=model_options,
    #         response_model=response_model
    #     )

    #     if not tail:
    #         return base_chain

    #     alternatives = []
    #     for backup in tail:
    #         try:
    #             fallback_chain = self._build_single_chain(
    #                 provider=backup,
    #                 prompt_config=prompt_map[backup],
    #                 temperature=temperature,
    #                 model_options=model_options,
    #                 response_model=response_model
    #             )
    #             alternatives.append(fallback_chain)
    #             logger.debug(f"{backup} registered as fallback.")
    #         except Exception as error:
    #             logger.warning(f"Could not add {backup} to fallback: {error}")

    #     return base_chain.with_fallbacks(alternatives)
    
    def build(
        self,
        prompt_map: Dict[str, ChatPromptTemplate],
        temperature: float = 0.3,
        provider: str = "groq",
        model_overrides: Optional[Dict[str, any]] = None,
        structured_output: Optional[any] = None
        ) -> any:
        """
        Builds a provider-aware chain by combining prompts and language models.
        """
        chains = {}

        for name, prompt in prompt_map.items():
            llm = LLMManager.get_llm(
                provider=provider,
                temperature=temperature,
                model_overrides=model_overrides,
                structured_output=structured_output  # ✅ Pass here
            )
            chains[name] = prompt | llm  # ✅ Use LangChain syntax
            logger.info(f"Built chain for: {name} using provider: {provider}")

        return chains


    def _build_single_chain(
        self,
        provider: str,
        prompt_config: ProviderPromptConfig,
        temperature: float,
        model_options: Optional[Dict[str, any]],
        response_model: Optional[BaseModel],
    ) -> Chain:
        template = ChatPromptTemplate.from_messages([
            ("system", prompt_config.system_prompt),
            ("human", prompt_config.human_prompt)
        ])

        llm_instance = LLMManager.get_llm(
            provider=provider,
            temperature=temperature,
            model_overrides=model_options,
            structured_output=response_model,
        )

        return template | llm_instance


class ChainAccess:
    """
    Singleton access point for building LLM chains.
    """

    _singleton = None
    _orchestrator = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._singleton is None:
                cls._singleton = super().__new__(cls)
                cls._singleton._orchestrator = ChainOrchestrator()
        return cls._singleton

    @classmethod
    def get_orchestrator(cls) -> ChainOrchestrator:
        return cls()._orchestrator
