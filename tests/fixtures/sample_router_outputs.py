"""Sample RouterDecision outputs for mocking LLM router agent."""

from llm.schemas import RouterDecision


def router_subscriptions() -> RouterDecision:
    """Router output for 'What are my subscriptions?'."""
    return RouterDecision(
        intent="subscription_analysis",
        required_agents=["transaction_context", "subscription", "response_synthesis"],
        reasoning="User asked about subscriptions.",
        needs_transaction_context=True,
        needs_spending_analysis=False,
        needs_subscription_analysis=True,
        needs_savings_analysis=False,
        needs_investment_analysis=False,
        response_mode="synthesis",
    )


def router_spending_last_month() -> RouterDecision:
    """Router output for 'How much did I spend last month?'."""
    return RouterDecision(
        intent="spending_analysis",
        required_agents=["transaction_context", "spending_insights", "response_synthesis"],
        reasoning="User asked about spending.",
        needs_transaction_context=True,
        needs_spending_analysis=True,
        needs_subscription_analysis=False,
        needs_savings_analysis=False,
        needs_investment_analysis=False,
        response_mode="synthesis",
    )


def router_savings_goal() -> RouterDecision:
    """Router output for 'How can I save $20,000 in 12 months?'."""
    return RouterDecision(
        intent="savings_goal_planning",
        required_agents=["transaction_context", "spending_insights", "subscription", "savings", "response_synthesis"],
        reasoning="User asked about savings goal.",
        needs_transaction_context=True,
        needs_spending_analysis=True,
        needs_subscription_analysis=True,
        needs_savings_analysis=True,
        needs_investment_analysis=False,
        response_mode="synthesis",
    )


def router_investment_medium_risk() -> RouterDecision:
    """Router output for 'Can I invest with medium risk over 24 months?'."""
    return RouterDecision(
        intent="investment_suggestions",
        required_agents=["transaction_context", "investment", "response_synthesis"],
        reasoning="User asked about investment with risk and horizon.",
        needs_transaction_context=True,
        needs_spending_analysis=False,
        needs_subscription_analysis=False,
        needs_savings_analysis=False,
        needs_investment_analysis=True,
        response_mode="synthesis",
    )


def router_full_review() -> RouterDecision:
    """Router output for 'Give me a full financial review.'."""
    return RouterDecision(
        intent="full_financial_review",
        required_agents=[
            "transaction_context",
            "spending_insights",
            "subscription",
            "savings",
            "investment",
            "response_synthesis",
        ],
        reasoning="User requested full review.",
        needs_transaction_context=True,
        needs_spending_analysis=True,
        needs_subscription_analysis=True,
        needs_savings_analysis=True,
        needs_investment_analysis=True,
        response_mode="synthesis",
    )


def router_savings_and_investment() -> RouterDecision:
    """Router for 'Save $15K in 10 months, what to cut and where to invest?'."""
    return RouterDecision(
        intent="full_financial_review",
        required_agents=[
            "transaction_context",
            "spending_insights",
            "subscription",
            "savings",
            "investment",
            "response_synthesis",
        ],
        reasoning="Combined savings and investment question.",
        needs_transaction_context=True,
        needs_spending_analysis=True,
        needs_subscription_analysis=True,
        needs_savings_analysis=True,
        needs_investment_analysis=True,
        response_mode="synthesis",
    )


def router_direct_refusal() -> RouterDecision:
    """Router output for unsupported request (e.g. tax advice)."""
    return RouterDecision(
        intent="unsupported_or_insufficient_request",
        required_agents=[],
        reasoning="Tax advice is not supported.",
        needs_transaction_context=False,
        needs_spending_analysis=False,
        needs_subscription_analysis=False,
        needs_savings_analysis=False,
        needs_investment_analysis=False,
        response_mode="direct_refusal",
    )
