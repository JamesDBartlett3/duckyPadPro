# duckyPadPro Cleanup & Simplification Plan

**Goal**: Simplify the codebase by removing unused code, fixing broken references, consolidating duplicate logic, and questioning the necessity of anything not clearly being used.

**Date**: 2025-11-23

**Note**: This plan excludes gitignored files/directories (vendor/, sample_profiles/, workbench/, \*.dsb, **pycache**/, etc.) as they don't exist in the repository.

---

## 🔴 Phase 1: Fix Broken References (Critical)

These are broken links and references that will confuse users.

### Documentation Path Fixes

- [x] **README.md**
  - Line 38: Remove or fix reference to non-existent `settings/readme-settings.md`
  - Line 60: Change `helpers/readme-helpers.md` → `tools/readme-tools.md`
- [x] **profiles/readme-profiles.md**
  - Line 626: Change `../helpers/readme-helpers.md` → `../tools/readme-tools.md`
- [x] **docs/key-layout.md**
  - Line 5: Change `../helpers/shared/key_layout.py` → `../tools/shared/key_layout.py`
- [x] **docs/getting-started.md**
  - Line 126: Change `helpers/` → `tools/`
  - Review other references to ensure consistency

### Question: Settings Directory

- [x] **Decide**: Do we need a `settings/` directory?
  - Currently referenced in README but doesn't exist
  - Options:
    1. Create it with actual content
    2. Remove all references (recommended for simplification)
  - **Decision**: Removed all references

---

## 🟡 Phase 2: Remove Unused/Empty Directories

Simplify the structure by removing directories that serve no clear purpose.

### Empty Game Profile Directories

These directories exist but contain no files (or only empty readme files):

- [x] **profiles/games/astroneer/** - Removed
- [x] **profiles/games/cold-waters/** - Removed
- [x] **profiles/games/cyberpunk-2077/** - Removed
- [x] **profiles/games/dcs/** - Removed
- [x] **profiles/games/elite-dangerous/** - Removed
- [x] **profiles/games/garrys-mod/** - Removed
- [x] **profiles/example-productivity/** - Removed

**Result**: Removed 7 empty directories and updated readme-games.md

---

## 🟢 Phase 3: Consolidate Duplicate Code

Reduce maintenance burden by extracting common patterns.

### Common Utility Functions

These functions are duplicated across **all** Python scripts in `tools/`:

```python
# Found in: compile.py, deploy.py, backup_and_restore.py, generate_profile_from_yaml.py,
#           duckypad_device.py, generate_readme_files.py, etc.

def _print_color(message: str, color: str = "white"):
    """Print colored message"""
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color, colors['white'])}{message}{colors['reset']}")

def _print_verbose(message: str):
    """Print verbose message if verbose mode enabled"""
    if self.verbose:
        self._print_color(f"  {message}", "cyan")
```

#### Action Items

- [x] Create `tools/shared/console_utils.py` with:

  - `print_color(message, color)`
  - `print_verbose(message, verbose_flag)`
  - `print_success(message)`
  - `print_error(message)`
  - `print_warning(message)`
  - `print_info(message)`
  - `prompt_yes_no()` (unified from deploy.py, backup_and_restore.py, generate_readme_files.py)

- [x] Update `tools/shared/__init__.py` to export new functions

- [ ] Update all scripts to import from shared module:
  - [x] compile.py
  - [ ] deploy.py
  - [ ] backup_and_restore.py
  - [ ] generate_profile_from_yaml.py
  - [ ] generate_readme_files.py (in profiles/)
  - [ ] duckypad_device.py
  - [ ] duckypad.py

### Profile Validation Logic

Profile validation code appears in multiple places but could be centralized.

- [ ] Review if `tools/shared/profile_loader.py` should handle all validation
- [ ] Remove duplicate validation from individual scripts

---

## 🔵 Phase 4: Code Quality Improvements

Make code more maintainable without adding complexity.

### Type Hints

- [ ] Add type hints to functions missing them (maintain consistency)
- [ ] Ensure all public functions have type hints

### Error Handling Patterns

Current state: Inconsistent patterns across scripts

- Some use inline `import traceback` in except blocks
- Some have minimal error handling
- Some suppress errors silently

#### Action Items

- [ ] Standardize error handling pattern
- [ ] Move traceback imports to top of files (not inline)
- [ ] Ensure user-facing errors are clear and actionable

### Import Organization

- [ ] Move all `import copy` statements to top of files (currently inline in profile_loader.py)
- [ ] Move all `import io`, `import contextlib` to top (currently inline in duckypad_device.py)
- [ ] Organize imports: stdlib → third-party → local

---

## 📝 Phase 5: Documentation Cleanup

### Missing or Incomplete Documentation

- [ ] **workbench/readme-workbench.md**

  - Currently minimal (only mentions profiles subdirectory)
  - Should explain YAML workflow or be removed entirely since workbench/ is gitignored
  - **Question**: Is this file even needed if the directory is gitignored?

- [ ] **Empty Game Profile READMEs**
  - Auto-generated but contain no useful information
  - Remove along with empty directories

### Terminology Consistency

Throughout the codebase, ensure consistent use of:

- ✅ `tools/` (not `helpers/`)
- ✅ "profile" (consistently)
- ✅ "duckyScript" (not "ducky script" or "duckyscript")

---

## 🧹 Phase 6: Question Everything

Apply critical thinking to features and files.

### Files to Question

Note: As a general rule, "helpers" (scripts that are utilized by one or more other scripts) should be capable of running independently. The reason for this is to allow for development and testing of individual components without needing to run a full workflow.

- [ ] **workbench/readme-workbench.md**

  - Entire directory is gitignored
  - Is documentation for a gitignored directory useful?
  - **Recommendation**: Remove or drastically simplify to one paragraph in main README

- [ ] **tools/duckypad_device.py**

  - 263 lines of device communication code
  - Is this actively used? By which scripts?
  - If only used by deploy.py, consider inlining or making it optional

- [ ] **tests/test_profile_manager.py**

  - Is this an actual test that runs, or example code?
  - Should it be in tests/ if not run automatically?

- [ ] **Multiple compiled profile output directories**
  - workbench/profiles/ contains many test profiles
  - These are gitignored, so documentation about them may be confusing
  - Ensure docs don't reference gitignored content

### Features to Question

- [ ] **Profile number auto-detection** (deploy.py lines 100-120)

  - Is this feature used in practice?
  - Could deployment be simpler?

- [ ] **Multiple inheritance in YAML profiles**
  - Used anywhere in actual profiles?
  - If not, consider removing to simplify profile_loader.py

---

## 📊 Summary Statistics

### Broken References Found

- 6+ documentation links pointing to wrong paths
- 1 non-existent directory referenced (settings/)
- Multiple helper vs tools inconsistencies

### Duplicate Code Identified

- `_print_color()`: 6+ instances across different files
- `_print_verbose()`: 5+ instances
- `_prompt_yes_no()`: 3 instances
- Import patterns: Repeated in every script

### Empty/Questionable Content

- 6+ empty game profile directories
- 1 minimal workbench readme for gitignored directory
- Inline imports that should be at top of file

---

## 🎯 Recommended Execution Order

1. **Fix broken documentation links** (Phase 1) - Quick wins, high user impact
2. **Remove empty directories** (Phase 2) - Simplifies structure
3. **Remove settings/ references or create the directory** (Phase 1) - Resolve ambiguity
4. **Question workbench readme necessity** (Phase 6) - May be able to delete entirely
5. **Consolidate utility functions** (Phase 3) - Reduces future maintenance
6. **Standardize imports** (Phase 4) - Quick cleanup
7. **Review and simplify YAML loader** (Phase 6) - Remove unused features
8. **Add type hints to remaining functions** (Phase 4) - Low priority

---

## 🚫 Out of Scope (Gitignored)

The following are explicitly **not** part of this cleanup:

- `tools/vendor/` - Auto-downloaded compiler dependencies
- `profiles/sample_profiles/` - Auto-downloaded official samples
- `workbench/` - Development sandbox (except readme discussion)
- `*.dsb` files - Compiled bytecode
- `__pycache__/` - Python cache directories

---

## Success Criteria

After cleanup, the repository should be:

- ✅ Free of broken documentation links
- ✅ Free of empty directories that serve no purpose
- ✅ Consistent in terminology (tools not helpers)
- ✅ DRY - no duplicated utility functions
- ✅ Clear - only keeping what's actively used
- ✅ Simple - easier for contributors to understand

---
