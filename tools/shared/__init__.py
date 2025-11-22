"""
duckyPad Pro Helper Library

Shared utilities for duckyPad Pro profile generation and management.
"""

from .key_layout import (
    PHYSICAL_KEYS,
    TOTAL_KEYS,
    PORTRAIT_ROWS,
    PORTRAIT_COLS,
    LANDSCAPE_ROWS,
    LANDSCAPE_COLS,
    get_portrait_diagram,
    get_landscape_diagram,
    get_both_diagrams,
    print_portrait_layout,
    print_landscape_layout,
    print_both_layouts,
    validate_key_number,
    is_physical_key,
    is_rotary_encoder,
    get_key_description,
    parse_key_list,
    get_portrait_position,
    get_landscape_position,
)

from .profile_loader import (
    ProfileLoader,
    load_profile,
)

from .profile_info_manager import (
    ProfileInfoManager,
)

__all__ = [
    'PHYSICAL_KEYS',
    'TOTAL_KEYS',
    'PORTRAIT_ROWS',
    'PORTRAIT_COLS',
    'LANDSCAPE_ROWS',
    'LANDSCAPE_COLS',
    'get_portrait_diagram',
    'get_landscape_diagram',
    'get_both_diagrams',
    'print_portrait_layout',
    'print_landscape_layout',
    'print_both_layouts',
    'validate_key_number',
    'is_physical_key',
    'is_rotary_encoder',
    'get_key_description',
    'parse_key_list',
    'get_portrait_position',
    'get_landscape_position',
    'ProfileLoader',
    'load_profile',
    'ProfileInfoManager',
]
