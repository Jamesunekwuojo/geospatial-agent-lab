from geoscout.data.generate_synthetic import generate_dataset


def test_dataset_has_100_cells():
    gdf = generate_dataset()

    assert len(gdf) == 100


def test_dataset_has_expected_crs():
    gdf = generate_dataset()

    assert gdf.crs.to_string() == "EPSG:4326"


def test_dataset_has_nine_degraded_cells():
    gdf = generate_dataset()

    assert gdf["is_degraded"].sum() == 9


def test_ndvi_change_is_correct():
    gdf = generate_dataset()

    calculated_change = gdf["current_ndvi"] - gdf["baseline_ndvi"]

    assert (calculated_change.round(10) == gdf["ndvi_change"].round(10)).all()
