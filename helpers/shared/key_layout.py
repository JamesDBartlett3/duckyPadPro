#!/usr/bin/env python3
"""
duckyPad Pro Key Layout Definitions

Centralized key layout information for duckyPad Pro device.
Provides constants, diagrams, and utilities for both portrait and landscape orientations.

Author: duckyPad Pro Community
Date: 2025-11-16
"""

# Key layout constants
PHYSICAL_KEYS = 20  # Physical keys in grid
TOTAL_KEYS = 26     # Including rotary encoders
PORTRAIT_ROWS = 4
PORTRAIT_COLS = 5
LANDSCAPE_ROWS = 5
LANDSCAPE_COLS = 4


def get_portrait_diagram():
    """
    Get ASCII diagram of portrait key layout.
    
    Returns:
        String containing the portrait layout diagram
    """
    return """
PORTRAIT ORIENTATION (4 wide × 5 tall):
┌────────────────────────┐
│  1   2   3   4   [22↶] │  21: First encoder CW ↷
│                  [23⊙] │  22: First encoder CCW ↶
│  5   6   7   8   [21↷] │  23: First encoder press ⊙
│                        │
│  9  10  11  12   [25↶] │  24: Second encoder CW ↷
│                  [26⊙] │  25: Second encoder CCW ↶
│ 13  14  15  16   [24↷] │  26: Second encoder press ⊙
│                        │
│ 17  18  19  20         │
└────────────────────────┘
Rotary encoders on RIGHT side
"""


def get_landscape_diagram():
    """
    Get ASCII diagram of landscape key layout.
    
    Returns:
        String containing the landscape layout diagram
    """
    return """
LANDSCAPE ORIENTATION (5 wide × 4 tall, rotated 90° CCW):
┌────────────────────────────────────┐
│ [22↶][23⊙][21↷]  [25↶][26⊙][24↷]   │  21: First encoder CW ↷
│                                    │  22: First encoder CCW ↶
│  4   8  12  16  20                 │  23: First encoder press ⊙
│  3   7  11  15  19                 │
│  2   6  10  14  18                 │  24: Second encoder CW ↷
│  1   5   9  13  17                 │  25: Second encoder CCW ↶
└────────────────────────────────────┘  26: Second encoder press ⊙
Rotary encoders on TOP
Key numbers unchanged, but physical layout rotated
"""


def get_both_diagrams():
    """
    Get both orientation diagrams.
    
    Returns:
        String containing both portrait and landscape diagrams
    """
    return get_portrait_diagram() + "\n" + get_landscape_diagram()


def print_portrait_layout():
    """Display portrait key layout to console."""
    print(get_portrait_diagram())


def print_landscape_layout():
    """Display landscape key layout to console."""
    print(get_landscape_diagram())


def print_both_layouts():
    """Display both orientation diagrams to console."""
    print(get_both_diagrams())


def validate_key_number(key_num):
    """
    Validate key number is in valid range.
    
    Args:
        key_num: Key number to validate (1-26)
    
    Returns:
        int: The validated key number
    
    Raises:
        ValueError: If key number is out of range
    """
    if not isinstance(key_num, int):
        raise TypeError(f"Key number must be an integer, got {type(key_num)}")
    
    if not 1 <= key_num <= TOTAL_KEYS:
        raise ValueError(f"Key number must be between 1 and {TOTAL_KEYS}, got {key_num}")
    
    return key_num


def is_physical_key(key_num):
    """
    Check if key number is a physical grid key (not rotary encoder).
    
    Args:
        key_num: Key number (1-26)
    
    Returns:
        bool: True if physical key, False if rotary encoder
    """
    validate_key_number(key_num)
    return key_num <= PHYSICAL_KEYS


def is_rotary_encoder(key_num):
    """
    Check if key number is a rotary encoder input.
    
    Args:
        key_num: Key number (1-26)
    
    Returns:
        bool: True if rotary encoder, False if physical key
    """
    validate_key_number(key_num)
    return key_num > PHYSICAL_KEYS


def get_key_description(key_num):
    """
    Get human-readable description of key.
    
    Args:
        key_num: Key number (1-26)
    
    Returns:
        str: Description of the key
    """
    validate_key_number(key_num)
    
    if key_num <= PHYSICAL_KEYS:
        return f"Key {key_num}"
    
    encoder_descriptions = {
        21: "First rotary encoder - Clockwise rotation",
        22: "First rotary encoder - Counter-clockwise rotation",
        23: "First rotary encoder - Press",
        24: "Second rotary encoder - Clockwise rotation",
        25: "Second rotary encoder - Counter-clockwise rotation",
        26: "Second rotary encoder - Press"
    }
    
    return encoder_descriptions[key_num]


def parse_key_list(key_string):
    """
    Parse comma-separated key numbers with range support.
    
    Supports:
    - Single keys: "1"
    - Multiple keys: "1,6,8,10"
    - Ranges: "1-5" or "1-5,10-15"
    - Mixed: "1,3-5,8,10-12"
    
    Args:
        key_string: String containing key numbers
    
    Returns:
        list: Sorted list of unique validated key numbers
    
    Raises:
        ValueError: If key string format is invalid or keys out of range
    """
    if not key_string:
        return []
    
    keys = []
    parts = key_string.split(',')
    
    for part in parts:
        part = part.strip()
        if '-' in part:
            # Range like "1-5"
            range_parts = part.split('-')
            if len(range_parts) != 2:
                raise ValueError(f"Invalid range format: {part}")
            
            try:
                start = int(range_parts[0])
                end = int(range_parts[1])
            except ValueError:
                raise ValueError(f"Invalid range numbers: {part}")
            
            if start > end:
                raise ValueError(f"Range start must be <= end: {part}")
            
            keys.extend(range(start, end + 1))
        else:
            # Single key
            try:
                keys.append(int(part))
            except ValueError:
                raise ValueError(f"Invalid key number: {part}")
    
    # Validate and deduplicate
    validated = sorted(set(validate_key_number(k) for k in keys))
    return validated


def get_portrait_position(key_num):
    """
    Get row and column position for portrait orientation.
    
    Args:
        key_num: Physical key number (1-20)
    
    Returns:
        tuple: (row, col) where row is 0-3 and col is 0-4
    
    Raises:
        ValueError: If key is not a physical key (>20)
    """
    if not is_physical_key(key_num):
        raise ValueError(f"Key {key_num} is not a physical grid key")
    
    # Keys are numbered left-to-right, top-to-bottom in portrait
    index = key_num - 1
    row = index // PORTRAIT_COLS
    col = index % PORTRAIT_COLS
    return (row, col)


def get_landscape_position(key_num):
    """
    Get row and column position for landscape orientation.
    
    Note: Physical layout rotates 90° CCW but key numbers stay the same.
    
    Args:
        key_num: Physical key number (1-20)
    
    Returns:
        tuple: (row, col) where row is 0-4 and col is 0-3
    
    Raises:
        ValueError: If key is not a physical key (>20)
    """
    if not is_physical_key(key_num):
        raise ValueError(f"Key {key_num} is not a physical grid key")
    
    # Get portrait position first
    portrait_row, portrait_col = get_portrait_position(key_num)
    
    # Rotate 90° CCW: (row, col) -> (4-col, row)
    landscape_row = (PORTRAIT_COLS - 1) - portrait_col
    landscape_col = portrait_row
    
    return (landscape_row, landscape_col)


if __name__ == '__main__':
    # Demo when run directly
    print("duckyPad Pro Key Layout Information")
    print("=" * 50)
    print_both_layouts()
    
    print("\nKey Descriptions:")
    print("-" * 50)
    for i in range(1, TOTAL_KEYS + 1):
        print(f"{i:2d}: {get_key_description(i)}")
    
    print("\nExample: Parse key list '1,3-5,8,10-12'")
    print("-" * 50)
    keys = parse_key_list("1,3-5,8,10-12")
    print(f"Parsed keys: {keys}")
    
    print("\nExample: Key positions")
    print("-" * 50)
    for key in [1, 5, 6, 10, 16, 20]:
        p_pos = get_portrait_position(key)
        l_pos = get_landscape_position(key)
        print(f"Key {key:2d}: Portrait row={p_pos[0]} col={p_pos[1]}, "
              f"Landscape row={l_pos[0]} col={l_pos[1]}")
