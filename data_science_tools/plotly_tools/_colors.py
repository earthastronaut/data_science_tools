""" Convert plotly compadible formats.

Plotly requires a string 'rgba(1, 1, 1, 1)' for color.
"""
__all__ = [
    "format_color",
    "format_colors",
]

WEB_COLORS = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "lime": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "cyan": (0, 255, 255),
    "aqua": (0, 255, 255),
    "magenta": (55, 0, 255),
    "fuchsia": (55, 0, 255),
    "silver": (192, 192, 192),
    "gray": (128, 128, 128),
    "maroon": (128, 0, 0),
    "olive": (128, 128, 0),
    "green": (0, 128, 0),
    "purple": (128, 0, 128),
    "teal": (0, 128, 128),
    "navy": (0, 0, 128),
}
COLOR_FORMAT_WEB = "web"
COLOR_FORMAT_HEX = "hex"
COLOR_FORMAT_RGB = "rgb"
COLOR_FORMAT_RGBA = "rgba"
COLOR_FORMAT_RGB_STR = "rgb()"
COLOR_FORMAT_RGBA_STR = "rgba()"
COLOR_FORMATS = {
    COLOR_FORMAT_WEB: "web standard names, e.g. 'red'",
    COLOR_FORMAT_HEX: "hex format, e.g. '#000000'",
    COLOR_FORMAT_RGB: "rgb tuple, e.g. (0, 0, 0)",
    COLOR_FORMAT_RGBA: "rgba tuple, e.g. (0, 0, 0, 0.5)",
    COLOR_FORMAT_RGB_STR: "rgb string 'rgb(0, 0, 0)'",
    COLOR_FORMAT_RGBA_STR: "rgba string 'rgba(0, 0, 0, 1)'",
}


def _detect_color_format(color):
    """Detect what format the color is."""
    if isinstance(color, str):
        if color.startswith("#"):
            return COLOR_FORMAT_HEX

        if color.startswith("rgba("):
            return COLOR_FORMAT_RGBA_STR

        if color.startswith("rgb("):
            return COLOR_FORMAT_RGB_STR

        if color.lower() in WEB_COLORS:
            return COLOR_FORMAT_WEB
    else:
        if len(color) == 3:
            return COLOR_FORMAT_RGB

        if len(color) == 4:
            return COLOR_FORMAT_RGBA

    raise TypeError(f"Unknown color '{color}'")


def _rgba_to_hex(rgba):
    red, green, blue, alpha = rgba
    return "{:02x}{:02x}{:02x}{:02x}".format(red, green, blue, alpha * 100)


def _hex_to_rgba(value):
    value = value.lstrip("#")
    hex_total_length = len(value)
    rgb_section_length = hex_total_length // 3
    return tuple(
        int(value[i : i + rgb_section_length], 16)  # noqa
        for i in range(0, hex_total_length, rgb_section_length)
    )


def _color_to_rgba(  # pylint: disable=too-many-return-statements
    color, alpha=None, input_format=None
):
    """Convert color to an RGBA tuple"""
    if input_format is None:
        input_format = _detect_color_format(color)

    if input_format == COLOR_FORMAT_WEB:
        return WEB_COLORS[color.lower()] + (alpha or 1,)

    if input_format == COLOR_FORMAT_HEX:
        components = _hex_to_rgba(color)
        if len(components) == 3:
            red, green, blue = components
            return (red, green, blue, alpha or 1)
        else:
            red, green, blue, _alpha = components
            return (red, green, blue, alpha or (_alpha / 100))

    if input_format == COLOR_FORMAT_RGB:
        red, green, blue = color
        return (red, green, blue, alpha or 1)

    if input_format == COLOR_FORMAT_RGBA:
        red, green, blue, _alpha = color
        return (red, green, blue, alpha or _alpha)

    if input_format == COLOR_FORMAT_RGB_STR:
        i = len("rgb") + 1
        color_components = color[i:-1]
        red, green, blue = color_components.split(",")
        red = int(red)
        green = int(green)
        blue = int(blue)
        return (red, green, blue, alpha or 1)

    if input_format == COLOR_FORMAT_RGBA_STR:
        i = len("rgba") + 1
        color_components = color[i:-1]
        red, green, blue, _alpha = color_components.split(",")
        red = int(red)
        green = int(green)
        blue = int(blue)
        _alpha = float(_alpha)
        return (red, green, blue, alpha or _alpha)

    raise ValueError(f"Color format {input_format} not in {tuple(COLOR_FORMATS)}")


def _rgba_to_color(color_rgba, output_format="rgba()"):
    """Convert rgba to color."""
    if output_format == COLOR_FORMAT_HEX:
        return _rgba_to_hex(color_rgba)

    if output_format == COLOR_FORMAT_RGB:
        return color_rgba[:3]

    if output_format == COLOR_FORMAT_RGBA:
        return color_rgba

    if output_format == COLOR_FORMAT_RGB_STR:
        return "rgb({:g},{:g},{:g})".format(*color_rgba[:3])

    if output_format == COLOR_FORMAT_RGBA_STR:
        return "rgba({:g},{:g},{:g},{:g})".format(*color_rgba)

    raise ValueError(f"Color format {output_format} not in {tuple(COLOR_FORMATS)}")


def format_color(
    color,
    alpha=None,
    input_format=None,
    output_format="rgba()",
):
    """Standardize input color format.

    Parameters
    ----------
    color (str | Tuple[int]): The color to convert
    alpha (float): Opacity of the color, defaults to 1 or inferrence from color
    input_format (str): Input format of the color, will be detected if None.
        See options below.
    output_format (str): Output format of the color. See options below.

    Returns
    -------
    str | tuple: Depending on the output format desired.

    Color Formats
    -------------
    hex: (str) hex format, e.g. '#000000'
    web: (str) web standard names, e.g. 'red'
    rgb: (tuple) rgb tuple, e.g. (0, 0, 0)
    rgba: (tuple) rgba tuple, e.g. (0, 0, 0, 0.5)
    rgb(): (str) rgb string 'rgb(0, 0, 0)'
    rgba(): (str) rgba string 'rgba(0, 0, 0, 1)'
    """
    return _rgba_to_color(
        _color_to_rgba(color, alpha=alpha, input_format=input_format),
        output_format=output_format,
    )


def format_colors(
    colors,
    alpha=None,
    input_format=None,
    output_format="rgba()",
):
    """Standardize input color format.

    Parameters
    ----------
    color (str | Tuple[int]): The color to convert
    alpha (float): Opacity of the color, defaults to 1 or inferrence from color
    input_format (str): Input format of the color, will be detected if None.
        See options below.
    output_format (str): Output format of the color. See options below.

    Returns
    -------
    generator[str | tuple]: all the same type depending on output_format.

    Color Formats
    -------------
    hex: (str) hex format, e.g. '#000000'
    web: (str) web standard names, e.g. 'red'
    rgb: (tuple) rgb tuple, e.g. (0, 0, 0)
    rgba: (tuple) rgba tuple, e.g. (0, 0, 0, 0.5)
    rgb(): (str) rgb string 'rgb(0, 0, 0)'
    rgba(): (str) rgba string 'rgba(0, 0, 0, 1)'
    """
    for color in colors:
        yield format_color(
            color,
            alpha=alpha,
            input_format=input_format,
            output_format=output_format,
        )
