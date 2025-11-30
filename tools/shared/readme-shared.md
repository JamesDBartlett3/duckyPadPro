# duckyPad Pro Helper Library

Shared Python utilities for duckyPad Pro profile generation and management.

## Modules

### `key_layout.py`

Centralized key layout information for duckyPad Pro device. Provides constants, diagrams, and utilities for both portrait and landscape orientations.

**Constants:**

- `PHYSICAL_KEYS = 20` - Physical keys in grid
- `TOTAL_KEYS = 26` - Including rotary encoders
- `PORTRAIT_ROWS = 4` - Rows in portrait mode
- `PORTRAIT_COLS = 5` - Columns in portrait mode
- `LANDSCAPE_ROWS = 5` - Rows in landscape mode
- `LANDSCAPE_COLS = 4` - Columns in landscape mode

**Functions:**

**Display Functions:**

- `get_portrait_diagram()` - Returns portrait layout diagram as string
- `get_landscape_diagram()` - Returns landscape layout diagram as string
- `get_both_diagrams()` - Returns both diagrams as string
- `print_portrait_layout()` - Prints portrait diagram to console
- `print_landscape_layout()` - Prints landscape diagram to console
- `print_both_layouts()` - Prints both diagrams to console

**Validation Functions:**

- `validate_key_number(key_num)` - Validates key number (1-26)
- `is_physical_key(key_num)` - True if physical key (1-20)
- `is_rotary_encoder(key_num)` - True if rotary encoder (21-26)

**Utility Functions:**

- `get_key_description(key_num)` - Returns human-readable key description
- `parse_key_list(key_string)` - Parses "1,3-5,8" into [1,3,4,5,8]
- `get_portrait_position(key_num)` - Returns (row, col) for portrait mode
- `get_landscape_position(key_num)` - Returns (row, col) for landscape mode

## Usage Examples

### Basic Import and Display

```python
from shared.key_layout import print_both_layouts

# Show key layouts
print_both_layouts()
```

### Parse Key Lists

```python
from shared.key_layout import parse_key_list

# Parse complex key specifications
keys = parse_key_list("1,3-5,8,10-12")
# Result: [1, 3, 4, 5, 8, 10, 11, 12]
```

### Key Descriptions

```python
from shared.key_layout import get_key_description

for i in range(1, 27):
    print(f"{i}: {get_key_description(i)}")
```

### Position Calculations

```python
from shared.key_layout import get_portrait_position, get_landscape_position

key = 10
p_row, p_col = get_portrait_position(key)
l_row, l_col = get_landscape_position(key)

print(f"Key {key}:")
print(f"  Portrait: row {p_row}, col {p_col}")
print(f"  Landscape: row {l_row}, col {l_col}")
```

### Use in Scripts

```python
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.key_layout import TOTAL_KEYS, parse_key_list, get_key_description

# Your script code here
```

## Testing

Run the module directly to see a demo:

```bash
python tools/shared/key_layout.py
```

### `profiles.py`

Manages SD card detection, profile_info.txt parsing, and compilation support.

**Classes:**

- `ProfileInfoManager` - Auto-detects SD card, parses profile_info.txt, resolves GOTO_PROFILE commands
- `KeySettings` - Holds per-key settings (allow_abort, dont_repeat) parsed from config.txt

**Functions:**

- `parse_key_settings(config_path)` - Parses `ab N` and `dr N` directives from config.txt, returns `Dict[int, KeySettings]`
- `make_script_preamble(key_settings)` - Generates preamble lines (`$_ALLOW_ABORT = 1`, `$_DONT_REPEAT = 1`) for script compilation

**ProfileInfoManager Methods:**

- `detect_sd_card()` - Auto-detect SD card on Windows/macOS/Linux
- `parse_profile_info(sd_card_path)` - Parse profile_info.txt to build name→index mapping
- `load_profile_mapping()` - Load profile mapping from detected SD card
- `get_profile_index(name)` - Get 0-based index for profile name
- `transform_goto_commands(script_content)` - Replace `GOTO_PROFILE Name` with `GOTO_PROFILE N` (1-based)

**Usage:**

```python
from shared.profiles import ProfileInfoManager, parse_key_settings, make_script_preamble

# Profile resolution
manager = ProfileInfoManager()
if manager.load_profile_mapping():
    content, warnings = manager.transform_goto_commands(script_content)

# Config.txt settings for compilation
from pathlib import Path
key_settings = parse_key_settings(Path("config.txt"))
if 1 in key_settings:
    preamble = make_script_preamble(key_settings[1])
    # preamble might be ["$_ALLOW_ABORT = 1"] if ab 1 is in config
```

### `validators.py`

Validation functions for profile names, key labels, and counts.

### `colors.py`

Color parsing utilities for YAML profiles. Converts color names, hex values, and RGB arrays to duckyPad-compatible RGB tuples.

**Functions:**

- `parse_color(value)` - Parse color from any format (name, hex, RGB array) → `(r, g, b)` tuple
- `format_rgb(color)` - Format RGB tuple as space-separated string for config.txt
- `normalize_color_name(name)` - Normalize color names (handles underscores, aliases)
- `get_available_colors()` - List all available CSS3 color names

**Supported Formats:**

- **Color names:** CSS3/HTML colors like `red`, `darkblue`, `coral`
- **Underscore variants:** `dark_blue`, `light_green` (converted to `darkblue`, `lightgreen`)
- **Hex colors:** `#FF5500` or `FF5500`
- **RGB arrays:** `[255, 0, 0]`

**Usage:**

```python
from shared.colors import parse_color, format_rgb

# Parse different color formats
rgb = parse_color('red')           # (255, 0, 0)
rgb = parse_color('darkblue')      # (0, 0, 139)
rgb = parse_color('dark_blue')     # (0, 0, 139)
rgb = parse_color('#FF5500')       # (255, 85, 0)
rgb = parse_color([100, 150, 200]) # (100, 150, 200)

# Format for config.txt
color_str = format_rgb(rgb)        # "255 0 0"
```

### `console.py`

Console output utilities with color support.

### `yaml_loader.py`

YAML profile loading and parsing utilities.

## Integration

This library is used by:

- `tools/compile.py` - Compilation with preamble injection and GOTO_PROFILE resolution
- `tools/deploy.py` - SD card detection and profile_info.txt management
- `tools/generate.py` - YAML to profile conversion

All scripts that need key layout, profile management, or validation should use these centralized modules.
