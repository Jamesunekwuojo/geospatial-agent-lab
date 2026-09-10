from pathlib import Path

import geopandas as gpd

DEFAULT_DATASET = Path("data/synthetic/vegetation_grid.geojson")


def _resolve_dataset_path(dataset_path: Path | str) -> Path:
    p = Path(dataset_path)
    if p.exists():
        return p
    # Try relative to the package root (handles running from repo root or arbitrary cwd)
    pkg_data = Path(__file__).resolve().parent.parent.parent.parent / "data" / "synthetic" / p.name
    if pkg_data.exists():
        return pkg_data
    repo_data = Path("geoscout") / p
    if repo_data.exists():
        return repo_data
    return p


def load_dataset(
    dataset_path: Path = DEFAULT_DATASET,
) -> gpd.GeoDataFrame:
    """Load the GeoScout synthetic geospatial dataset."""
    resolved_path = _resolve_dataset_path(dataset_path)
    if not resolved_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    return gpd.read_file(resolved_path)


def get_region(
    dataset_path: Path = DEFAULT_DATASET,
) -> dict:
    """Return basic information about the study region."""

    gdf = load_dataset(dataset_path)

    min_x, min_y, max_x, max_y = gdf.total_bounds

    return {
        "cell_count": len(gdf),
        "crs": gdf.crs.to_string(),
        "bounds": {
            "min_x": float(min_x),
            "min_y": float(min_y),
            "max_x": float(max_x),
            "max_y": float(max_y),
        },
    }


def calculate_ndvi_change(
    dataset_path: Path = DEFAULT_DATASET,
) -> gpd.GeoDataFrame:
    """Calculate vegetation-health change for every spatial cell."""

    gdf = load_dataset(dataset_path).copy()

    gdf["ndvi_change"] = gdf["current_ndvi"] - gdf["baseline_ndvi"]

    return gdf


def detect_change_hotspots(
    threshold: float = -0.10,
    dataset_path: Path = DEFAULT_DATASET,
) -> gpd.GeoDataFrame:
    """
    Identify cells where NDVI deterioration is greater
    than or equal to the specified negative threshold.
    """

    gdf = calculate_ndvi_change(dataset_path)

    hotspots = gdf[gdf["ndvi_change"] <= threshold].copy()

    return hotspots


def calculate_statistics(
    dataset_path: Path = DEFAULT_DATASET,
) -> dict:
    """Calculate summary statistics for NDVI change."""

    gdf = calculate_ndvi_change(dataset_path)

    changes = gdf["ndvi_change"]

    return {
        "cell_count": int(len(gdf)),
        "mean_change": float(changes.mean()),
        "median_change": float(changes.median()),
        "minimum_change": float(changes.min()),
        "maximum_change": float(changes.max()),
        "degraded_cells": int((changes <= -0.10).sum()),
    }


def summarize_hotspots(
    threshold: float = -0.10,
    dataset_path: Path = DEFAULT_DATASET,
) -> dict:
    """Return a compact summary of detected change hotspots."""

    hotspots = detect_change_hotspots(
        threshold=threshold,
        dataset_path=dataset_path,
    )

    return {
        "threshold": threshold,
        "hotspot_count": int(len(hotspots)),
        "hotspot_cells": hotspots["cell_id"].tolist(),
        "mean_ndvi_change": (float(hotspots["ndvi_change"].mean()) if len(hotspots) > 0 else None),
    }


def export_hotspots(
    output_path: Path,
    threshold: float = -0.10,
    dataset_path: Path = DEFAULT_DATASET,
) -> Path:
    """Export detected hotspots as GeoJSON."""

    hotspots = detect_change_hotspots(
        threshold=threshold,
        dataset_path=dataset_path,
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    hotspots.to_file(
        output_path,
        driver="GeoJSON",
    )

    return output_path
