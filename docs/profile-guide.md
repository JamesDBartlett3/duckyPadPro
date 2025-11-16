# Creating duckyPad Pro Profiles

This guide explains how to create custom profiles for your duckyPad Pro device.

## Profile Structure

A complete profile consists of:

```
my-profile/
├── config.txt       # Profile configuration
├── key1.txt         # Script for key 1
├── key2.txt         # Script for key 2
├── ...
├── keyN.txt         # Script for key N
└── README.md        # Profile documentation
```

## Configuration File (config.txt)

The `config.txt` file defines profile settings:

```
PROFILE_NAME My Profile Name
BG_COLOR 100 150 200
DIM_UNUSED_KEYS 1
```

### Configuration Options

- `PROFILE_NAME`: Display name for the profile
- `BG_COLOR`: RGB color values (0-255)
- `DIM_UNUSED_KEYS`: Whether to dim unused keys (0 or 1)

### Key Label Constraints

**Important:** Key labels displayed on the duckyPad Pro screen have strict size limits:
- **Maximum 2 lines** of text per key
- **Maximum 5 characters** per line (ASCII only)
- Total: 10 characters maximum per key label

Examples of valid key labels:
```
COPY     (1 line, 4 chars)

CTRL      (2 lines, 4 chars + 1 char)
C

MENUS     (2 lines, 5 chars each - maximum)
OPEN
```

## Key Scripts

Each key file contains duckyScript commands:

```
REM Description of what this key does
REM Author: Your Name
REM Date: 2025-01-01

COMMAND SPACE
DELAY 500
STRING terminal
ENTER
```

### Best Practices

1. **Add comments**: Use `REM` to document what the script does
2. **Include delays**: Add appropriate delays between commands
3. **Test thoroughly**: Verify scripts work on your target system
4. **Document platform**: Note if scripts are OS-specific

## duckyScript Commands

### Basic Commands

- `STRING`: Type text
- `ENTER`: Press Enter key
- `DELAY`: Wait in milliseconds
- `REM`: Comment (not executed)

### Modifier Keys

- `CONTROL`: Ctrl key
- `SHIFT`: Shift key
- `ALT`: Alt key
- `COMMAND`: macOS Command key
- `WINDOWS` or `GUI`: Windows key

### Special Keys

- `ESCAPE`: ESC key
- `TAB`: Tab key
- `SPACE`: Space bar
- `BACKSPACE`: Backspace
- `DELETE`: Delete key
- `ENTER`: Enter/Return
- `UP`, `DOWN`, `LEFT`, `RIGHT`: Arrow keys
- `F1` through `F12`: Function keys

### Example Scripts

**Open Application:**
```
COMMAND SPACE
DELAY 500
STRING application name
DELAY 200
ENTER
```

**Type Text:**
```
STRING Hello, World!
ENTER
```

**Keyboard Shortcut:**
```
CONTROL SHIFT T
```

**Multi-line Text:**
```
STRING First line
ENTER
DELAY 100
STRING Second line
ENTER
```

## Profile Organization

### Single-Purpose Profiles

Create profiles focused on specific tasks:
- Development environment
- Media controls
- System administration
- Productivity tools

### Multi-Purpose Profiles

Organize keys by category:
- Keys 1-4: Application launchers
- Keys 5-8: Text snippets
- Keys 9-12: System controls

## Testing Your Profile

1. **Create** the profile structure locally
2. **Test** individual key scripts
3. **Adjust** delays and commands as needed
4. **Copy** to your duckyPad Pro device
5. **Verify** all keys work as expected

## Using the Profile Generator

Quick-start with the helper tool:

```bash
cd helpers/generators
python profile_generator.py my-profile 8
```

This creates a basic profile structure with 8 keys that you can customize.

## Tips for Success

### Timing is Everything

- Start with longer delays (500-1000ms)
- Reduce delays after testing
- Some applications need more time to launch

### Platform Considerations

- Test on your target operating system
- Document platform-specific requirements
- Consider creating platform-specific versions

### Key Naming

Use descriptive key file names when possible:
- `key1.txt` (standard)
- `launch-browser.txt` (descriptive, if supported)

## Examples

Check the `profiles/` directory for complete examples:
- `example-productivity`: Basic productivity profile
- More examples coming soon!

## Resources

- [duckyScript Documentation](https://dekunukem.github.io/duckyPad-Pro/doc/duckyscript_info.html)
- [duckyPad Pro User Guide](https://dekunukem.github.io/duckyPad-Pro/doc/getting_started.html)
