from geoscout.__main__ import main


def test_geoscout_starts(capsys):
    main()

    captured = capsys.readouterr()

    assert "GeoScout initialized successfully." in captured.out