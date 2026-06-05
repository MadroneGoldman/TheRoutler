import click
import asyncio
from rapidfuzz import process
import pandas as pd

from .subway_services import get_subway_routes, get_routes_and_stops, bfs_shortest_path
from .ANSI_formating import format_route_names

ascii_title = r"""
 _____ _              __             _   _           
/__   \ |__   ___    /__\ ___  _   _| |_| | ___ _ __ 
  / /\/ '_ \ / _ \  / \/// _ \| | | | __| |/ _ \ '__|
 / /  | | | |  __/ / _  \ (_) | |_| | |_| |  __/ |   
 \/   |_| |_|\___| \/ \_/\___/ \__,_|\__|_|\___|_|   
                                                     
    """

class RoutlerHelpGroup(click.Group):
    """Custom Click Group that can handle ASCII art in help output without broken formating."""

    def format_help(self, ctx, formatter):
        # Add colored ASCII art at the top
        colored_ascii = click.style(ascii_title, fg="bright_green", bold=True)
        formatter.write(colored_ascii + "\n")
        super().format_help(ctx, formatter)


@click.command(
    cls=RoutlerHelpGroup,
    help="Madrone's CLI tool for the AgZen take home challenge.",
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
    cls=RoutlerHelpGroup,
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
    cls=RoutlerHelpGroup,
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
    cls=RoutlerHelpGroup,
    short_help="Finds route between two stops",
    epilog="\b\b\bExample:\nuv run routler question-three Ashmont Arlington"
    "\n\nstops names that are multiple words with spaces should be surrounded by quotes:"
    '\n\nuv run routler question-three Ashmont "Science Park/West End"',
)
@click.argument("first_stop")
@click.argument("second_stop")
def question_three(first_stop: str, second_stop: str) -> None:
    """Given two stops; lists a rail route you could travel from one stop to the other."""

    subway_df = asyncio.run(get_routes_and_stops())

    # Run a fuzzy search on input stops and raise an error if no existing stops match
    fuzz_cutoff_score = 65
    if first_stop not in subway_df.index:
        start_best_match = process.extractOne(
            first_stop, subway_df.index, score_cutoff=fuzz_cutoff_score
        )
        if start_best_match:
            click.echo(f"best match for input: {first_stop} is {start_best_match[0]}\n")
            first_stop = start_best_match[0]
        else:
            raise ValueError(f"Starting stop '{first_stop}' not found")
    if second_stop not in subway_df.index:
        goal_best_match = process.extractOne(
            second_stop, subway_df.index, score_cutoff=fuzz_cutoff_score
        )
        if goal_best_match:
            click.echo(f"best match for input: {second_stop} is {goal_best_match[0]}\n")
            second_stop = goal_best_match[0]
        else:
            raise ValueError(f"Ending stop '{second_stop}' not found")

    # Use a breadth first search to find a path from the sirst stop to the second
    path = bfs_shortest_path(subway_df, first_stop, second_stop)

    click.echo(
        f"Path from {first_stop} to {second_stop}:\n{format_route_names(subway_df[subway_df['is_route'] == True], path, route_arrows=True)}"
    )


def main() -> None:
    """Main CLI entry point."""
    try:
        cli()

    # this is a question-three specific error because it's the only command with arguments
    except click.UsageError as e:
        click.echo(
            "Usage: routler question-three [OPTIONS] FIRST_STOP SECOND_STOP"
            "\nTry 'routler question-three --help' for help."
        )
        click.echo(f"Error: {e}", err=True)
    except (ValueError, RuntimeError, ConnectionError) as e:
        click.echo(f"Error: {e}", err=True)


if __name__ == "__main__":
    main()
