import click
import asyncio
import pandas as pd

from .subway_services import get_subway_routes, get_routes_and_stops, bfs_shortest_path
from .ANSI_formating import format_route_names


@click.group(
    help=f"{click.style("""Ｍａｄｒｏｎｅｓ\n\n             
    ＡｇＺｅｎ  Ｓｕｂｗａｙ－ＣＬＩ""",fg='bright_green')}",
    epilog=(f"""Examples:\n
        \nuv run routler question-one\n
        \nuv run routler question-two\n
        \nuv run routler question-three Ashmont Arlington\n
        """),
)
def cli():
    """Click command group entry point"""
    pass


@cli.command(
    short_help="List subway routes",
    epilog="\b\b\bExample:\tuv run routler question-one",
)
def question_one() -> None:
    """Retrieves MBTA subway routes and prints their names to the console."""
    routes_df = asyncio.run(get_subway_routes())

    if routes_df.any:
        click.echo("\n Subway routes:")
        click.echo(format_route_names(routes_df))


@cli.command(
    short_help="Get routes with most/least stops",
    epilog="\b\b\bExample:\tuv run routler question-two",
)
def question_two() -> None:
    """
    1. Prints he name of the subway route with the most stops and the count of its stops
    2. The name of the subway route with the fewest stops and the count of its stops
    3. A list of the stops that connect two or more subway routes and the route
        names for each of those stops
    """
    subway_df = asyncio.run(get_routes_and_stops())

    route_rows = subway_df.loc[subway_df["is_route"] == True]
    stop_rows = subway_df.loc[subway_df["is_route"] == False]

    # Find routes with most stops
    max_stops = route_rows["link_count"].max()
    most_stop_routes = route_rows[route_rows["link_count"] == max_stops]
    click.echo("\n The subway route/s with the most stops is:")
    click.echo(format_route_names(most_stop_routes))
    click.echo(f"\twith {max_stops} stops")

    # Find routes with fewest stops
    min_stops = route_rows["link_count"].min()
    fewest_stop_routes = route_rows[route_rows["link_count"] == min_stops]
    click.echo("\n The subway route/s with the least stops is:")
    click.echo(format_route_names(fewest_stop_routes))
    click.echo(f"\twith {min_stops} stops")

    # Get stops that connect two or more subway routes
    click.echo("\n Stops connecting two or more routes:")
    for stop_name, stop_row in stop_rows.iterrows():
        if stop_row.link_count > 1:
            click.echo(f"""\t{stop_name} connects {stop_row.link_count} routes:
                 \n\t{ format_route_names(route_rows, stop_row.links)} \n""")


@cli.command(
    short_help="Finds route between two stops",
    epilog="\b\b\bExample:\tuv run routler question-three Ashmont Arlington",
)
@click.argument("first_stop")
@click.argument("second_stop")
def question_three(first_stop: str, second_stop: str) -> None:
    """Given two stops; lists a rail route you could travel from one stop to the other."""

    subway_df = asyncio.run(get_routes_and_stops())

    # Use a breadth first search to find a path from the sirst stop to thw second
    path = bfs_shortest_path(subway_df, first_stop, second_stop)

    click.echo(
        f"Path from {first_stop} to {second_stop}:\n{format_route_names(subway_df[subway_df['is_route'] == True], path, route_arrows=True)}"
    )


def main() -> None:
    """Main CLI entry point."""
    try:
        cli()
    # TODO:: different behaviors for exception types
    except (ValueError, RuntimeError, ConnectionError) as e:
        click.echo(f"Error: {e}", err=True)


if __name__ == "__main__":
    main()
