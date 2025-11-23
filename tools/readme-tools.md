# tools

Development tools for duckyPad Pro profile creation, compilation, and deployment.

## Core Tools

### compile.py

Compiles duckyScript source files (`.txt`) to bytecode (`.dsb`) for duckyPad Pro.

**Features:**

- Auto-downloads compiler dependencies from GitHub
- Compiles all profiles or specific profile
- Automatic GOTO_PROFILE name-to-index resolution
- Verbose output for debugging

**Usage:**

```bash
# Compile all profiles
python tools/compile.py

# Compile specific profile
python tools/compile.py -p profiles/example-productivity

# Verbose output
python tools/compile.py -v

# Disable profile name resolution
python tools/compile.py --no-resolve-profiles
```

### backup.py

Manages SD card backups and restoration. Backups are automatically created by deploy.py and stored in `~/.duckypad/backups/`.

**Features:**

- Create manual backups of SD card
- List available backups with timestamps
- Restore from specific or latest backup
- Auto-detects SD card location
- Excludes .dsb bytecode files from backups

**Usage:**

```bash
# Create backup
python tools/backup.py --backup

# List available backups
python tools/backup.py --list

# Restore from latest backup
python tools/backup.py --restore --latest

# Restore from specific backup
python tools/backup.py --restore backup_20251122_153000

# Skip confirmation
python tools/backup.py --restore --latest -f
```

### deploy.py

Deploys profiles to duckyPad Pro SD card with automatic backup and profile_info.txt management.

**Features:**

- Automatic SD card detection (Windows/macOS/Linux)
- Backs up SD card before deployment (uses backup.py)
- Creates profile\_<name> folders (no ordinal numbers)
- Updates profile_info.txt preserving existing order

**Usage:**

```bash
# Deploy single profile
python tools/deploy.py profiles/my-profile

# Deploy multiple profiles
python tools/deploy.py profiles/profile1 profiles/profile2

# Verbose output
python tools/deploy.py profiles/my-profile -v

# Skip confirmation
python tools/deploy.py profiles/my-profile -f
```

### generate_profile.py

Creates new profile structure from template.

**Features:**

- Generates config.txt with default settings
- Creates keyN.txt files with comments
- Includes helpful rotary encoder key descriptions
- Supports 1-26 keys

**Usage:**

```bash
# Create profile with 20 keys
python tools/generate_profile.py discord-tools 20

# Create profile with all 26 keys (includes rotary encoders)
python tools/generate_profile.py photo-editing 26
```

### generate.py

**THE ONLY script that reads YAML template files.** Converts YAML profile definitions (with templates, inheritance, and layers) into duckyScript profiles ready for compilation.

**Features:**

- Parses YAML templates with inheritance and layers
- Generates config.txt with all settings
- Creates keyN.txt files for each defined key
- Supports all layer types (modifier_hold, toggle, oneshot, momentary)
- Auto-generates README.md for each profile
- Handles template extension and key ranges

**Usage:**

```bash
# Generate profile from YAML
python tools/generate.py workbench/foxhole.yaml

# Specify output directory
python tools/generate.py workbench/test.yaml -o workbench/profiles/my-test

# Verbose output
python tools/generate.py workbench/foxhole.yaml -v
```

**YAML Template Features:**

- **Templates**: Reusable key definitions (e.g., `media_encoder` for volume controls)
- **Inheritance**: `extends: parent` or `extends: [template1, template2]`
- **Layers**: Multiple profiles linked by layer switchers
- **Ranges**: Define multiple keys: `6-10: [A, E, "1", "2", "3"]`
- **Configuration**: Orientation, colors, labels in one file

**Example YAML:**

```yaml
profile:
  name: MyProfile
  config:
    orientation: landscape
    background_color: [100, 100, 100]
  keys:
    1: { key: A, label: [A] }
    2: { key: SHIFT, hold: true, label: [Run] }
  layers:
    ctrl:
      name: MyProfile-Ctrl
      extends: parent
```

### convert_text.py

Converts plain text to duckyScript STRING commands.

**Usage:**

```bash
python tools/convert_text.py input.txt output.txt
```

## Directory Structure

```
tools/
├── compile.py              # duckyScript compiler
├── deploy.py               # Profile deployment manager
├── generate_profile.py     # Profile template generator
├── convert_text.py         # Text to duckyScript converter
├── vendor/                 # Auto-downloaded compiler dependencies (gitignored)
└── shared/                 # Shared library code
    ├── __init__.py
    ├── profiles.py              # SD card and profile_info.txt handling
    ├── yaml_loader.py           # Profile loading utilities
    └── key_layout.py            # Key layout constants and helpers
```

## Compilation Details

### Overview

duckyScript 3 files (`.txt`) must be compiled to bytecode (`.dsb`) before execution on duckyPad Pro. The compilation converts human-readable scripts into optimized 3-byte instruction sequences for the duckyPad Pro virtual machine.

### How It Works

1. **Auto-fetch Compiler**: Downloads latest compiler from [duckyPad-Configurator releases](https://github.com/duckyPad/duckyPad-Configurator/releases)
2. **Compile Scripts**: Processes all `.txt` files matching `key\d+(-release)?\.txt` pattern
3. **Name Resolution**: Automatically converts `GOTO_PROFILE ProfileName` to numeric indices
4. **Generate Bytecode**: Creates `.dsb` files in same directory as source files

### Requirements

- **Python 3**: Required to run compiler
- **Internet**: Needed for initial compiler download (cached in `tools/vendor/`)

### Bytecode Format

Compiled `.dsb` files contain:

- **3-byte instructions**: Fixed-length opcodes for duckyPad Pro VM
- **String table**: Zero-terminated strings at end of binary
- **Variables**: Up to 64 variables in VM memory

See [duckyScript Bytecode VM Documentation](https://dekunukem.github.io/duckyPad-Pro/doc/bytecode_vm.html) for details.

## Common Issues

### Compilation Errors

| Error                      | Cause                                 | Solution                                        |
| -------------------------- | ------------------------------------- | ----------------------------------------------- |
| `Python not found`         | Python 3 not installed or not in PATH | Install Python 3 and add to system PATH         |
| `Syntax error in line X`   | Invalid duckyScript syntax            | Check script syntax at specified line           |
| `Undefined variable $name` | Variable used before declaration      | Declare variable with `VAR $name = value` first |
| `Unknown command`          | Unsupported duckyScript command       | Verify command is supported in duckyScript 3    |
| `Missing ENDIF/ENDWHILE`   | Unclosed control structure            | Add matching `ENDIF` or `ENDWHILE`              |

### Deployment Issues

| Issue                        | Cause                    | Solution                                   |
| ---------------------------- | ------------------------ | ------------------------------------------ |
| `SD card not detected`       | Card not inserted        | Insert duckyPad SD card and retry          |
| `Profile already exists`     | Duplicate profile number | Choose different number or use -f to force |
| `Permission denied`          | SD card write-protected  | Remove write protection                    |
| `profile_info.txt corrupted` | Manual edit error        | Restore from backup or recreate manually   |

## Git Ignore

The following are automatically gitignored:

- `tools/vendor/` - Auto-downloaded compiler dependencies
- `*.dsb` - Compiled bytecode files (regenerated from .txt sources)

## Related Documentation

- [duckyScript Language Reference](https://dekunukem.github.io/duckyPad-Pro/doc/duckyscript_info.html)
- [duckyPad Pro User Guide](https://dekunukem.github.io/duckyPad-Pro/doc/getting_started.html)
- [Bytecode VM Documentation](https://dekunukem.github.io/duckyPad-Pro/doc/bytecode_vm.html)
