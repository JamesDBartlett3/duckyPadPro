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

- [ ] Update `tools/shared/yaml_loader.py`

  - [ ] Validate profile names during parsing
  - [ ] Validate key labels during parsing
  - [ ] Check orientation setting and apply correct limits
  - [ ] Provide clear error messages with line numbers

- [ ] Update `tools/generate.py`
  - [ ] Validate before generating config.txt
  - [ ] Validate layer names
  - [ ] Report all validation errors at once (not just first)

### Phase 4: Integrate into Compilation

- [ ] Update `tools/compile.py`
  - [ ] Read config.txt to get orientation setting
  - [ ] Parse key labels from config.txt (z1-z26, x1-x26)
  - [ ] Validate all labels before compilation
  - [ ] Exit with clear error if validation fails

### Phase 5: Integrate into Deployment

- [ ] Update `tools/deploy.py`

  - [ ] Count total profiles on SD card + profiles being deployed
  - [ ] Validate count doesn't exceed 64
  - [ ] Validate profile names in profile_info.txt

- [ ] Update `tools/shared/profiles.py`
  - [ ] Add profile count validation to ProfileInfoManager
  - [ ] Validate names when reading/writing profile_info.txt

### Phase 6: Integration into Main Launcher

- [ ] Update `execute.py`
  - [ ] Ensure validation errors propagate correctly
  - [ ] Provide user-friendly error messages
  - [ ] Add `--no-validate` flag for advanced users (use at own risk)

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

- [ ] Create test profiles

  - [ ] Valid profiles at boundary limits
  - [ ] Invalid profiles exceeding each limit
  - [ ] Edge cases (Unicode, emojis, special characters)

- [ ] Test each workflow

  - [ ] YAML → Generate → Compile → Deploy
  - [ ] Manual config.txt editing → Compile
  - [ ] Deployment with 64 existing profiles

- [ ] Verify error messages are clear and actionable

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
