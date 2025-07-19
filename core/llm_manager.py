from typing import Any, Optional, Dict
from threading import Lock

from langchain_core.language_models import BaseLanguageModel
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

from configs.app_config import AppConfig
from logs.logging_config import logger


class LLMProviderFactory:
    """
    Factory to create instances of different LLM providers.
    Reads configuration dynamically and applies structured output if required.
    """

    def __init__(self, config: AppConfig):
        self.config = config

    def _init_groq(self, temperature: float, **overrides) -> BaseLanguageModel:
        return ChatGroq(
            model=self.config.GROQ_MODEL_NAME,
            api_key=self.config.get("GROQ_API_KEY"),
            temperature=temperature,
            **overrides
        )

    # def _init_openai(self, temperature: float, **overrides) -> BaseLanguageModel:
    #     cfg = {
    #         "model": self.config.OPENAI_CHAT_MODEL_NAME,
    #         "api_key": self.config.get("OPENAI_API_KEY"),
    #         "temperature": temperature,
    #     }

        # if cfg["model"] == "o3-mini":
        #     cfg.pop("temperature", None)

        # cfg.update(overrides)
        # return ChatOpenAI(**cfg)

    # def _init_anthropic(self, temperature: float, **overrides) -> BaseLanguageModel:
    #     return ChatAnthropic(
    #         model=self.config.ANTHROPIC_MODEL_NAME,
    #         api_key=self.config.get("ANTHROPIC_API_KEY"),
    #         temperature=temperature,
    #         **overrides
    #     )

    # def _init_gemini(self, temperature: float, **overrides) -> BaseLanguageModel:
    #     return ChatGoogleGenerativeAI(
    #         model=self.config.GEMINI_MODEL_NAME,
    #         api_key=self.config.get("GEMINI_API_KEY"),
    #         temperature=temperature,
    #         **overrides
    #     )

    def create_llm(
        self,
        provider: str,
        temperature: float = 0.3,
        model_overrides: Optional[Dict[str, Any]] = None,
        structured_output: Optional[Any] = None
    ) -> BaseLanguageModel:
        """
        Constructs the LLM client for a given provider.
        """
        model_overrides = model_overrides or {}

        provider_map = {
            "groq": self._init_groq,
            # "openai": self._init_openai,
            # "anthropic": self._init_anthropic,
            # "gemini": self._init_gemini
        }

        if provider not in provider_map:
            raise ValueError(f"Unsupported provider: {provider}")
        
        logger.info(f"Initializing LLM provider: {provider} | Temperature: {temperature} | Overrides: {model_overrides}")

        llm_instance = provider_map[provider](temperature, **model_overrides)

        return llm_instance.with_structured_output(structured_output) if structured_output else llm_instance


class LLMManager:
    """
    Singleton interface for creating and reusing LLM instances.
    """

    _instance = None
    _llm_factory: Optional[LLMProviderFactory] = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                app_config = AppConfig.get_config_instance()
                cls._instance._llm_factory = LLMProviderFactory(app_config)
        return cls._instance

    @classmethod
    def get_llm(
        cls,
        provider: str = "groq",
        temperature: float = 0.3,
        model_overrides: Optional[Dict[str, Any]] = None,
        structured_output: Optional[Any] = None
    ) -> BaseLanguageModel:
        """
        Access point to obtain an LLM with specified configuration.
        """
        return cls()._llm_factory.create_llm(
            provider=provider,
            temperature=temperature,
            model_overrides=model_overrides,
            structured_output=structured_output
        )
