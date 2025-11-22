# compilers

Tools for compiling duckyScript 3 text files (`.txt`) to bytecode executables (`.dsb`).

## Scripts

### compile_duckyscript.py

Compiler for duckyScript `.txt` source files to `.dsb` bytecode.

**Features:**

- Auto-downloads compiler dependencies from GitHub
- Compiles single profiles or entire directories
- Colored output for easy error identification
- Verbose mode for detailed compilation info
- Cross-platform compatible (Windows/macOS/Linux)

**Usage:**

```bash
# Compile all profiles in profiles/
python helpers/compilers/compile_duckyscript.py

# Compile specific profile
python helpers/compilers/compile_duckyscript.py -p profiles/games/astroneer

# Compile multiple profiles
python helpers/compilers/compile_duckyscript.py -p workbench/my_profiles

# Verbose output
python helpers/compilers/compile_duckyscript.py -p test_profile -v
```

**Parameters:**

- `-p, --profile-path` (optional): Path to specific profile directory or profiles directory (default: profiles/)
- `-v, --verbose` (optional): Enable verbose output

**Output:**

- Creates `.dsb` files next to each `.txt` file
- Displays compilation summary with success/failure counts
- Returns exit code 0 on success, 1 on failure

---

## Validation

To validate compiled bytecode files, use the compilation script with verbose mode to see detailed output for each file.

---

---

## Workflow

### Initial Setup

1. Ensure Python 3.7+ is installed
2. Run `compile_duckyscript.py` to download compiler and compile all scripts

### During Development

1. Edit `.txt` duckyScript files
2. Run `compile_duckyscript.py` to recompile
3. Use verbose mode (`-v`) to see detailed compilation results
4. Use verbose mode (`-v`) to see detailed compilation results

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
