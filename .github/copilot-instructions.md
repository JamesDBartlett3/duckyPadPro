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
│   │   ├── Invoke-DuckyScriptCompiler.ps1
│   │   └── Test-DuckyScriptCompilation.ps1
│   ├── converters/                 # Format conversion utilities
│   └── generators/                 # Profile/script generators
│       └── profile_generator.py
├── profiles/                       # Complete profile packages
│   ├── example-productivity/
│   ├── sample_profiles/            # Auto-downloaded samples (gitignored)
│   ├── Generate-ReadmeFiles.ps1    # Auto-generate readme files
│   └── Get-SampleProfiles.ps1      # Download official samples
├── scripts/                        # Standalone duckyScript files
│   ├── development/
│   ├── media/
│   ├── productivity/
│   └── system/
├── settings/                       # Device configuration files
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

## File Naming Conventions

### duckyScript Files

- **Key scripts**: `key1.txt` through `key26.txt` (all optional)
- **Release scripts**: `key1-release.txt` through `key26-release.txt` (optional, for key release events)
- **Config files**: `config.txt` (not duckyScript, plain text configuration)
- **Compiled bytecode**: `key1.dsb` through `key26.dsb` (gitignored, auto-generated)

### Documentation Files

- **Profile readmes**: `readme-{folder-name}.md` (e.g., `readme-profiles.md`)
- **Not** `README.md` except for the repository root

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

```powershell
# Compile all profiles
.\helpers\compilers\Invoke-DuckyScriptCompiler.ps1

# Compile specific profile
.\helpers\compilers\Invoke-DuckyScriptCompiler.ps1 -ProfilePath .\profiles\example-productivity

# Validate compilations
.\helpers\compilers\Test-DuckyScriptCompilation.ps1 -ProfilePath .\profiles\example-productivity
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

**Key Colors:**

- `SWCOLOR_N <r> <g> <b>`: RGB color for specific key N's switch LED

**Auto-Brightness:**

- `ab <N>`: Set auto-brightness for key N

### Key Label Constraints

- **Maximum 2 lines** per key label
- **Maximum 5 characters** per line (ASCII only)
- Total: 10 characters maximum per key label

## PowerShell Scripting Guidelines

### Path Handling

- **Always use** `Join-Path` for cross-platform compatibility
- **Never** use string concatenation for paths (e.g., `"$path\file"`)
- Example: `Join-Path $PSScriptRoot "vendor"`

### DRY Principle

- Extract repeated logic into functions
- Example: `Get-ReadmePath` function in `Generate-ReadmeFiles.ps1`

### User Confirmations

- Use `-Force` switch to bypass confirmations
- Default to "Y" (continue) when prompting user
- Show what will be affected before making changes

### Loop Syntax

- Prefer `foreach ($item in $collection)` over `$collection | ForEach-Object`
- Use `ForEach-Object` in pipelines when appropriate

### Error Handling

- Use `-ErrorAction SilentlyContinue` for cleanup operations
- Use try/catch for critical operations
- Provide clear, colored output (Green=success, Red=error, Yellow=warning, Cyan=info)

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
- `.ps1` files in repository

## Documentation Standards

### Profile README Requirements

1. **Description**: What the profile does
2. **Keys**: List of what each key does
3. **Usage**: How to install and use
4. **Platform**: OS compatibility (Windows/macOS/Linux)
5. **Prerequisites**: Any required software or setup

### Code Comments

- **duckyScript**: Use `REM` for comments
- **PowerShell**: Use `#` for comments
- **Python**: Use `"""docstrings"""` and `#` comments
- Always document what a script/key does, not just how

### Markdown Formatting

- Use code fences with language identifiers
- Use tables for structured data
- Use relative links for intra-repository references
- Example: `[profiles](profiles/readme-profiles.md)` not `[profiles](profiles/README.md)`

## Common Patterns

### Creating New Profiles

```powershell
# Generate structure with descriptive name
cd helpers/generators
python profile_generator.py discord-tools 20

# Edit key files and config.txt
# Compile if needed
.\helpers\compilers\Invoke-DuckyScriptCompiler.ps1 -ProfilePath .\profiles\discord-tools

# When deploying to device, user renames to profileN_Name:
# discord-tools -> profile2_DiscordTools (or whatever number/name they prefer)
```

### Downloading Resources

```powershell
# Get official sample profiles
.\profiles\Get-SampleProfiles.ps1

# Re-download (overwrite existing)
.\profiles\Get-SampleProfiles.ps1 -Force
```

### Auto-generating READMEs

```powershell
# Generate in all directories
.\profiles\Generate-ReadmeFiles.ps1

# Overwrite existing files
.\profiles\Generate-ReadmeFiles.ps1 -Overwrite

# Force without confirmation
.\profiles\Generate-ReadmeFiles.ps1 -Overwrite -Force
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
2. **Validate**: Run `Test-DuckyScriptCompilation.ps1`
3. **Verify**: Check git status doesn't include .dsb files or vendor/
4. **Document**: Ensure README files are up to date
5. **Test**: Try scripts on actual hardware if possible

### Compilation Validation

```powershell
# Compile and validate
.\helpers\compilers\Invoke-DuckyScriptCompiler.ps1 -ProfilePath .\profiles\my-profile
.\helpers\compilers\Test-DuckyScriptCompilation.ps1 -ProfilePath .\profiles\my-profile
```

## Helper Script Downloads

### Sample Profiles

- **Source**: `https://github.com/dekuNukem/duckyPad-Pro/raw/master/resources/sample_profiles/sample_profiles.zip`
- **Destination**: `profiles/sample_profiles/`
- **Script**: `Get-SampleProfiles.ps1`
- **Gitignored**: Yes

### Compiler Dependencies

- **Source**: GitHub Releases API for `duckyPad/duckyPad-Configurator`
- **Destination**: `helpers/compilers/vendor/`
- **Script**: Auto-downloaded by `Invoke-DuckyScriptCompiler.ps1`
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

- **PowerShell**: Follow existing patterns in `Invoke-DuckyScriptCompiler.ps1`
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
- Use proper PowerShell path handling
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
