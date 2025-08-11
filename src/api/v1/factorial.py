"""Factorial operation API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.deps import get_factorial_service, verify_api_key
from domain.models import FactorialRequest
from services.factorial import FactorialService

router = APIRouter(prefix="/v1/factorial", tags=["Factorial Operations"])


class FactorialRequestModel(BaseModel):
    """Request model for factorial calculation."""

    n: int = Field(
        ..., ge=0, description="Number to calculate factorial for", example=5
    )


class FactorialResponseModel(BaseModel):
    """Response model for factorial calculation."""

    n: int = Field(..., description="Input number")
    result: int = Field(..., description="Factorial result")


@router.post(
    "/",
    response_model=FactorialResponseModel,
    summary="Calculate factorial",
    description="Calculate factorial of a number (n!)",
)
async def calculate_factorial(
    request: FactorialRequestModel,
    _: Annotated[None, Depends(verify_api_key)],
    service: Annotated[FactorialService, Depends(get_factorial_service)],
) -> FactorialResponseModel:
    """Calculate n! (factorial)."""
    try:
        # Convert to domain model
        domain_request = FactorialRequest(n=request.n)

        # Calculate result
        result = await service.calculate_factorial(domain_request)

        # Return response
        return FactorialResponseModel(
            n=result.n,
            result=result.result,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
