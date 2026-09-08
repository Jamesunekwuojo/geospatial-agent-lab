from pathlib import Path

import geopandas as gpd
import numpy as np
from shapely.geometry import box


GRID_SIZE = 10
CELL_SIZE = 0.01

BASELINE_YEAR = 2020
CURRENT_YEAR = 2025

OUTPUT_DIR = Path("data/synthetic")
OUTPUT_FILE = OUTPUT_DIR / "vegetation_grid.geojson"


def generate_dataset() -> gpd.GeoDataFrame:
    rng = np.random.default_rng(42)

    records = []

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            cell_id = f"cell_{row:02d}_{col:02d}"

            min_x = col * CELL_SIZE
            min_y = row * CELL_SIZE
            max_x = min_x + CELL_SIZE
            max_y = min_y + CELL_SIZE

            geometry = box(
                min_x,
                min_y,
                max_x,
                max_y,
            )

            # Natural variation in vegetation health.
            baseline_ndvi = rng.uniform(0.55, 0.85)

            # Small natural year-to-year variation.
            natural_change = rng.normal(0.0, 0.015)

            current_ndvi = baseline_ndvi + natural_change

            records.append(
                {
                    "cell_id": cell_id,
                    "row": row,
                    "col": col,
                    "baseline_year": BASELINE_YEAR,
                    "current_year": CURRENT_YEAR,
                    "baseline_ndvi": baseline_ndvi,
                    "current_ndvi": current_ndvi,
                    "geometry": geometry,
                }
            )

    gdf = gpd.GeoDataFrame(
        records,
        geometry="geometry",
        crs="EPSG:4326",
    )

    # ---------------------------------------------------------
    # Inject known vegetation degradation.
    # ---------------------------------------------------------
    #
    # These cells represent areas where vegetation health
    # deteriorated significantly between 2020 and 2025.
    #
    degraded_cells = {
        "cell_03_03": -0.20,
        "cell_03_04": -0.18,
        "cell_03_05": -0.22,
        "cell_04_03": -0.25,
        "cell_04_04": -0.21,
        "cell_04_05": -0.19,
        "cell_05_03": -0.17,
        "cell_05_04": -0.23,
        "cell_05_05": -0.20,
    }

    for cell_id, change in degraded_cells.items():
        mask = gdf["cell_id"] == cell_id
        gdf.loc[mask, "current_ndvi"] = (
            gdf.loc[mask, "baseline_ndvi"] + change
        )

    # Calculate the actual change.
    gdf["ndvi_change"] = (
        gdf["current_ndvi"] - gdf["baseline_ndvi"]
    )

    # Ground-truth degradation label.
    #
    # This is intentionally deterministic and will later be
    # useful for evaluating GeoScout.
    gdf["is_degraded"] = gdf["ndvi_change"] <= -0.10

    return gdf


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    gdf = generate_dataset()

    gdf.to_file(
        OUTPUT_FILE,
        driver="GeoJSON",
    )

    print(f"Dataset written to: {OUTPUT_FILE}")
    print(f"Number of cells: {len(gdf)}")
    print(f"CRS: {gdf.crs}")
    print(
        f"Degraded cells: "
        f"{gdf['is_degraded'].sum()}"
    )


if __name__ == "__main__":
    main()
