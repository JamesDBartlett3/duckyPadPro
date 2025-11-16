# duckyScript Compilers

Tools for compiling duckyScript 3 text files (`.txt`) to bytecode executables (`.dsb`).

## Scripts

### Invoke-DuckyScriptCompiler.ps1

Main compilation script that compiles duckyScript files to bytecode.

**Features:**

- Automatically fetches latest `make_bytecode.py` from GitHub
- Compiles all `.txt` files in profile directories
- Always overwrites existing `.dsb` files
- Detailed compilation statistics and error reporting

**Usage:**

```powershell
# Compile all profiles in the repository
.\Invoke-DuckyScriptCompiler.ps1

# Compile a specific profile directory
.\Invoke-DuckyScriptCompiler.ps1 -ProfilePath ..\..\profiles\example-productivity

# Enable verbose output to see compilation details
.\Invoke-DuckyScriptCompiler.ps1 -Verbose
```

**Parameters:**

- `-ProfilePath` (optional): Path to specific profile directory. If omitted, compiles all profiles.
- `-Verbose` (optional): Show detailed compilation output for each file.

**Output:**

- Creates `.dsb` files next to each `.txt` file
- Displays compilation summary with success/failure counts
- Returns exit code 0 on success, 1 on failure

---

### Test-DuckyScriptCompilation.ps1

Validation script that checks compiled bytecode files.

**Features:**

- Verifies all `.txt` files have corresponding `.dsb` files
- Checks bytecode file validity (size, format)
- Detects outdated compilations (`.txt` newer than `.dsb`)
- Detailed issue reporting

**Usage:**

```powershell
# Validate all profiles
.\Test-DuckyScriptCompilation.ps1

# Validate a specific profile
.\Test-DuckyScriptCompilation.ps1 -ProfilePath ..\..\profiles\example-productivity
```

**Parameters:**

- `-ProfilePath` (optional): Path to specific profile directory. If omitted, validates all profiles.

**Validation Checks:**

- ✓ `.dsb` file exists for each `.txt` file
- ✓ `.dsb` file is not empty
- ✓ `.dsb` file size is valid (≥ 3 bytes)
- ✓ `.dsb` is newer than or same age as `.txt`

---

## Workflow

### Initial Setup

1. Ensure Python 3 is installed
2. Run `Invoke-DuckyScriptCompiler.ps1` to download compiler and compile all scripts

### During Development

1. Edit `.txt` duckyScript files
2. Run `Invoke-DuckyScriptCompiler.ps1` to recompile
3. Run `Test-DuckyScriptCompilation.ps1` to validate

### Pre-Deployment

1. Run `Test-DuckyScriptCompilation.ps1` to ensure all scripts are compiled
2. Transfer both `.txt` and `.dsb` files to duckyPad Pro

## File Structure

After compilation, each profile directory will contain:

```
profile-name/
├── config.txt           # Profile configuration
├── key1.txt            # duckyScript source
├── key1.dsb            # Compiled bytecode
├── key2.txt
├── key2.dsb
└── readme-profile.md
```

## Technical Details

### Compilation Process

1. **Download Compiler**: Fetches latest `make_bytecode.py` from duckyPad-Pro-Configurator
2. **Preprocessing**: Expands `DEFINE` statements, resolves constants
3. **Assembly Generation**: Converts to intermediate assembly language
4. **Bytecode Generation**: Creates 3-byte instructions
5. **String Table**: Appends zero-terminated strings to binary

### Bytecode Format

- **Instruction Size**: 3 bytes (opcode + 2 data bytes)
- **Minimum Size**: 3 bytes (at least HALT instruction)
- **String Storage**: Zero-terminated strings at end of binary
- **Variable Limit**: Up to 64 variables per script

### VM Architecture

- **Type**: 16-bit stack machine
- **Stacks**: Arithmetic stack + Call stack
- **Program Counter**: Points to current instruction
- **Memory**: Variable buffer for up to 64 variables

## References

- [duckyScript Bytecode VM Documentation](https://dekunukem.github.io/duckyPad-Pro/doc/bytecode_vm.html)
- [duckyPad-Pro-Configurator Repository](https://github.com/dekuNukem/duckyPad-Pro-Configurator)
- [duckyScript 3 Guide](https://dekunukem.github.io/duckyPad-Pro/doc/duckyscript_info.html)
