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

    pattern = r"COLOUR_RGB\('',(\d+\.?\d*),(\d+\.?\d*),(\d+\.?\d*)\)"
    matches = re.findall(pattern, content)

    colors = [tuple(round(float(x), 6) for x in match) for match in matches]
    unique_colors = list(set(colors))

    # Return colors with hex conversion
    colors_with_hex = [
        {"rgb": color, "hex": rgb_to_hex(*color)} for color in unique_colors
    ]

    return colors_with_hex


def change_color(step_file, old_color, new_color, output_file):
    """Change a specific color in a STEP file.

    Args:
        step_file (str): Path to the input STEP file.
        old_color (tuple): RGB tuple to replace (0.0-1.0 range).
        new_color (tuple): RGB tuple for replacement (0.0-1.0 range).
        output_file (str): Path to the output STEP file.
    """
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


def change_all_colors(step_file, new_color, output_file):
    """Change all colors in a STEP file to a single color.

    Args:
        step_file (str): Path to the input STEP file.
        new_color (tuple): RGB tuple for all colors (0.0-1.0 range).
        output_file (str): Path to the output STEP file.
    """
    with open(step_file, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    pattern = r"(COLOUR_RGB\('',)(\d+\.?\d*),(\d+\.?\d*),(\d+\.?\d*)"
    replacement = f"\\g<1>{new_color[0]},{new_color[1]},{new_color[2]}"
    content = re.sub(pattern, replacement, content)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)


# Usage examples
if __name__ == "__main__":
    # Find all colors
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
            old_color=(0.286, 0.643, 0.867),
            new_color=(0.376, 0.596, 0.223),
            output_file=(
                "3D_models/terminal_blocks/"
                f"TJ{'{:02d}'.format(pincount)}31530000G.step"
            ),
        )

    # # Change all colors to green
    # change_all_colors(
    #     "TBP02P1-381-02BE.step",
    #     new_color=(0.0, 1.0, 0.0),
    #     output_file="output_green.step",
    # )
