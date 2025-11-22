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
python helpers/shared/key_layout.py
```

## Integration

This library is used by:
- `helpers/generators/profile_generator.py` - Basic profile generation
- `helpers/generators/modifier_layer_generator.py` - Modifier layer generation
- Other helper scripts

All scripts that need key layout information should use this centralized module instead of duplicating the layout definitions.
