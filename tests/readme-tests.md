# tests

Test and validation scripts for duckyPad Pro.

## Test Files

### test_profile_manager.py

Tests the ProfileInfoManager module for SD card detection and profile_info.txt parsing.

**Tests:**

- SD card auto-detection (Windows/macOS/Linux)
- profile_info.txt parsing
- GOTO_PROFILE command transformation

**Usage:**

```bash
python tests/test_profile_manager.py
```

**Requirements:**

- SD card with profile_info.txt in root (for full testing)
- Falls back gracefully if SD card not found

### validate_compilation.py

Validates duckyScript compilation results by checking .txt to .dsb conversions.

**Features:**

- Checks for missing .dsb files
- Verifies .dsb files are newer than source .txt files
- Validates bytecode file sizes (minimum 3 bytes for HALT instruction)
- Detects stale compilations (source modified after compilation)

**Usage:**

```bash
# Validate all profiles
python tests/validate_compilation.py

# Validate specific profile
python tests/validate_compilation.py -p profiles/example-productivity

# Verbose mode
python tests/validate_compilation.py -v
```

**Exit Codes:**

- `0`: All compilations valid
- `1`: Missing or invalid compilations found

### get_sample_profiles.py

Downloads official sample profiles from the duckyPad-Pro GitHub repository.

**Features:**

- Downloads sample_profiles.zip from official repo
- Extracts to profiles/sample_profiles/
- Skips download if profiles already exist (unless --force)
- Counts and reports number of profiles downloaded

**Usage:**

```bash
# Download sample profiles
python tests/get_sample_profiles.py

# Force re-download
python tests/get_sample_profiles.py -f

# Verbose mode
python tests/get_sample_profiles.py -v
```

**Destination:**

- `profiles/sample_profiles/` (gitignored)

## Running Tests

Run individual tests:

```bash
python tests/test_profile_manager.py
python tests/validate_compilation.py
python tests/get_sample_profiles.py
```

Run all tests (when pytest is configured):

```bash
python -m pytest tests/
```

## Test Organization

- **Unit tests**: `test_*.py` files testing individual modules
- **Validation scripts**: Utilities for verifying compilation output
- **Resource downloaders**: Scripts that fetch external resources for testing
