"""
Color utilities for duckyPad Pro profile generation.

Converts color names (e.g., "red", "darkblue", "dark_blue") to RGB tuples.
Uses the webcolors library for CSS3/HTML color name support.
"""

from typing import List, Tuple, Union, Optional
import re

try:
    import webcolors
    HAS_WEBCOLORS = True
except ImportError:
    HAS_WEBCOLORS = False


# Custom color aliases for common variations
COLOR_ALIASES = {
    # Underscore variants (webcolors uses no separators)
    'dark_blue': 'darkblue',
    'dark_red': 'darkred',
    'dark_green': 'darkgreen',
    'dark_cyan': 'darkcyan',
    'dark_gray': 'darkgray',
    'dark_grey': 'darkgrey',
    'dark_magenta': 'darkmagenta',
    'dark_orange': 'darkorange',
    'dark_violet': 'darkviolet',
    'light_blue': 'lightblue',
    'light_green': 'lightgreen',
    'light_gray': 'lightgray',
    'light_grey': 'lightgrey',
    'light_cyan': 'lightcyan',
    'light_pink': 'lightpink',
    'light_yellow': 'lightyellow',
    'sky_blue': 'skyblue',
    'steel_blue': 'steelblue',
    'royal_blue': 'royalblue',
    'hot_pink': 'hotpink',
    'deep_pink': 'deeppink',
    'indian_red': 'indianred',
    'olive_drab': 'olivedrab',
    'sea_green': 'seagreen',
    'forest_green': 'forestgreen',
    'lime_green': 'limegreen',
    'lawn_green': 'lawngreen',
    'spring_green': 'springgreen',
    'medium_blue': 'mediumblue',
    'midnight_blue': 'midnightblue',
    'navy_blue': 'navy',
    'cadet_blue': 'cadetblue',
    'powder_blue': 'powderblue',
    'cornflower_blue': 'cornflowerblue',
    'dodger_blue': 'dodgerblue',
    'alice_blue': 'aliceblue',
    
    # Common shorthand aliases
    'dk_blue': 'darkblue',
    'lt_blue': 'lightblue',
    'dk_red': 'darkred',
    'dk_green': 'darkgreen',
    'lt_green': 'lightgreen',
    'dk_gray': 'darkgray',
    'lt_gray': 'lightgray',
    'dk_grey': 'darkgrey',
    'lt_grey': 'lightgrey',
}


def normalize_color_name(name: str) -> str:
    """
    Normalize a color name for lookup.
    
    - Converts to lowercase
    - Removes spaces, underscores, and hyphens
    - Checks for aliases
    
    Args:
        name: Color name to normalize
        
    Returns:
        Normalized color name suitable for webcolors lookup
    """
    # First check if it's an alias (before normalization)
    lower_name = name.lower().strip()
    if lower_name in COLOR_ALIASES:
        return COLOR_ALIASES[lower_name]
    
    # Remove separators and normalize
    normalized = re.sub(r'[\s_-]+', '', lower_name)
    return normalized


def parse_color(color_value: Union[str, List[int], Tuple[int, ...]]) -> Optional[Tuple[int, int, int]]:
    """
    Parse a color value from YAML into an RGB tuple.
    
    Supports:
    - RGB list/tuple: [255, 0, 0] or (255, 0, 0)
    - Color name string: "red", "darkblue", "dark_blue"
    - Hex string: "#FF0000" or "FF0000"
    
    Args:
        color_value: Color value from YAML (string, list, or tuple)
        
    Returns:
        Tuple of (r, g, b) integers (0-255), or None if parsing fails
        
    Raises:
        ValueError: If the color format is invalid or color name not found
    """
    if color_value is None:
        return None
    
    # Already an RGB list/tuple
    if isinstance(color_value, (list, tuple)):
        if len(color_value) != 3:
            raise ValueError(f"RGB color must have exactly 3 values, got {len(color_value)}: {color_value}")
        r, g, b = color_value
        # Validate range
        for i, val in enumerate(['red', 'green', 'blue']):
            v = color_value[i]
            if not isinstance(v, int) or v < 0 or v > 255:
                raise ValueError(f"RGB {val} value must be integer 0-255, got: {v}")
        return (int(r), int(g), int(b))
    
    # String value - could be color name or hex
    if isinstance(color_value, str):
        color_str = color_value.strip()
        
        # Try hex format first
        if color_str.startswith('#') or re.match(r'^[0-9a-fA-F]{6}$', color_str):
            hex_str = color_str.lstrip('#')
            if len(hex_str) != 6:
                raise ValueError(f"Invalid hex color format: {color_value}")
            try:
                r = int(hex_str[0:2], 16)
                g = int(hex_str[2:4], 16)
                b = int(hex_str[4:6], 16)
                return (r, g, b)
            except ValueError:
                raise ValueError(f"Invalid hex color: {color_value}")
        
        # Try as color name
        if not HAS_WEBCOLORS:
            raise ValueError(
                f"Color name '{color_value}' requires the webcolors library. "
                "Install it with: pip install webcolors"
            )
        
        normalized = normalize_color_name(color_str)
        try:
            # webcolors.name_to_hex returns '#rrggbb'
            hex_value = webcolors.name_to_hex(normalized)
            r = int(hex_value[1:3], 16)
            g = int(hex_value[3:5], 16)
            b = int(hex_value[5:7], 16)
            return (r, g, b)
        except (ValueError, AttributeError):
            raise ValueError(
                f"Unknown color name: '{color_value}'. "
                "Use CSS3 color names (e.g., 'red', 'darkblue', 'coral') "
                "or RGB values [r, g, b]."
            )
    
    raise ValueError(f"Invalid color format: {color_value} (type: {type(color_value).__name__})")


def format_rgb(color: Tuple[int, int, int]) -> str:
    """
    Format an RGB tuple as a space-separated string for duckyPad config.
    
    Args:
        color: RGB tuple (r, g, b)
        
    Returns:
        String like "255 0 0"
    """
    return f"{color[0]} {color[1]} {color[2]}"


def get_available_colors() -> List[str]:
    """
    Get a list of all available color names.
    
    Returns:
        List of color names that can be used
    """
    if not HAS_WEBCOLORS:
        return []
    
    # Get CSS3 color names
    colors = list(webcolors.CSS3_NAMES_TO_HEX.keys())
    colors.sort()
    return colors


# Common colors for quick reference
COMMON_COLORS = {
    'red': (255, 0, 0),
    'green': (0, 128, 0),
    'blue': (0, 0, 255),
    'yellow': (255, 255, 0),
    'cyan': (0, 255, 255),
    'magenta': (255, 0, 255),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'orange': (255, 165, 0),
    'purple': (128, 0, 128),
    'pink': (255, 192, 203),
    'gray': (128, 128, 128),
    'grey': (128, 128, 128),
    'lime': (0, 255, 0),
    'navy': (0, 0, 128),
    'teal': (0, 128, 128),
    'maroon': (128, 0, 0),
    'olive': (128, 128, 0),
    'aqua': (0, 255, 255),
    'silver': (192, 192, 192),
    'gold': (255, 215, 0),
    'coral': (255, 127, 80),
    'salmon': (250, 128, 114),
    'tomato': (255, 99, 71),
    'crimson': (220, 20, 60),
    'violet': (238, 130, 238),
    'indigo': (75, 0, 130),
}
