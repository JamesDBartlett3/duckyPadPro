# Validation Implementation Plan

Plan for implementing duckyPad Pro operating system limitation checks to prevent invalid bytecode compilation.

## Limitations to Enforce

### System-Level Limits

- **Profile Count**: Maximum 64 profiles total on SD card
- **Profile/Layer Names**: Maximum 16 characters per name

### Key Label Limits (Orientation-Dependent)

**Portrait Mode:**

- Total: 10 characters maximum per key
- Line 1 (z): 5 characters maximum
- Line 2 (x): 5 characters maximum

**Landscape Mode:**

- Total: 8 characters maximum per key
- Line 1 (z): 4 characters maximum
- Line 2 (x): 4 characters maximum

## Implementation Phases

### Phase 1: Planning & Analysis

- [x] Identify all files that need validation

  - `tools/compile.py` - Pre-compilation validation
  - `tools/generate.py` - YAML generation validation (found silent truncation at line 210-211)
  - `tools/deploy.py` - Deployment validation
  - `tools/shared/profiles.py` - ProfileInfoManager validation (profile_info.txt parsing)
  - `tools/shared/yaml_loader.py` - YAML parsing validation

- [x] Determine validation points

  - [x] YAML file parsing (catch early)
  - [x] Profile generation (before writing files)
  - [x] Pre-compilation (before invoking compiler)
  - [x] Deployment (before copying to SD card)

- [x] Design validation architecture
  - [x] Create shared validation module (`tools/shared/validators.py`)
  - [x] Define validation error types/classes (ValidationError)
  - [x] Decide on error reporting format (fail-fast approach)

### Phase 2: Create Validation Module

- [x] Create `tools/shared/validators.py`

  - [x] `validate_profile_name(name: str) -> tuple[bool, str]`
  - [x] `validate_key_label(z_line: str, x_line: str, orientation: str) -> tuple[bool, str]`
  - [x] `validate_profile_count(profile_paths: list) -> tuple[bool, str]`
  - [x] `ValidationError` exception class
  - [x] Helper functions for character counting (handle Unicode correctly)
  - [x] Added convenience `require_*` functions for raising exceptions
  - [x] Exported all validators and constants from `tools/shared/__init__.py`
  - [x] Tested imports successfully

- [x] Add unit tests for validators
  - [x] Test edge cases (empty strings, Unicode, emojis)
  - [x] Test boundary conditions (exactly at limit)
  - [x] Test orientation-specific limits
  - [x] All 66 tests passed ✓

### Phase 3: Integrate into YAML Workflow

- [x] Update `tools/shared/yaml_loader.py`

  - [x] Validate profile names during parsing
  - [x] Added ValidationError import and require_valid_profile_name
  - [x] Profile name validated when loading YAML
  - [x] Added copy import for deepcopy usage
  - [x] Provides clear error messages with file path

- [x] Update `tools/generate.py`
  - [x] Validate before generating config.txt
  - [x] Validate layer names (uses same \_validate_folder_name)
  - [x] Added validator imports (ValidationError, validate_key_label, etc.)
  - [x] Enhanced \_validate_folder_name to check both duckyPad Pro limits (16 chars) and filesystem chars
  - [x] Replaced silent label truncation with orientation-aware validation
  - [x] Validates labels against portrait (5/5/10) or landscape (4/4/8) limits
  - [x] Tested with multiple YAML files:
    - ✓ test_profile.yaml (caught 6-char label in portrait mode)
    - ✓ validation_test.yaml (valid labels pass)
    - ✓ long_name_test.yaml (caught 31-char profile name)
    - ✓ landscape_test.yaml (valid landscape labels pass)
    - ✓ landscape_fail_test.yaml (caught 5-char label in landscape mode)

### Phase 4: Integrate into Compilation

- [x] Update `tools/compile.py`
  - [x] Read config.txt to get orientation setting
  - [x] Parse key labels from config.txt (z1-z26, x1-x26)
  - [x] Validate all labels before compilation
  - [x] Exit with clear error if validation fails
  - [x] Added validator imports (ValidationError, validate_key_label, require_valid_key_label)
  - [x] Created `_parse_config()` method to extract orientation and labels from config.txt
  - [x] Created `_validate_profile_config()` method to validate before compilation
  - [x] Integrated validation into `compile_profile()` workflow
  - [x] Enhanced CompilerStats to track validation failures separately
  - [x] Updated compilation summary to show validation failures
  - [x] Fixed exit code behavior - now returns 1 on validation failure
  - [x] Tested with multiple scenarios:
    - ✓ Portrait mode: caught 6-char label (exceeds 5-char limit)
    - ✓ Portrait mode: valid labels pass
    - ✓ Landscape mode: caught 5-char label (exceeds 4-char limit)
    - ✓ Landscape mode: valid labels pass
    - ✓ YAML-generated profiles compile successfully
    - ✓ Exit code 1 on validation failure, 0 on success
    - ✓ Summary correctly shows "Validation failed: N"

### Phase 5: Integrate into Deployment

- [x] Update `tools/deploy.py`

  - [x] Count total profiles on SD card + profiles being deployed
  - [x] Validate count doesn't exceed 64
  - [x] Validate profile names in profile_info.txt
  - [x] Added validator imports (ValidationError, validate_profile_count, validate_profile_name, etc.)
  - [x] Added validation_failed counter to DeploymentStats
  - [x] Count existing profiles on SD card before deployment
  - [x] Validate total count (existing + new) before deployment
  - [x] Display clear breakdown: existing, new, total, and max allowed
  - [x] Validate profile names when updating profile_info.txt
  - [x] Skip invalid profile names with warning

- [x] Update `tools/shared/profiles.py`

  - [x] Add profile count validation to ProfileInfoManager
  - [x] Validate names when reading/writing profile_info.txt
  - [x] Added validator imports
  - [x] Validate profile names when parsing profile_info.txt
  - [x] Skip invalid names during parsing (silent skip for backwards compatibility)

- [x] Testing
  - [x] Created test_deployment_validation.py
  - [x] All 15 validation tests pass:
    - ✓ Profile count scenarios (7 tests): valid deployments, at-limit, over-limit
    - ✓ Profile name scenarios (8 tests): valid names, too long, empty
    - ✓ Correctly accepts valid profiles
    - ✓ Correctly rejects invalid profiles

### Phase 6: Integration into Main Launcher

- [x] Update `execute.py`
  - [x] Ensure validation errors propagate correctly
    - ✓ cmd_yaml() checks exit codes from generate, compile, deploy
    - ✓ cmd_compile() returns exit code from compile_profiles()
    - ✓ All validation errors propagate through to main()
    - ✓ Exit codes: 0 = success, 1 = failure (including validation)
  - [x] Provide user-friendly error messages
    - ✓ Tools already provide clear validation error messages
    - ✓ execute.py shows which step failed
    - ✓ Color-coded output: red for errors, yellow for warnings
  - [ ] Add `--no-validate` flag for advanced users (optional - deferred)
    - Note: Current design has validation integrated deeply into workflows
    - Skipping validation could produce invalid bytecode
    - Consider adding in future if there's a valid use case

### Phase 7: Documentation

- [ ] Create validation documentation

  - [ ] Document all limits
  - [ ] Provide examples of valid/invalid configurations
  - [ ] Explain error messages

- [ ] Update existing docs

  - [ ] `docs/getting-started.md` - Mention limits
  - [ ] `docs/profile-guide.md` - Explain label limits
  - [ ] `tools/readme-tools.md` - Document validation behavior
  - [ ] `README.md` - Link to validation docs

- [ ] Update error messages to reference documentation

### Phase 8: Testing

- [x] Create test profiles

  - [x] Valid profiles at boundary limits
    - ✓ validation_test.yaml - portrait mode at limits
    - ✓ landscape_test.yaml - landscape mode at limits
  - [x] Invalid profiles exceeding each limit
    - ✓ long_name_test.yaml - 31-char profile name
    - ✓ landscape_fail_test.yaml - 5-char label in landscape
    - ✓ test_profile.yaml - caught 6-char label
  - [x] Edge cases (Unicode, emojis, special characters)
    - ✓ test_validators.py - Unicode and emoji tests (6 test cases)

- [x] Test each workflow

  - [x] YAML → Generate → Compile → Deploy
    - ✓ YAML generation validates names and labels
    - ✓ Compilation validates config.txt labels
    - ✓ Deployment validates profile count
  - [x] Manual config.txt editing → Compile
    - ✓ Created ValidationFailTest profile with invalid label
    - ✓ Compilation correctly rejects invalid labels
  - [x] Deployment with profile limits
    - ✓ test_deployment_validation.py - 7 profile count scenarios
    - ✓ Correctly accepts up to 64 profiles
    - ✓ Correctly rejects 65+ profiles

- [x] Verify error messages are clear and actionable
  - ✓ Profile name errors include character count and limit
  - ✓ Label errors specify which line, orientation, and limit
  - ✓ Profile count errors show existing, new, total, and max
  - ✓ All errors include context and suggested fixes

**Testing Summary:**

- Unit tests: 66 validator tests + 15 deployment tests = 81 total ✓
- Integration tests: 5 YAML files tested with various scenarios ✓
- Exit codes: Properly return 1 on failure, 0 on success ✓

## Technical Considerations

### Unicode/Character Counting

- duckyPad Pro likely counts **bytes** or **display width**, not Unicode code points
- Need to verify: Do emojis count as 1 character or more?
- ASCII characters are safe (1 byte each)
- Consider warning users about non-ASCII characters

### Orientation Detection

- Read from `config.txt`: `IS_LANDSCAPE 1` or `IS_LANDSCAPE 0`
- Default to portrait if not specified
- YAML templates specify orientation in profile config

### Error Reporting Strategy

**Option A: Fail Fast**

- Stop at first validation error
- Quick feedback
- User must fix and retry

**Option B: Collect All Errors**

- Report all validation errors at once
- More efficient for users
- More complex to implement

**Recommendation**: Start with Option A, consider Option B in future

### Backward Compatibility

- Add validation as warnings first?
- Make validation opt-in initially?
- Or enforce immediately (breaking change)?

**Recommendation**: Enforce immediately - invalid profiles won't work on device anyway

## Success Criteria

- [ ] All validation limits enforced
- [ ] Clear, actionable error messages
- [ ] No false positives (valid profiles pass)
- [ ] No false negatives (invalid profiles caught)
- [ ] Performance impact minimal (<100ms validation overhead)
- [ ] Documentation complete
- [ ] All existing valid profiles still work

## Future Enhancements

- [ ] Validate duckyScript syntax before compilation
- [ ] Check for common duckyScript mistakes
- [ ] Warn about deprecated commands
- [ ] Validate GOTO_PROFILE references exist
- [ ] Check for infinite loops in scripts
