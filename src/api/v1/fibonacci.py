"""Fibonacci operation API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field

from api.deps import get_fibonacci_service, verify_api_key
from services.fibonacci import FibonacciService

router = APIRouter(prefix="/v1/fibonacci", tags=["Fibonacci Operations"])


class FibonacciResponseModel(BaseModel):
    """Response model for Fibonacci calculation."""
    
    n: int = Field(..., description="Input number")
    result: int = Field(..., description="Fibonacci result")


@router.get(
    "/{n}",
    response_model=FibonacciResponseModel,
    summary="Calculate Fibonacci number",
    description="Calculate the nth Fibonacci number"
)
async def calculate_fibonacci(
    n: Annotated[int, Path(ge=0, description="Position in Fibonacci sequence")],
    _: Annotated[None, Depends(verify_api_key)],
    service: Annotated[FibonacciService, Depends(get_fibonacci_service)],
) -> FibonacciResponseModel:
    """Calculate nth Fibonacci number."""
    try:
        # Calculate result
        result = await service.calculate_fibonacci(n)
        
        # Return response
        return FibonacciResponseModel(
            n=result.n,
            result=result.result,
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
