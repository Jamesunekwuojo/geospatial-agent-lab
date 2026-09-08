from geoscout.tools.schemas import (
    CalculateNDVIChangeInput,
    CalculateStatisticsInput,
    DetectChangeHotspotsInput,
    GetRegionInput,
    SummarizeHotspotsInput,
    ToolDefinition,
)

TOOLS = [
    ToolDefinition(
        name="get_region",
        description=(
            "Retrieve basic information about the study region, "
            "including spatial extent, coordinate reference system, "
            "and number of spatial cells."
        ),
        input_schema=GetRegionInput.model_json_schema(),
    ),
    ToolDefinition(
        name="calculate_ndvi_change",
        description=(
            "Calculate NDVI change between the fixed baseline and current "
            "years stored in the dataset for every spatial cell. "
            "This tool accepts no arguments."
        ),
        input_schema=CalculateNDVIChangeInput.model_json_schema(),
    ),
    ToolDefinition(
        name="detect_change_hotspots",
        description=(
            "Identify spatial cells experiencing significant "
            "vegetation deterioration based on an NDVI change threshold."
        ),
        input_schema=DetectChangeHotspotsInput.model_json_schema(),
    ),
    ToolDefinition(
        name="calculate_statistics",
        description=(
            "Calculate summary statistics describing vegetation change across the study region."
        ),
        input_schema=CalculateStatisticsInput.model_json_schema(),
    ),
    ToolDefinition(
        name="summarize_hotspots",
        description=(
            "Return a compact summary of vegetation degradation "
            "hotspots, including their count and cell identifiers."
        ),
        input_schema=SummarizeHotspotsInput.model_json_schema(),
    ),
]
