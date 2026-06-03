"""Mock data for MBTA API responses."""

from typing import Any

stops_response_RedLine = {
    "data": [
        {
            "id": "place-mit",
            "type": "stop",
            "attributes": {
                "name": "Kendall/MIT",
            },
            "relationships": {},
        },
        {
            "id": "place-hrvrd",
            "type": "stop",
            "attributes": {
                "name": "Harvard",
            },
            "relationships": {},
        },
        {
            "id": "place-pktrm",
            "type": "stop",
            "attributes": {
                "name": "Park Street",
            },
            "relationships": {},
        },
    ],
    "jsonapi": {"version": "1.0"},
}

stops_response_BlueLine = {
    "data": [
        {
            "id": "place-mit",
            "type": "stop",
            "attributes": {
                "name": "Kendall/MIT",
            },
            "relationships": {},
        },
        {
            "id": "place-hrvrd",
            "type": "stop",
            "attributes": {
                "name": "Harvard",
            },
            "relationships": {},
        },
        {
            "id": "place-pktrm",
            "type": "stop",
            "attributes": {
                "name": "Park Street",
            },
            "relationships": {},
        },
        {
            "id": "blue-stop",
            "type": "stop",
            "attributes": {
                "name": "Blue only stop",
            },
            "relationships": {},
        },
    ],
    "jsonapi": {"version": "1.0"},
}

stops_response_IsolatedLine = {
    "data": [
        {
            "id": "isolated-a",
            "is_route": True,
            "attributes": {
                "name": "Isolated Line Stop A",
            },
            "relationships": {},
        },
        {
            "id": "isolated-b",
            "is_route": True,
            "attributes": {
                "name": "Isolated Line Stop B",
            },
            "relationships": {},
        },
    ],
    "jsonapi": {"version": "1.0"},
}

stops_response_StoplessLine = {
    "data": [],
    "jsonapi": {"version": "1.0"},
}

routes_response = {
    "data": [
        {
            "id": "Red",
            "type": "route",
            "attributes": {
                "color": "DA291C",
                "long_name": "Red Line",
                "type": 1,
            },
            "relationships": {},
        },
        {
            "id": "Blue",
            "type": "route",
            "attributes": {
                "color": "DA291C",
                "long_name": "Blue Line",
                "type": 1,
            },
            "relationships": {},
        },
        {
            "id": "stopless-line",
            "type": "route",
            "attributes": {
                "color": "DA291C",
                "long_name": "Stopless Line",
                "type": 1,
            },
            "relationships": {},
        },
        {
            "id": "isolated-line",
            "type": "route",
            "attributes": {
                "color": "DA291C",
                "long_name": "Isolated Line",
                "type": 1,
            },
            "relationships": {},
        },
    ],
    "jsonapi": {"version": "1.0"},
}


def mock_empty_mbta_response() -> dict[str, Any]:
    """Mock empty MBTA API response."""
    return {
        "data": [],
        "jsonapi": {"version": "1.0"},
    }


def mock_mbta_error_response(
    status_code: int = 429, message: str = "Too Many Requests"
) -> dict[str, Any]:
    """Mock MBTA API error response."""
    return {
        "errors": [
            {
                "status": str(status_code),
                "title": message,
                "detail": f"API Error: {message}",
            }
        ],
        "jsonapi": {"version": "1.0"},
    }
