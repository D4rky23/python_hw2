"""Power operation API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.deps import get_power_service, verify_api_key
from domain.models import PowerRequest
from services.power import PowerService

router = APIRouter(prefix="/v1/power", tags=["Power Operations"])


class PowerRequestModel(BaseModel):
    """Request model for power calculation."""

    base: int = Field(..., description="Base number", example=2)
    exponent: int = Field(
        ..., ge=0, description="Exponent (non-negative)", example=3
    )


class PowerResponseModel(BaseModel):
    """Response model for power calculation."""

    base: int = Field(..., description="Base number")
    exponent: int = Field(..., description="Exponent")
    result: int = Field(..., description="Calculation result")


@router.post(
    "/",
    response_model=PowerResponseModel,
    summary="Calculate power",
    description="Calculate base raised to the power of exponent",
)
async def calculate_power(
    request: PowerRequestModel,
    _: Annotated[None, Depends(verify_api_key)],
    service: Annotated[PowerService, Depends(get_power_service)],
) -> PowerResponseModel:
    """Calculate base^exponent."""
    try:
        # Convert to domain model
        domain_request = PowerRequest(
            base=request.base, exponent=request.exponent
        )

        # Calculate result
        result = await service.calculate_power(domain_request)

        # Return response
        return PowerResponseModel(
            base=result.base,
            exponent=result.exponent,
            result=result.result,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
