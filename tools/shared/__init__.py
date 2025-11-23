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

from .yaml_loader import (
    ProfileLoader,
    load_profile,
)

from .profiles import (
    ProfileInfoManager,
)

from .console import (
    print_color,
    print_success,
    print_error,
    print_warning,
    print_info,
    print_verbose,
    prompt_yes_no,
)

from .validators import (
    ValidationError,
    validate_profile_name,
    validate_key_label,
    validate_profile_count,
    validate_label_list,
    require_valid_profile_name,
    require_valid_key_label,
    require_valid_profile_count,
    MAX_PROFILES,
    MAX_PROFILE_NAME_LENGTH,
    MAX_LABEL_CHARS_PORTRAIT,
    MAX_LABEL_CHARS_PER_LINE_PORTRAIT,
    MAX_LABEL_CHARS_LANDSCAPE,
    MAX_LABEL_CHARS_PER_LINE_LANDSCAPE,
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
    'print_color',
    'print_success',
    'print_error',
    'print_warning',
    'print_info',
    'print_verbose',
    'prompt_yes_no',
    'ValidationError',
    'validate_profile_name',
    'validate_key_label',
    'validate_profile_count',
    'validate_label_list',
    'require_valid_profile_name',
    'require_valid_key_label',
    'require_valid_profile_count',
    'MAX_PROFILES',
    'MAX_PROFILE_NAME_LENGTH',
    'MAX_LABEL_CHARS_PORTRAIT',
    'MAX_LABEL_CHARS_PER_LINE_PORTRAIT',
    'MAX_LABEL_CHARS_LANDSCAPE',
    'MAX_LABEL_CHARS_PER_LINE_LANDSCAPE',
]
