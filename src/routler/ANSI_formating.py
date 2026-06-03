import click
import pandas as pd


def hex_to_rgb(hex_color: str):
    """Not using this currently, keeping it in case the option to swap between
    standard 16 color ANSI, 256 color ANSI, and true color is added in the future."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def hex_to_ansi256(hex_color: str):
    """
    code is from:
        https://www.dev-toolbox.tech/tools/ansi-color-reference/examples/hex-to-ansi-conversion
    """
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    # Check grayscale
    if r == g == b:
        if r < 4:
            return 16
        if r > 248:
            return 231
        return round((r - 8) / 10) + 232

    # Map to 6x6x6 cube
    values = [0, 95, 135, 175, 215, 255]
    ri = min(range(6), key=lambda i: abs(values[i] - r))
    gi = min(range(6), key=lambda i: abs(values[i] - g))
    bi = min(range(6), key=lambda i: abs(values[i] - b))
    return 16 + (36 * ri) + (6 * gi) + bi


def format_route_names(
    routes_df: pd.DataFrame, route_names_list: list = None, route_arrows: bool = None
) -> str:
    """Adds ANSI color encoding to route names with colors from route dataframe.

    Args:
        routes_df: DataFrame containing route hex colors and names.
        route_names_list: Optional list of route names to format. If None, formats all route names in the DataFrame.
        route_arrows: Include "-->" after route names in output. Defaults to False
    Returns:
        Formatted string with color-encoded route names.
    """
    color_encoded_names = []
    if not route_names_list:
        route_names_list = routes_df.index.tolist()

    for route_name in route_names_list:
        if route_name in routes_df.index:
            route_name_fancy = route_name
            if route_arrows: route_name_fancy +="-->"
            color_encoded_names.append(
                click.style(
                    route_name_fancy, fg=hex_to_ansi256(routes_df.loc[route_name]["color"])
                )
            )
        else:
            color_encoded_names.append(route_name)

    return f"\t{(", ".join(color_encoded_names))}"
