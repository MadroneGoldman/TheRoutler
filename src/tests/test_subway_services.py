import asyncio
from unittest.mock import patch

import pytest
import pandas as pd

from routler.subway_services import (
    bfs_shortest_path,
    get_routes_and_stops,
    get_subway_routes,
)
from tests.fixtures import (
    routes_response,
    stops_response_RedLine,
    stops_response_BlueLine,
    stops_response_IsolatedLine,
    stops_response_StoplessLine,
)


@patch(
    "routler.subway_services.MBTAClient.get_routes",
    return_value=routes_response,
)
def test_get_subway_routes(mock_get_stops):

    result = asyncio.run(get_subway_routes())

    mock_get_stops.assert_called_once()
    assert isinstance(result, pd.DataFrame)
    assert result.index.tolist() == [
        "Red Line",
        "Blue Line",
        "Stopless Line",
        "Isolated Line",
    ]
    assert result.loc["Red Line", "id"] == "Red"
    assert result.loc["Red Line", "color"] == "DA291C"


@patch(
    "routler.subway_services.MBTAClient.get_routes",
    side_effect=ConnectionError("API connection failed"),
)
def test_get_subway_routes_raises_exception_on_api_error(mock_get_routes, capsys):
    with pytest.raises(ConnectionError):
        asyncio.run(get_subway_routes())
    captured = capsys.readouterr()
    mock_get_routes.assert_called_once()
    assert "Error: API connection failed" in captured.err


@patch("routler.subway_services.MBTAClient.get_stops")
@patch(
    "routler.subway_services.MBTAClient.get_routes",
    side_effect=ConnectionError("API connection failed"),
)
def test_get_routes_and_stops_raises_exception_on_api_error(
    mock_get_routes, mock_get_stops, capsys
):
    with pytest.raises(ConnectionError):
        asyncio.run(get_routes_and_stops())
    captured = capsys.readouterr()
    assert "Error: API connection failed" in captured.err
    mock_get_routes.assert_called_once()
    mock_get_stops.assert_not_called()


@patch(
    "routler.subway_services.MBTAClient.get_stops",
    side_effect=[
        stops_response_RedLine,
        stops_response_BlueLine,
        stops_response_StoplessLine,
        stops_response_IsolatedLine,
    ],
)
@patch(
    "routler.subway_services.MBTAClient.get_routes",
    return_value=routes_response,
)
def test_get_routes_and_stops(mock_get_routes, mock_get_stops):

    result = asyncio.run(get_routes_and_stops())
    assert mock_get_routes.call_count == 1
    assert mock_get_stops.call_count == 4
    assert isinstance(result, pd.DataFrame)

    # check route cols
    assert result.index[result["is_route"] == True].tolist() == [
        "Red Line",
        "Blue Line",
        "Stopless Line",
        "Isolated Line",
    ]
    assert result.loc["Red Line", "links"] == [
        "Kendall/MIT",
        "Harvard",
        "Park Street",
    ]
    assert result.loc["Blue Line", "links"] == [
        "Kendall/MIT",
        "Harvard",
        "Park Street",
        "Blue only stop",
    ]
    assert result.loc["Isolated Line", "links"] == [
        "Isolated Line Stop A",
        "Isolated Line Stop B",
    ]
    assert result.loc["Stopless Line", "links"] == []

    # check stop cols
    assert result.index[result["is_route"] == False].tolist() == [
        "Kendall/MIT",
        "Harvard",
        "Park Street",
        "Blue only stop",
        "Isolated Line Stop A",
        "Isolated Line Stop B",
    ]
    assert result.loc[result["is_route"] == False, "link_count"].tolist() == [
        2,  # Kendall/MIT
        2,  # Harvard
        2,  # Park Street
        1,  # Blue only stop
        1,  # Isolated Line Stop A
        1,  # Isolated Line Stop B
    ]


def test_bfs_shortest_path_finds_route_between_nodes():
    subway_df = pd.DataFrame(
        [
            {
                "long_name": "Test Line",
                "is_route": True,
                "links": ["Stoppy"],
                "link_count": 1,
            },
            {
                "long_name": "Stoppy",
                "is_route": False,
                "links": ["Test Line"],
                "link_count": 1,
            },
        ]
    ).set_index("long_name")

    path = bfs_shortest_path(subway_df, "Test Line", "Stoppy")
    assert path == ["Test Line", "Stoppy"]


def test_bfs_shortest_path_returns_none_for_unreachable_nodes():
    subway_df = pd.DataFrame(
        [
            {
                "long_name": "Route A",
                "is_route": True,
                "links": ["A Stop"],
                "link_count": 1,
            },
            {
                "long_name": "A Stop",
                "is_route": False,
                "links": ["Route A"],
                "link_count": 1,
            },
            {
                "long_name": "Route B",
                "is_route": True,
                "links": ["B Stop"],
                "link_count": 1,
            },
            {
                "long_name": "B Stop",
                "is_route": False,
                "links": ["Route B"],
                "link_count": 1,
            },
        ]
    ).set_index("long_name")

    path = bfs_shortest_path(subway_df, "Route A", "B Stop")
    assert path is None


def test_bfs_shortest_path_raises_for_missing_node():
    subway_df = pd.DataFrame(
        [
            {
                "id": "stoppy-id",
                "long_name": "Stoppy",
                "is_route": False,
                "links": [],
                "link_count": 0,
            }
        ]
    ).set_index("long_name")

    try:
        bfs_shortest_path(subway_df, "Stoppy", "Nonexistent")
        assert False, "Expected ValueError for missing node"
    except ValueError as exc:
        assert "Ending stop 'Nonexistent' not found" in str(exc)
