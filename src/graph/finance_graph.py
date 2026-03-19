"""
LangGraph finance analysis workflow for the Finance Agentic System.

Two flows:
1. Legacy: transaction_context -> categorize -> spending -> subscriptions -> savings -> investment -> compile_final_summary (all LLM)
2. QA: router -> transaction_context -> run_agents (conditional) -> response_synthesis
"""

from typing import Any, Dict, Literal, Optional

from langgraph.graph import END, StateGraph
from sqlalchemy.orm import Session

from agents.categorization_agent import run_categorization
from agents.investment_agent import get_investment_suggestions, investment_result_to_legacy_format
from agents.response_synthesis_agent import run_response_synthesis
from agents.router_agent import run_router, router_decision_to_dict
from agents.savings_agent import generate_savings_plan, savings_result_to_legacy_format
from agents.spending_insights_agent import run_spending_insights, spending_insights_to_legacy_format
from agents.subscription_agent import detect_subscriptions, subscription_result_to_legacy_format
from agents.transaction_context_agent import run_transaction_context, transaction_context_to_dict
from graph.state import FinanceGraphState
from utils.logging import get_logger

logger = get_logger(__name__)


def _dict_from_obj(obj: Any) -> Dict[str, Any]:
    """Convert dataclass/dict to plain dict for JSON serialization."""
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "__dataclass_fields__"):
        return {k: getattr(obj, k) for k in obj.__dataclass_fields__ if not k.startswith("_")}
    return {}


def categorize_transactions_node(state: FinanceGraphState) -> Dict[str, Any]:
    """Categorize uncategorized transactions and update DB."""
    session: Optional[Session] = state.session
    if not session:
        raise ValueError("Database session required")
    transactions, summary = run_categorization(
        session, user_id=state.user_id, update_db=True
    )
    return {
        "categorized_transactions": transactions,
        "categorization_summary": summary,
    }


def spending_insights_node(state: FinanceGraphState) -> Dict[str, Any]:
    """Compute spending insights (LLM)."""
    session: Optional[Session] = state.session
    if not session:
        raise ValueError("Database session required")
    context_narr = state.transaction_context.get("context_narrative") if state.transaction_context else None
    insights = run_spending_insights(session, user_id=state.user_id, months=3, context_narrative=context_narr)
    return {"spending_insights": spending_insights_to_legacy_format(insights)}


def detect_subscriptions_node(state: FinanceGraphState) -> Dict[str, Any]:
    """Detect recurring subscriptions (LLM)."""
    session: Optional[Session] = state.session
    if not session:
        raise ValueError("Database session required")
    result = detect_subscriptions(session, user_id=state.user_id, months=6)
    subs_list, summary = subscription_result_to_legacy_format(result)
    return {"subscriptions": subs_list, "subscription_summary": summary}


def savings_analysis_node(state: FinanceGraphState) -> Dict[str, Any]:
    """Generate savings plan (LLM) if goal inputs provided."""
    session: Optional[Session] = state.session
    if not session:
        raise ValueError("Database session required")
    result: Dict[str, Any] = {"savings_metrics": {}}

    goal_amount = state.savings_goal_amount or 0.0
    goal_months = state.savings_goal_months or 12
    if state.savings_goal_amount is not None and state.savings_goal_months is not None:
        ctx = state.transaction_context.get("context_narrative") if state.transaction_context else None
        spend_narr = (
            state.spending_insights.get("narrative_summary") or state.spending_insights.get("human_summary")
            if state.spending_insights else None
        )
        sub_narr = state.subscription_summary.get("narrative_summary") if state.subscription_summary else None
        plan = generate_savings_plan(
            session=session,
            user_id=state.user_id,
            savings_goal_amount=goal_amount,
            savings_goal_months=goal_months,
            context_narrative=ctx,
            spending_narrative=spend_narr,
            subscription_narrative=sub_narr,
            months=6,
        )
        leg = savings_result_to_legacy_format(plan)
        result["savings_plan"] = leg
        result["savings_metrics"] = {
            "current_estimated_monthly_savings": plan.current_estimated_monthly_savings,
        }
    return result


def investment_suggestions_node(state: FinanceGraphState) -> Dict[str, Any]:
    """Generate educational investment suggestions (LLM)."""
    surplus = 0.0
    if state.savings_metrics:
        surplus = (
            state.savings_metrics.get("average_monthly_savings")
            or state.savings_metrics.get("current_estimated_monthly_savings")
            or 0
        )
    stability_note = ""
    if state.savings_plan and isinstance(state.savings_plan.get("limitations"), list):
        stability_note = " ".join(state.savings_plan.get("limitations", []))
    suggestions = get_investment_suggestions(
        risk_appetite=state.risk_appetite or "medium",
        time_horizon_months=state.investment_horizon_months or 60,
        monthly_surplus=surplus,
        stability_note=stability_note or None,
    )
    return {
        "investment_profile": {
            "risk_appetite": state.risk_appetite,
            "horizon_months": state.investment_horizon_months,
        },
        "investment_suggestions": investment_result_to_legacy_format(suggestions),
    }


def router_node(state: FinanceGraphState) -> Dict[str, Any]:
    """Route user question to determine which agents to run."""
    decision = run_router(
        user_question=state.user_question or "",
        savings_goal_amount=state.savings_goal_amount,
        savings_goal_months=state.savings_goal_months,
        risk_appetite=state.risk_appetite,
        investment_horizon_months=state.investment_horizon_months,
    )
    return {"router_decision": router_decision_to_dict(decision)}


def transaction_context_node(state: FinanceGraphState) -> Dict[str, Any]:
    """Load transactions and produce LLM context narrative."""
    session: Optional[Session] = state.session
    if not session:
        raise ValueError("Database session required")
    result = run_transaction_context(session, user_id=state.user_id, months=6)
    return {"transaction_context": transaction_context_to_dict(result)}


def run_qa_agents_node(state: FinanceGraphState) -> Dict[str, Any]:
    """Run spending, subscription, savings, investment agents based on router decision."""
    session: Optional[Session] = state.session
    rd = state.router_decision or {}
    updates: Dict[str, Any] = {}

    if rd.get("needs_spending_analysis"):
        context_narr = (state.transaction_context or {}).get("context_narrative")
        insights = run_spending_insights(session, state.user_id, months=3, context_narrative=context_narr)
        updates["spending_insights"] = spending_insights_to_legacy_format(insights)

    if rd.get("needs_subscription_analysis"):
        sub_result = detect_subscriptions(session, state.user_id, months=6)
        subs_list, summary = subscription_result_to_legacy_format(sub_result)
        updates["subscriptions"] = subs_list
        updates["subscription_summary"] = summary

    if rd.get("needs_savings_analysis") and state.savings_goal_amount and state.savings_goal_months:
        ctx = (state.transaction_context or {}).get("context_narrative")
        spend_narr = (state.spending_insights or {}).get("narrative_summary") or (state.spending_insights or {}).get("human_summary")
        sub_narr = (state.subscription_summary or {}).get("narrative_summary")
        plan = generate_savings_plan(
            session=session,
            user_id=state.user_id,
            savings_goal_amount=state.savings_goal_amount,
            savings_goal_months=state.savings_goal_months,
            context_narrative=ctx,
            spending_narrative=spend_narr,
            subscription_narrative=sub_narr,
            months=6,
        )
        updates["savings_plan"] = savings_result_to_legacy_format(plan)
        updates["savings_metrics"] = {"current_estimated_monthly_savings": plan.current_estimated_monthly_savings}

    if rd.get("needs_investment_analysis"):
        surplus = (state.savings_metrics or {}).get("current_estimated_monthly_savings") or 0
        stability = " ".join((state.savings_plan or {}).get("limitations", [])) if isinstance((state.savings_plan or {}).get("limitations"), list) else ""
        inv_result = get_investment_suggestions(
            risk_appetite=state.risk_appetite or "medium",
            time_horizon_months=state.investment_horizon_months or 60,
            monthly_surplus=surplus,
            stability_note=stability or None,
        )
        updates["investment_suggestions"] = investment_result_to_legacy_format(inv_result)

    return updates


def response_synthesis_node(state: FinanceGraphState) -> Dict[str, Any]:
    """Compile agent outputs into FinalResponse."""
    rd = state.router_decision or {}
    final = run_response_synthesis(
        user_question=state.user_question or "",
        router_reasoning=rd.get("reasoning", ""),
        transaction_context=state.transaction_context,
        spending_insights=state.spending_insights,
        subscription_findings=state.subscription_summary,
        savings_plan=state.savings_plan,
        investment_suggestions=state.investment_suggestions,
    )
    return {"final_response": final.model_dump()}


def direct_refusal_node(state: FinanceGraphState) -> Dict[str, Any]:
    """Handle unsupported or insufficient requests."""
    rd = state.router_decision or {}
    reason = rd.get("reasoning", "Request not supported.")
    return {
        "final_response": {
            "executive_summary": f"Cannot fulfill request: {reason}",
            "confirmed_facts": [],
            "inferred_insights": [],
            "limitations": [reason],
            "recommendations": [],
            "disclaimer": None,
        }
    }


def _entry_path(state: FinanceGraphState) -> Literal["router", "transaction_context"]:
    """Determine entry point: QA flow if user_question, else legacy (starts with transaction_context)."""
    return "router" if state.user_question else "transaction_context"


def _router_next(state: FinanceGraphState) -> Literal["direct_refusal", "transaction_context"]:
    """After router: direct_refusal or transaction_context."""
    rd = state.router_decision or {}
    return "direct_refusal" if rd.get("response_mode") == "direct_refusal" else "transaction_context"


def _transaction_context_next(
    state: FinanceGraphState,
) -> Literal["run_qa_agents", "categorize_transactions"]:
    """After transaction_context: QA agents if user asked, else legacy pipeline."""
    return "run_qa_agents" if state.user_question else "categorize_transactions"


def compile_final_summary_node(state: FinanceGraphState) -> Dict[str, Any]:
    """LLM-based: Synthesize final response from all agent outputs (legacy flow)."""
    user_question = state.user_question or "Provide a comprehensive financial summary based on the analysis."
    rd = state.router_decision or {}
    final = run_response_synthesis(
        user_question=user_question,
        router_reasoning=rd.get("reasoning", "Full financial analysis requested."),
        transaction_context=state.transaction_context,
        spending_insights=state.spending_insights,
        subscription_findings=state.subscription_summary,
        savings_plan=state.savings_plan,
        investment_suggestions=state.investment_suggestions,
    )
    return {
        "final_response": final.model_dump(),
        "final_summary": final.executive_summary,
    }


def build_finance_graph():
    """Build the LangGraph workflow."""
    graph = StateGraph(FinanceGraphState)

    graph.add_node("categorize_transactions", categorize_transactions_node)
    graph.add_node("spending_insights", spending_insights_node)
    graph.add_node("detect_subscriptions", detect_subscriptions_node)
    graph.add_node("savings_analysis", savings_analysis_node)
    graph.add_node("investment_suggestions", investment_suggestions_node)
    graph.add_node("compile_final_summary", compile_final_summary_node)

    graph.add_node("router", router_node)
    graph.add_node("transaction_context", transaction_context_node)
    graph.add_node("run_qa_agents", run_qa_agents_node)
    graph.add_node("response_synthesis", response_synthesis_node)
    graph.add_node("direct_refusal", direct_refusal_node)

    graph.set_conditional_entry_point(_entry_path, {"router": "router", "transaction_context": "transaction_context"})
    graph.add_conditional_edges("router", _router_next, {"direct_refusal": "direct_refusal", "transaction_context": "transaction_context"})
    graph.add_conditional_edges("transaction_context", _transaction_context_next, {"run_qa_agents": "run_qa_agents", "categorize_transactions": "categorize_transactions"})
    graph.add_edge("run_qa_agents", "response_synthesis")
    graph.add_edge("response_synthesis", END)
    graph.add_edge("direct_refusal", END)
    graph.add_edge("categorize_transactions", "spending_insights")
    graph.add_edge("spending_insights", "detect_subscriptions")
    graph.add_edge("detect_subscriptions", "savings_analysis")
    graph.add_edge("savings_analysis", "investment_suggestions")
    graph.add_edge("investment_suggestions", "compile_final_summary")
    graph.add_edge("compile_final_summary", END)

    return graph.compile()


# Module-level compiled graph
_finance_graph = None


def get_finance_graph():
    """Get or create the compiled finance graph."""
    global _finance_graph
    if _finance_graph is None:
        _finance_graph = build_finance_graph()
    return _finance_graph


def run_finance_analysis(
    session: Session,
    user_id: str = "default",
    savings_goal_amount: Optional[float] = None,
    savings_goal_months: Optional[int] = None,
    risk_appetite: str = "medium",
    investment_horizon_months: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Run the full finance analysis workflow.

    Args:
        session: Database session.
        user_id: User identifier.
        savings_goal_amount: Optional target savings amount.
        savings_goal_months: Optional target timeframe in months.
        risk_appetite: low, medium, or high.
        investment_horizon_months: Expected investment horizon.

    Returns:
        Final state dict with all analysis results.
    """
    graph = get_finance_graph()
    initial_state = FinanceGraphState(
        user_id=user_id,
        session=session,
        savings_goal_amount=savings_goal_amount,
        savings_goal_months=savings_goal_months,
        risk_appetite=risk_appetite,
        investment_horizon_months=investment_horizon_months or 60,
    )
    result = graph.invoke(initial_state)
    # Convert to plain dict, excluding non-serializable session
    out = {
        "user_id": result.user_id,
        "categorization_summary": result.categorization_summary,
        "spending_insights": result.spending_insights,
        "subscriptions": result.subscriptions,
        "subscription_summary": result.subscription_summary,
        "savings_metrics": result.savings_metrics,
        "savings_plan": result.savings_plan,
        "investment_profile": result.investment_profile,
        "investment_suggestions": result.investment_suggestions,
        "final_summary": result.final_summary,
    }
    return out


def run_ask(
    session: Session,
    user_question: str,
    user_id: str = "default",
    savings_goal_amount: Optional[float] = None,
    savings_goal_months: Optional[int] = None,
    risk_appetite: str = "medium",
    investment_horizon_months: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Run the QA flow: route question -> transaction context -> agents -> synthesis.

    Args:
        session: Database session.
        user_question: Natural-language question.
        user_id: User identifier.
        savings_goal_amount: Optional for savings analysis.
        savings_goal_months: Optional for savings analysis.
        risk_appetite: low, medium, or high.
        investment_horizon_months: Optional for investment suggestions.

    Returns:
        Dict with final_response (and optionally router_decision, etc.).
    """
    graph = get_finance_graph()
    initial_state = FinanceGraphState(
        user_id=user_id,
        session=session,
        user_question=user_question,
        savings_goal_amount=savings_goal_amount,
        savings_goal_months=savings_goal_months,
        risk_appetite=risk_appetite,
        investment_horizon_months=investment_horizon_months or 60,
    )
    result = graph.invoke(initial_state)
    # LangGraph may return dict or state object
    if isinstance(result, dict):
        return {
            "user_id": result.get("user_id", user_id),
            "question": user_question,
            "router_decision": result.get("router_decision"),
            "final_response": result.get("final_response"),
        }
    return {
        "user_id": result.user_id,
        "question": user_question,
        "router_decision": result.router_decision,
        "final_response": result.final_response,
    }
