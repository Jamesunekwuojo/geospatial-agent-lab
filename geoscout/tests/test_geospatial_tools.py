from geoscout.tools.geospatial import (
    calculate_ndvi_change,
    calculate_statistics,
    detect_change_hotspots,
    get_region,
    summarize_hotspots,
)


def test_get_region():
    result = get_region()

    assert result["cell_count"] == 100
    assert result["crs"] == "EPSG:4326"


def test_calculate_ndvi_change():
    gdf = calculate_ndvi_change()

    assert "ndvi_change" in gdf.columns
    assert len(gdf) == 100

    expected = (
        gdf["current_ndvi"] - gdf["baseline_ndvi"]
    )

    assert (
        expected.round(10)
        == gdf["ndvi_change"].round(10)
    ).all()


def test_detect_change_hotspots():
    hotspots = detect_change_hotspots()

    assert len(hotspots) == 9
    assert (hotspots["ndvi_change"] <= -0.10).all()


def test_statistics():
    statistics = calculate_statistics()

    assert statistics["cell_count"] == 100
    assert statistics["degraded_cells"] == 9


def test_hotspot_summary():
    summary = summarize_hotspots()

    assert summary["threshold"] == -0.10
    assert summary["hotspot_count"] == 9
    assert len(summary["hotspot_cells"]) == 9
