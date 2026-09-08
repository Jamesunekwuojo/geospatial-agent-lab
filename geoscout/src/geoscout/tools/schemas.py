from typing import Any

from pydantic import BaseModel, Field


class GetRegionInput(BaseModel):
    """Input for retrieving study-region information."""

    pass


class CalculateNDVIChangeInput(BaseModel):
    """Input for calculating NDVI change."""

    pass


class DetectChangeHotspotsInput(BaseModel):
    """Input for detecting significant vegetation deterioration."""

    threshold: float = Field(
        default=-0.10,
        description=(
            "NDVI change threshold. "
            "Cells with NDVI change less than or equal to this "
            "value are considered degradation hotspots."
        ),
    )


class CalculateStatisticsInput(BaseModel):
    """Input for calculating NDVI change statistics."""

    pass


class SummarizeHotspotsInput(BaseModel):
    """Input for summarizing detected degradation hotspots."""

    threshold: float = Field(
        default=-0.10,
        description=(
            "NDVI change threshold used to identify degradation hotspots."
        ),
    )


class ToolDefinition(BaseModel):
    """Standard representation of a GeoScout agent tool."""

    name: str
    description: str
    input_schema: dict[str, Any]
