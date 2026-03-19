"""
FastAPI endpoints for natural-language Q&A on finances.

POST /finance/ask - Ask a question and receive a synthesized LLM-based response.
"""

from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database.db import get_db
from graph.finance_graph import run_ask
from utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/finance", tags=["finance-qa"])


class AskRequest(BaseModel):
    """Request for natural-language finance Q&A."""

    user_id: str = Field(default="default", description="User identifier")
    question: str = Field(..., description="Natural-language question about your finances")
    savings_goal_amount: Optional[float] = Field(default=None, gt=0)
    savings_goal_months: Optional[int] = Field(default=None, gt=0, le=600)
    risk_appetite: Literal["low", "medium", "high"] = Field(default="medium")
    investment_horizon_months: Optional[int] = Field(default=None, ge=1, le=600)


@router.post("/ask")
def ask(
    body: AskRequest,
    db: Session = Depends(get_db),
) -> dict:
    """
    Ask a natural-language question about your finances.

    The system routes your question to the appropriate analysis agents
    (spending, subscriptions, savings, investment) and synthesizes a response.
    """
    try:
        result = run_ask(
            session=db,
            user_question=body.question,
            user_id=body.user_id,
            savings_goal_amount=body.savings_goal_amount,
            savings_goal_months=body.savings_goal_months,
            risk_appetite=body.risk_appetite,
            investment_horizon_months=body.investment_horizon_months,
        )
        return result
    except Exception as e:
        logger.exception("Ask error: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e
