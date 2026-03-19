"""
Router / Supervisor LLM Agent for the Finance Agentic System.

Interprets the user's natural-language question and determines which
downstream agents should be invoked.
"""

from typing import Any, Dict, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from llm.client import get_llm_structured
from llm.prompts import ROUTER_SYSTEM, ROUTER_USER
from llm.schemas import RouterDecision
from utils.logging import get_logger

logger = get_logger(__name__)


def run_router(
    user_question: str,
    savings_goal_amount: Optional[float] = None,
    savings_goal_months: Optional[int] = None,
    risk_appetite: str = "medium",
    investment_horizon_months: Optional[int] = None,
) -> RouterDecision:
    """
    Analyze the user's question and produce a routing decision.

    Args:
        user_question: Natural-language question from the user.
        savings_goal_amount: Optional structured input.
        savings_goal_months: Optional structured input.
        risk_appetite: Optional risk tolerance.
        investment_horizon_months: Optional investment horizon.

    Returns:
        RouterDecision with required_agents and needs_* flags.
    """
    llm = get_llm_structured(RouterDecision)
    prompt = ChatPromptTemplate.from_messages([
        ("system", ROUTER_SYSTEM),
        ("human", ROUTER_USER),
    ])
    chain = prompt | llm
    decision = chain.invoke({
        "user_question": user_question,
        "savings_goal_amount": savings_goal_amount if savings_goal_amount is not None else "not provided",
        "savings_goal_months": savings_goal_months if savings_goal_months is not None else "not provided",
        "risk_appetite": risk_appetite,
        "investment_horizon_months": investment_horizon_months if investment_horizon_months is not None else "not provided",
    })
    logger.info("Router decision: intent=%s, agents=%s", decision.intent, decision.required_agents)
    return decision


def router_decision_to_dict(decision: RouterDecision) -> Dict[str, Any]:
    """Convert RouterDecision to dict for graph state."""
    return {
        "intent": decision.intent,
        "required_agents": decision.required_agents,
        "reasoning": decision.reasoning,
        "needs_transaction_context": decision.needs_transaction_context,
        "needs_spending_analysis": decision.needs_spending_analysis,
        "needs_subscription_analysis": decision.needs_subscription_analysis,
        "needs_savings_analysis": decision.needs_savings_analysis,
        "needs_investment_analysis": decision.needs_investment_analysis,
        "response_mode": decision.response_mode,
    }
