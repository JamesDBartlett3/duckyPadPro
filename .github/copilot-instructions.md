# GitHub Copilot Instructions for duckyPadPro Repository

## Repository Overview

This is a community repository for duckyPad Pro profiles, settings, scripts, and helper utilities. The duckyPad Pro is a 26-input macro keyboard (20 physical keys + 2 rotary encoder knobs with 3 inputs each) that uses duckyScript to automate tasks and streamline workflows.

## Critical Hardware Information

### Key Layout

- **Physical Keys**: 20 keys in a 4×5 grid (portrait) or 5×4 grid (landscape after 90° CCW rotation)
- **Rotary Encoders**: 2 encoders with 3 inputs each (clockwise, counter-clockwise, press)
- **Total Inputs**: 26 (keys 1-20 are physical keys, keys 21-26 are rotary encoder inputs)

### Key Numbering

- Keys 1-20: Physical keys numbered left-to-right, top-to-bottom in portrait mode
- Key 21: First rotary encoder - clockwise rotation
- Key 22: First rotary encoder - counter-clockwise rotation
- Key 23: First rotary encoder - press
- Key 24: Second rotary encoder - clockwise rotation
- Key 25: Second rotary encoder - counter-clockwise rotation
- Key 26: Second rotary encoder - press

**Important**: Key numbers NEVER change regardless of orientation. Only the physical layout interpretation changes.

### Rotary Encoder Positions

- **Portrait mode**: Encoders on right side (first=upper, second=lower)
- **Landscape mode**: Encoders on top side (first=left, second=right)
- **Naming**: Use "first" and "second" encoder (not "top/bottom" or "left/right") for consistency across orientations

## Repository Structure

```
duckyPadPro/
├── .github/
│   └── copilot-instructions.md    # This file
├── docs/                           # Documentation and guides
│   ├── getting-started.md
│   ├── profile-guide.md
│   ├── key-layout.md
│   └── feature-ideas.md
├── helpers/                        # Helper utilities
│   ├── compilers/                  # duckyScript compilation tools
│   │   ├── vendor/                 # Auto-downloaded Python dependencies (gitignored)
│   │   ├── compile_duckyscript.py
│   │   └── Test-DuckyScriptCompilation.ps1
│   ├── converters/                 # Format conversion utilities
│   └── generators/                 # Profile/script generators
│       └── profile_generator.py
├── profiles/                       # Complete profile packages
│   ├── example-productivity/
│   ├── sample_profiles/            # Auto-downloaded samples (gitignored)
│   └── generate_readme_files.py    # Auto-generate readme files
├── scripts/                        # Standalone duckyScript files
│   ├── development/
│   ├── media/
│   ├── productivity/
│   └── system/
├── settings/                       # Device configuration files
├── tests/                          # Test and validation scripts
│   ├── get_sample_profiles.py      # Download official samples
│   ├── test_profile_manager.py     # Test profile name mapping
│   └── validate_compilation.py     # Validate .txt → .dsb conversions
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

## Terminal Commands

### PowerShell Syntax (Windows)

- **CRITICAL**: Use PowerShell syntax, NOT bash/shell redirection
- **File operations**: Use cmdlets like `Copy-Item`, `Remove-Item`, `Get-Content`, `Set-Content`
- **NEVER use bash redirects**: `>`, `>>`, `<` are NOT valid in PowerShell commands
- **Piping**: Use PowerShell pipeline `|` with cmdlets, not bash-style redirection
- **Examples**:
  - ✓ Correct: `Get-Content file.txt | Select-Object -First 10`
  - ✓ Correct: `Set-Content -Path file.txt -Value "content"`
  - ✗ Wrong: `cat file.txt | head -10` (bash syntax)
  - ✗ Wrong: `echo "content" > file.txt` (bash redirection)

### General Guidelines

- **Always** use proper terminal syntax for the active shell
- When running Python scripts, use `python` command
- Use forward slashes or backslashes appropriately for the OS

## File Naming Conventions

### duckyScript Files

- **Key scripts**: `key1.txt` through `key26.txt` (all optional)
- **Release scripts**: `key1-release.txt` through `key26-release.txt` (optional, for key release events)
- **Config files**: `config.txt` (not duckyScript, plain text configuration)
- **Compiled bytecode**: `key1.dsb` through `key26.dsb` (gitignored, auto-generated)

### Documentation Files

- **Profile readmes**: `readme-{folder-name}.md` (e.g., `readme-profiles.md`)
- **Repository root ONLY**: `README.md`
- **All other directories**: `readme-{folder-name}.md` where `{folder-name}` is the name of the directory containing the file

**Examples:**

- `profiles/` → `profiles/readme-profiles.md`
- `helpers/compilers/` → `helpers/compilers/readme-compilers.md`
- `scripts/development/` → `scripts/development/readme-development.md`
- Repository root → `README.md` (only exception)

**IMPORTANT**: When creating documentation files, ALWAYS use `readme-{folder-name}.md` format except for the repository root. Never create `README.md` in subdirectories.

### Pattern Matching

- duckyScript files: `^key\d+(-release)?\.txt$`
- Config files are NOT duckyScript and should NOT be compiled

## duckyScript Compilation

### Critical Rules

1. **All .dsb files are gitignored** - they are auto-generated binaries
2. **Compiler dependencies in `helpers/compilers/vendor/` are gitignored** - auto-downloaded from GitHub
3. **Only compile files matching pattern**: `^key\d+(-release)?\.txt$`
4. **DO NOT compile**: `config.txt`, README files, or other text files

### Compilation Process

```bash
# Compile all profiles
python helpers/compilers/compile_duckyscript.py

# Compile specific profile
python helpers/compilers/compile_duckyscript.py -p profiles/example-productivity

# Verbose mode for detailed output
python helpers/compilers/compile_duckyscript.py -p profiles/example-productivity -v
```

### Compiler Behavior

- Auto-downloads Python compiler files from GitHub Releases API: `duckyPad/duckyPad-Configurator`
- Stores dependencies in `helpers/compilers/vendor/` (gitignored)
- Requires Python 3 installed on system
- Uses GitHub API to fetch latest release
- Downloads all .py files from release zipball

## Profile Structure

### Profile Naming Convention

**For Deployment Only**: When deploying profiles to duckyPad Pro's SD card, folders MUST follow the naming pattern `profileN_Name` where:

- `profile` prefix identifies the folder as a profile to the duckyPad Pro
- `N` is a number (1, 2, 3, etc.) that determines display order
- `_` separates the number from the name
- `Name` is a descriptive name (spaces allowed, use underscores or CamelCase)

Examples:

- `profile1_Welcome`
- `profile2_Discord`
- `profile10_MS Teams`

**Purpose**:

1. The `profile` prefix tells duckyPad Pro this folder contains a profile
2. The number controls profile order - when users press +/- buttons on the device, it switches to next/previous profile by this number

**Important**:

- Folders without the `profileN_` prefix will be ignored by duckyPad Pro
- In this repository, profiles should use descriptive names (e.g., `discord-bots`, `photo-editing`) without the `profileN_` prefix
- Users apply their preferred naming and numbering when deploying to their device
- The `example-productivity` folder demonstrates this approach

### Required Files

```
profile-name/
├── config.txt       # Profile configuration (not duckyScript)
└── README.md        # Profile documentation
```

### Optional Files

- `key1.txt` through `key26.txt` - duckyScript for each key
- `key1-release.txt` through `key26-release.txt` - Scripts for key release events

### Config File Format

The `config.txt` file uses key-value pairs for configuration:

```
z1 My
x1 Key
z2 Other
BG_COLOR 100 150 200
DIM_UNUSED_KEYS 1
SWCOLOR_1 255 0 0
ab 5
```

### Configuration Directives

**Key Labels:**

- `zN <text>`: First line of label for key N (max 5 chars, ASCII only)
- `xN <text>`: Second line of label for key N (max 5 chars, ASCII only)
- Both lines optional; keys without labels appear blank

**Display Settings:**

- `BG_COLOR <r> <g> <b>`: Background color (RGB 0-255)
- `DIM_UNUSED_KEYS <0|1>`: Dim keys without scripts (0=off, 1=on)
- `IS_LANDSCAPE <0|1>`: Set landscape orientation (1=on, 0=off/portrait)

**Key Colors:**

- `SWCOLOR_N <r> <g> <b>`: RGB color for specific key N's switch LED
- `KEYDOWN_COLOR <r> <g> <b>`: Color when any key is pressed (default: inverse of BG_COLOR)

**Key Behavior:**

- `dr N`: Don't repeat - disable auto-repeat when key N is held down (macro won't repeat)
- `ab N`: Allow abort - allow exiting early from key N's macro by pressing any key

### Key Label Constraints

- **Maximum 2 lines** per key label
- **Maximum 5 characters** per line (ASCII only)
- Total: 10 characters maximum per key label

## Python Scripting Guidelines

### Path Handling

- **Always use** `Path` from `pathlib` for cross-platform compatibility
- **Never** use string concatenation for paths
- Example: `Path(__file__).parent / "vendor"`

### DRY Principle

- Extract repeated logic into functions
- Example: `ReadmeInfo` class in `generate_readme_files.py`

### User Confirmations

- Use `--force` or `-f` flag to bypass confirmations
- Default to "Y" (continue) when prompting user
- Show what will be affected before making changes

### Code Style

- Follow PEP 8 conventions
- Use type hints where appropriate
- Prefer list/dict comprehensions over loops when readable

### Error Handling

- Use try/except for critical operations
- Provide clear, colored output (Green=success, Red=error, Yellow=warning, Cyan=info)
- Use ANSI color codes for cross-platform terminal colors

## Python Scripting Guidelines

### Profile Generator

- Located at: `helpers/generators/profile_generator.py`
- Supports keys 1-26 (not just 1-20)
- Includes helpful comments for rotary encoder keys (21-26)
- Creates: `config.txt`, `keyN.txt` files, `README.md`

### Usage

```bash
python profile_generator.py <profile-name> <number-of-keys>
python profile_generator.py discord-tools 20
python profile_generator.py photo-editing 15
```

**Note**: Generated profiles use descriptive names. Users rename to `profileN_Name` format when deploying to their duckyPad Pro.

### Key Descriptions

- Keys 1-20: "Key N"
- Key 21: "First rotary encoder - Clockwise rotation"
- Key 22: "First rotary encoder - Counter-clockwise rotation"
- Key 23: "First rotary encoder - Press"
- Key 24: "Second rotary encoder - Clockwise rotation"
- Key 25: "Second rotary encoder - Counter-clockwise rotation"
- Key 26: "Second rotary encoder - Press"

## Git Ignore Rules

### Always Gitignored

- `*.dsb` - Compiled bytecode files
- `helpers/compilers/vendor/` - Auto-downloaded compiler dependencies
- `profiles/sample_profiles/` - Auto-downloaded official samples

### Never Gitignored

- `.txt` files (duckyScript source files)
- `config.txt` files
- `.py` files in repository

## Documentation Standards

### Profile README Requirements

1. **Description**: What the profile does
2. **Keys**: List of what each key does
3. **Usage**: How to install and use
4. **Platform**: OS compatibility (Windows/macOS/Linux)
5. **Prerequisites**: Any required software or setup

### Code Comments

- **duckyScript**: Use `REM` for comments
- **Python**: Use `"""docstrings"""` and `#` comments
- Always document what a script/key does, not just how

### Markdown Formatting

- Use code fences with language identifiers
- Use tables for structured data
- Use relative links for intra-repository references
- Example: `[profiles](profiles/readme-profiles.md)` not `[profiles](profiles/README.md)`

## Common Patterns

### Creating New Profiles

```bash
# Generate structure with descriptive name
cd helpers/generators
python profile_generator.py discord-tools 20

# Edit key files and config.txt
# Compile if needed
python helpers/compilers/compile_duckyscript.py -p profiles/discord-tools

# When deploying to device, user renames to profileN_Name:
# discord-tools -> profile2_DiscordTools (or whatever number/name they prefer)
```

### Downloading Resources

```bash
# Get official sample profiles
python tests/get_sample_profiles.py

# Re-download (overwrite existing)
python tests/get_sample_profiles.py -f
```

### Auto-generating READMEs

```bash
# Generate in all directories
python profiles/generate_readme_files.py

# Overwrite existing files
python profiles/generate_readme_files.py -o

# Force without confirmation
python profiles/generate_readme_files.py -o -f
```

## duckyScript Best Practices

### Timing

- Use delays between sequential actions (500-1000ms initially)
- Single key presses or key combinations don't need delays
- Reduce delays after testing on target system
- Applications need time to launch/switch

### Comments

```
REM Description of what this key does
REM Author: Your Name
REM Platform: Windows/macOS/Linux
```

### Platform-Specific Scripts

- Document OS requirements
- Test on target platform
- Consider creating separate versions for each OS

### Common Commands

- `STRING`: Type text
- `ENTER`: Press Enter
- `DELAY`: Wait in milliseconds
- `REM`: Comment
- `CONTROL`, `SHIFT`, `ALT`, `COMMAND`: Modifier keys
- `MEDIA_VOLUME_UP`, `MEDIA_VOLUME_DOWN`, `MEDIA_MUTE`: Media controls

## Testing Guidelines

### Before Committing

1. **Compile**: Ensure all .txt files compile without errors
2. **Validate**: Run `python tests/validate_compilation.py`
3. **Verify**: Check git status doesn't include .dsb files or vendor/
4. **Document**: Ensure README files are up to date
5. **Test**: Try scripts on actual hardware if possible

### Compilation Validation

```bash
# Compile all profiles
python helpers/compilers/compile_duckyscript.py

# Validate all compilations
python tests/validate_compilation.py

# Validate specific profile
python tests/validate_compilation.py -p profiles/my-profile -v
```

## Helper Script Downloads

### Sample Profiles

- **Source**: `https://github.com/dekuNukem/duckyPad-Pro/raw/master/resources/sample_profiles/sample_profiles.zip`
- **Destination**: `profiles/sample_profiles/`
- **Script**: `tests/get_sample_profiles.py`
- **Gitignored**: Yes

### Compiler Dependencies

- **Source**: GitHub Releases API for `duckyPad/duckyPad-Configurator`
- **Destination**: `helpers/compilers/vendor/`
- **Script**: Auto-downloaded by `compile_duckyscript.py`
- **Gitignored**: Yes
- **Files**: All .py files from release (make_bytecode.py, ds3_preprocessor.py, etc.)

## Contribution Guidelines

### Pull Request Checklist

- [ ] No .dsb files committed
- [ ] No vendor/ files committed
- [ ] All .txt files compile successfully
- [ ] README.md included with new profiles
- [ ] Documentation uses correct terminology (26 keys, rotary encoders, etc.)
- [ ] Platform compatibility documented
- [ ] Code follows repository patterns

### Code Style

- **Python**: Follow PEP 8
- **duckyScript**: Include REM comments
- **Markdown**: Use relative links, code fences

## External Resources

### Official Documentation

- [duckyPad Pro Site](https://dekunukem.github.io/duckyPad-Pro/)
- [duckyScript Documentation](https://dekunukem.github.io/duckyPad-Pro/doc/duckyscript_info.html)
- [User Guide](https://dekunukem.github.io/duckyPad-Pro/doc/getting_started.html)

### GitHub Repositories

- [duckyPad-Pro](https://github.com/dekuNukem/duckyPad-Pro) - Official repository
- [duckyPad-Configurator](https://github.com/duckyPad/duckyPad-Configurator) - Compiler source

## Special Considerations

### When Working with Profiles

- In repository: Use descriptive names (e.g., `discord-bots`, `photo-editing`)
- For deployment: Users rename to `profileN_Name` based on their preferred order
- Profile number determines display order on device (+/- buttons)
- Remember all key files are optional
- Keys 21-26 are for rotary encoders (not physical grid keys)
- Rotary encoder naming is consistent across orientations
- Config.txt is NOT duckyScript

### When Writing Helper Scripts

- Auto-download dependencies when possible
- Store downloads in gitignored folders
- Use proper Python path handling with pathlib
- Provide clear user feedback with colors
- Support -Force flags for automation

### When Creating Documentation

- Reference correct key counts (26 total, not 20)
- Use "first" and "second" for rotary encoders
- Explain orientation behavior clearly
- Link to existing docs using relative paths
- Follow readme-{name}.md naming pattern (not README.md)

## Future Feature Ideas

See `docs/feature-ideas.md` for detailed feature proposals including:

- Multi-layer profile generator
- Profile orientation converter
- Profile mirror tool
- Hold-toggle hybrid generator
- Layer inheritance tool

When implementing features, refer to this document for design patterns and use cases.
