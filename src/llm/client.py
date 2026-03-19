"""
LLM client for the Finance Agentic System.

Provides OpenAI ChatOpenAI via LangChain with structured output support.
"""

from typing import Type, TypeVar

from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from config.settings import settings
from utils.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)

_llm: ChatOpenAI | None = None


def get_llm() -> ChatOpenAI:
    """Get or create the shared ChatOpenAI instance."""
    global _llm
    if _llm is None:
        api_key = (settings.OPENAI_API_KEY or "").strip()
        model = (getattr(settings, "OPENAI_MODEL", None) or "").strip() or "gpt-4o-mini"
        temperature = getattr(settings, "OPENAI_TEMPERATURE", 0.2)
        if not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 2:
            temperature = 0.2
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for LLM-based agents.")
        _llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key,
        )
        logger.info("Initialized ChatOpenAI with model=%s", model)
    return _llm


def get_llm_structured(schema: Type[T]) -> ChatOpenAI:
    """Get ChatOpenAI configured for structured output with the given Pydantic schema."""
    llm = get_llm()
    return llm.with_structured_output(schema)
