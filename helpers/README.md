# Helpers

This directory contains helper scripts, tools, and utilities written in various programming languages to support duckyPad Pro usage.

## Supported Languages

- **Python**: Data processing, automation, converters
- **JavaScript/Node.js**: Web-based tools, generators
- **PowerShell**: Windows automation, compilation tools
- **Bash/Shell**: System utilities, batch operations
- **Other**: Any language that helps with duckyPad Pro workflows

## Organization

Helper scripts should be organized by purpose:

```
helpers/
├── compilers/        # duckyScript compilation tools
├── converters/       # Format conversion utilities
├── generators/       # Script/profile generators
├── validators/       # Validation tools
└── utilities/        # General utility scripts
```

## duckyScript Compilation

### Overview

duckyScript 3 files (`.txt`) must be compiled to bytecode (`.dsb`) before they can be executed on duckyPad Pro. The compilation process converts human-readable scripts into optimized 3-byte instruction sequences for the duckyPad Pro virtual machine.

### Quick Start

```powershell
# Compile all profiles
.\helpers\compilers\Invoke-DuckyScriptCompiler.ps1

# Compile a specific profile
.\helpers\compilers\Invoke-DuckyScriptCompiler.ps1 -ProfilePath .\profiles\example-productivity

# Validate all compilations
.\helpers\compilers\Test-DuckyScriptCompilation.ps1

# Enable verbose output
.\helpers\compilers\Invoke-DuckyScriptCompiler.ps1 -Verbose
```

### How It Works

1. **Auto-fetch Compiler**: `Invoke-DuckyScriptCompiler.ps1` automatically downloads the latest `make_bytecode.py` from [duckyPad-Pro-Configurator releases](https://github.com/dekuNukem/duckyPad-Pro-Configurator/releases)

2. **Compile Scripts**: Finds all `.txt` files in the specified path (or all profiles) and compiles them to `.dsb` bytecode

3. **Validate Results**: `Test-DuckyScriptCompilation.ps1` checks that:
   - All `.txt` files have corresponding `.dsb` files
   - Bytecode files are valid (correct size, not empty)
   - `.dsb` files are up-to-date with their `.txt` sources

### Requirements

- **Python 3**: Required to run `make_bytecode.py`
- **Internet Connection**: Needed for initial compiler download

### Common Compilation Errors

| Error                      | Cause                                 | Solution                                        |
| -------------------------- | ------------------------------------- | ----------------------------------------------- |
| `Python not found`         | Python 3 not installed or not in PATH | Install Python 3 and add to system PATH         |
| `Syntax error in line X`   | Invalid duckyScript syntax            | Check script syntax at the specified line       |
| `Undefined variable $name` | Variable used before declaration      | Declare variable with `VAR $name = value` first |
| `Unknown command`          | Unsupported duckyScript command       | Verify command is supported in duckyScript 3    |
| `Missing ENDIF/ENDWHILE`   | Unclosed control structure            | Add matching `ENDIF` or `ENDWHILE`              |

### Troubleshooting

**Compilation fails for all files:**

- Ensure Python 3 is installed: `python --version`
- Check internet connection for compiler download
- Verify `make_bytecode.py` downloaded correctly

**Some files fail to compile:**

- Run with `-Verbose` flag to see detailed error messages
- Check duckyScript syntax in failing `.txt` files
- Verify all variables are declared before use

**`.dsb` files are outdated:**

- Run `Invoke-DuckyScriptCompiler.ps1` to recompile
- `.dsb` files are automatically overwritten with latest compilation

### Bytecode Format

Compiled `.dsb` files contain:

- **3-byte instructions**: Fixed-length opcodes for the duckyPad Pro VM
- **String table**: Zero-terminated strings stored at end of binary
- **Variables**: Up to 64 variables stored in VM memory

For more details, see the [duckyScript Bytecode VM Documentation](https://dekunukem.github.io/duckyPad-Pro/doc/bytecode_vm.html).

## Requirements

Each helper script should include:

- A README explaining its purpose and usage
- Required dependencies (requirements.txt, package.json, etc.)
- Example usage
- Installation instructions if needed

## Examples

- Profile generators to create profiles from templates
- Converters to transform data into duckyScript format
- Validators to check duckyScript syntax
- Backup/restore utilities for duckyPad Pro configurations
