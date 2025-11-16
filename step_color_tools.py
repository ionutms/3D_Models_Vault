"""Tools for finding and changing colors in STEP files."""

import re


def rgb_to_hex(r, g, b):
    """Convert RGB values (0.0-1.0) to hex color code.

    Args:
        r (float): Red component (0.0-1.0).
        g (float): Green component (0.0-1.0).
        b (float): Blue component (0.0-1.0).

    Returns:
        str: Hex color code (e.g., '#ff0000').
    """
    return "#{:02x}{:02x}{:02x}".format(
        int(r * 255), int(g * 255), int(b * 255)
    )


def find_colors(step_file):
    """Find all unique colors in a STEP file.

    Args:
        step_file (str): Path to the STEP file.

    Returns:
        list: List of dictionaries with 'rgb' tuple and 'hex' string.
    """
    with open(step_file, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    rgb_pattern = r"COLOUR_RGB\('',(\d+\.?\d*),(\d+\.?\d*),(\d+\.?\d*)\)"
    rgb_matches = re.findall(rgb_pattern, content)

    predef_pattern = r"DRAUGHTING_PRE_DEFINED_COLOUR\('(\w+)'\)"
    predef_matches = re.findall(predef_pattern, content)

    colors = [
        tuple(round(float(x), 6) for x in match) for match in rgb_matches
    ]

    predef_rgb = {
        "white": (1.0, 1.0, 1.0),
        "black": (0.0, 0.0, 0.0),
        "red": (1.0, 0.0, 0.0),
        "green": (0.0, 1.0, 0.0),
        "blue": (0.0, 0.0, 1.0),
        "yellow": (1.0, 1.0, 0.0),
        "magenta": (1.0, 0.0, 1.0),
        "cyan": (0.0, 1.0, 1.0),
    }
    for color_name in predef_matches:
        if color_name.lower() in predef_rgb:
            colors.append(predef_rgb[color_name.lower()])

    unique_colors = list(set(colors))

    colors_with_hex = [
        {"rgb": color, "hex": rgb_to_hex(*color)} for color in unique_colors
    ]

    return colors_with_hex


def hex_to_rgb(hex_color):
    """Convert hex color code to RGB values (0.0-1.0).

    Args:
        hex_color (str): Hex color code (e.g., '#ff0000' or 'ff0000').

    Returns:
        tuple: RGB values as floats (0.0-1.0).
    """
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4))


def change_color(step_file, old_color, new_color, output_file):
    """Change a specific color in a STEP file.

    Args:
        step_file (str): Path to the input STEP file.
        old_color (tuple or str):
            RGB tuple to replace (0.0-1.0 range) or hex string
            (e.g., '#ff0000').
        new_color (tuple or str):
            RGB tuple (0.0-1.0 range) or hex string
            (e.g., '#ff0000').
        output_file (str): Path to the output STEP file.
    """
    # Convert hex to RGB if needed
    if isinstance(old_color, str):
        old_color = hex_to_rgb(old_color)
    if isinstance(new_color, str):
        new_color = hex_to_rgb(new_color)

    with open(step_file, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    pattern = r"COLOUR_RGB\('',(\d+\.?\d*),(\d+\.?\d*),(\d+\.?\d*)\)"

    def replace_match(match):
        r, g, b = (
            float(match.group(1)),
            float(match.group(2)),
            float(match.group(3)),
        )
        if (
            abs(r - old_color[0]) < 0.01
            and abs(g - old_color[1]) < 0.01
            and abs(b - old_color[2]) < 0.01
        ):
            return (
                f"COLOUR_RGB('',{new_color[0]},{new_color[1]},{new_color[2]})"
            )
        return match.group(0)

    content = re.sub(pattern, replace_match, content)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    colors = find_colors("3D_models/terminal_blocks/TBP02P1-381-02BE.step")
    print("Found colors:")
    for color_info in colors:
        print(f"  RGB: {color_info['rgb']} -> Hex: {color_info['hex']}")

    excluded_pincounts = {11, 13, 14, 15}
    for pincount in [
        pincount
        for pincount in range(2, 25)
        if pincount not in excluded_pincounts
    ]:
        change_color(
            "3D_models/terminal_blocks/"
            f"TBP02P1-381-{'{:02d}'.format(pincount)}BE.step",
            old_color="#49a3dd",
            new_color="#609939",
            output_file=(
                "3D_models/terminal_blocks/"
                f"TJ{'{:02d}'.format(pincount)}31530000G.step"
            ),
        )

    excluded_pincounts = {11, 13, 14, 15}
    for pincount in [
        pincount
        for pincount in range(2, 16)
        if pincount not in excluded_pincounts
    ]:
        change_color(
            "3D_models/connectors/"
            f"CUI_DEVICES_TBP02R2-381-{'{:02d}'.format(pincount)}BE.step",
            old_color="#49a3dd",
            new_color="#609939",
            output_file=(
                "3D_models/connectors/"
                f"OQ{'{:02d}'.format(pincount)}32500000G.step"
            ),
        )
