import click
import pandas as pd
from collections import deque
from .mbta_client import MBTAClient


async def get_subway_routes() -> pd.DataFrame:
    """
    Gets subway route data from the MBTA API
    and stores it in a dataframe.

    Returns:
        dataframe with the following columns for all subway routes:

        +-------------+----------+----------------+
        | Field       | Type     | Description    |
        +-------------+----------+----------------+
        | long_name   | str      | name of route  | dataframe index
        | id          | str      | MBTA api id    |
        | color       | str      | hex color code |
        +-------------+----------+----------------+
    """
    async with MBTAClient() as client:
        try:
            # get routes from client filtered by "subway" route types (0 and 1)
            routes_data = await client.get_routes(route_type="0,1")
            routes = routes_data.get("data", [])

            # flatten route "attribute" dict into root dict
            flattened = [
                {k: v for k, v in item.items() if k != "attributes"}
                | {k: v for k, v in item["attributes"].items()}
                for item in routes
            ]

            routes_df = pd.DataFrame(flattened, columns=["id", "color", "long_name"])
            routes_df.set_index("long_name", inplace=True)
            return routes_df

        except (ValueError, RuntimeError, ConnectionError) as e:
            click.echo(f"Error: {e}", err=True)
            click.echo("reraising from get_subway_routes")
            raise e

async def get_routes_and_stops() -> pd.DataFrame:
    """
    Gets subway route and stop data from the MBTA API
    and stores it in a dataframe.

    Returns:
        dataframe containing both routes and stops with the following columns:

        +-------------+----------+----------------------------------------------------+
        | Field       | Type     | Description                                        |
        +-------------+----------+----------------------------------------------------+
        | long_name   | str      | name of route/stop                                 | dataframe index
        | id          | str      | MBTA api id                                        |
        | color       | str      | hex color code in string (routes only)             |
        | is_route    | bool     | is element a route or stop                         |
        | links       | [str]    | for routes: list of stop names along route         |
        |             |          | for stops: list of route names that use this stop  |
        | link_count  | int      | length of links list                               |
        +-------------+----------+----------------------------------------------------+
    """
    async with MBTAClient() as client:
        try:
            routes_df = await get_subway_routes()
    
            # add new cols to df
            routes_df["is_route"] = True
            routes_df["links"] = [[] for _ in range(len(routes_df))]
            routes_df["link_count"] = 0

            stops_df = pd.DataFrame(
                columns=routes_df.columns,
                index=pd.Index([], name="long_name", dtype="object"),
            )

            # get all stops for our subway routes and store data
            for route_name, route in routes_df.iterrows():
                # get stops from client filtered by route id
                stops_data = await client.get_stops(route_id=route.id)
                stops = stops_data.get("data", [])

                # flatten route "attribute" dict into root dict
                stop_names = [item["attributes"]["name"] for item in stops]

                # set the list of stop names and its count as the routes links and link_count, respectively
                routes_df.at[route_name, "links"] = stop_names
                routes_df.at[route_name, "link_count"] = len(stop_names)

                # for each stop create or update existing row in datafram
                for stop in stop_names:
                    if stop in stops_df.index:
                        stops_df.at[stop, "links"].append(route_name)
                        stops_df.at[stop, "link_count"] += 1
                    else:
                        #                             {api_id, color, is_route, [links], link_count}
                        stops_df.loc[stop] = [None, "FFFFFF", False, [route_name], 1]

            subway_df = pd.concat(
                [routes_df, stops_df],
                ignore_index=False,
            )
            return subway_df

        except (ValueError, RuntimeError, ConnectionError) as e:
            click.echo(f"Error: {e}", err=True)
            raise e


def bfs_shortest_path(subway_df: pd.DataFrame, start: str, goal: str) -> list[str]:
    """Return the shortest path between two stops or routes in the subway graph.

    The subway dataframe is expected to contain rows for both routes and stops.
    Each row must have a "links" column with connected route or stop names.

    Args:
        subway_df: Dataframe containing subway routes and stops.
        start: Starting stop or route name.
        goal: Destination stop or route name.

    Returns:
        A list of names representing the shortest path, or None if no path exists.
    """

    # Validate input
    if start not in subway_df.index:
        raise ValueError(f"Starting stop '{start}' not found")
    if goal not in subway_df.index:
        raise ValueError(f"Ending stop '{goal}' not found")

    queue = deque([(start, [start])])
    visited = set([start])

    while queue:
        current_node, path = queue.popleft()

        if current_node == goal:
            return path

        for neighbor in subway_df.loc[current_node]["links"]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return None
