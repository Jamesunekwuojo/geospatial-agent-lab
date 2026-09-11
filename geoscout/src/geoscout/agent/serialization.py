from typing import Any

import geopandas as gpd
import pandas as pd


def serialize_tool_result(result: Any) -> str:
    """
    Convert a GIS tool result into a compact representation
    suitable for an LLM tool message.
    """

    if isinstance(result, gpd.GeoDataFrame):
        data = result.copy()

        columns = [
            column
            for column in [
                "cell_id",
                "row",
                "col",
                "baseline_year",
                "current_year",
                "baseline_ndvi",
                "current_ndvi",
                "ndvi_change",
                "is_degraded",
            ]
            if column in data.columns
        ]

        max_records = 20
        compact = data[columns].head(max_records).to_dict(orient="records")

        return str(
            {
                "type": "geospatial_table",
                "row_count": len(data),
                "columns": columns,
                "records": compact,
                "truncated": len(data) > max_records,
            }
        )

        # compact = data[columns].to_dict(orient="records")

        # return str(
        #     {
        #         "type": "geospatial_table",
        #         "row_count": len(data),
        #         "columns": columns,
        #         "records": compact,
        #     }
        # )

    if isinstance(result, pd.DataFrame):
        return str(
            {
                "type": "table",
                "row_count": len(result),
                "records": result.to_dict(orient="records"),
            }
        )

    if isinstance(result, dict):
        return str(result)

    if isinstance(result, list):
        return str(result)

    return str(result)
