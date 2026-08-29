# Project Status and TODO

Repository refresher and future improvements. Last reviewed on 2026-08-29.

## Current Status

- The working tree was clean at the start of the review.
- Local `main` and `dev` were synchronized with `origin` before implementation.
- Updated `main` contained the three documentation commits that had previously existed only on `dev`; `main` was then fast-forwarded back into local `dev`.
- Managed-environment work is being implemented on `feature/managed-uv-environment`, branched from the synchronized `dev` commit.
- The last substantive implementation work was completed on 2025-11-29. It added YAML custom-script and `STRING` support, layer inheritance fixes, per-key colors, 14-character profile validation, and safer deployment overwrite handling.

## Architecture Refresher

### Primary Workflow

The YAML workflow is the center of the repository:

1. Define a profile under `workbench/`.
2. Run `.\dpp workbench/<profile>.yaml` in PowerShell, `dpp workbench/<profile>.yaml` in Command Prompt, or `./dpp.sh workbench/<profile>.yaml` in Bash on macOS/Linux.
3. `tools/generate.py`, the repository's only YAML reader, creates one or more profiles under `workbench/profiles/`.
4. Generated `keyN.txt` and `keyN-release.txt` scripts are compiled to gitignored `.dsb` bytecode.
5. Profiles can be deployed to the duckyPad Pro SD card after an automatic backup.

`dpp.ps1`, `dpp.bat`, and `dpp.sh` provide the user entry points; `execute.py` implements YAML generation, compilation, deployment, backup, restore, and device mount/unmount/scan operations.

### YAML Capabilities

- Reusable templates and ordered template overrides
- Parent and layer inheritance
- Key ranges and full key objects
- Per-key labels and colors
- Custom scripts and `STRING` actions
- Modifier-hold, toggle, one-shot, and momentary layers
- Named `GOTO_PROFILE` resolution during compilation

### Hardware and Firmware Constraints

- 26 total inputs: 20 physical keys and six inputs from two rotary encoders
- Key numbers remain unchanged when the device orientation changes
- Keys 21-23 belong to the first encoder; keys 24-26 belong to the second encoder
- Maximum 64 profiles
- Maximum profile or layer name length: 14 characters
- Portrait labels: two lines with at most five characters per line
- Landscape labels: two lines with at most four characters per line
- Only files matching `keyN.txt` or `keyN-release.txt` are duckyScript compilation inputs; `config.txt` is not duckyScript

### Deployment Behavior

The current implementation in `tools/deploy.py` creates `profile_<name>` directories without ordinal numbers. Display order is stored in `profile_info.txt`; existing numbers are preserved and new profiles are appended.

Some documentation still describes the older `profileN_Name` directory convention. The implementation and `tools/readme-tools.md` currently agree on `profile_<name>` plus `profile_info.txt` as the authoritative behavior.

- [ ] Reconcile all deployment naming documentation with the implemented convention
- [ ] Remove or clearly label legacy numbered-folder handling after confirming firmware compatibility

## Managed Python Environment

The repository now defines a non-packaged uv project:

- `pyproject.toml` is the sole direct-dependency source.
- `.python-version` selects the managed CPython 3.12 line.
- `[tool.uv] python-preference = "only-managed"` prevents use of ambient system Python.
- `.venv/` isolates installed packages from user and system environments.
- Committed `uv.lock` records exact cross-platform dependency versions.
- `setup.py` initializes external compiler files, sample profiles, and the workbench; it no longer installs Python packages.
- `tools/vendor/` remains an external, gitignored compiler resource and is not a PyPI dependency.
- `platformdirs` is now declared explicitly because the downloaded compiler imports it; the previous ambient environment had hidden this dependency.
- Repeated setup runs now treat `CompilerUpdater.update()` exit code `0` as success instead of interpreting it as a false boolean.

`hidapi` is isolated as a Python dependency, but its operating-system prerequisites remain external. Linux systems may still require libusb development packages.

- [x] Complete locked-environment smoke tests and mark the uv migration verified
- [ ] Add cross-platform CI using managed CPython 3.12 and `uv sync --locked`
- [ ] Document required Linux libusb packages in CI and contributor setup

## Test Status

Results observed during the 2026-08-29 review before the uv migration:

- `tests/test_validators.py`: 66 checks passed as a standalone script.
- Pytest collection: 16 tests passed, one collection error, and three warnings.
- `tests/test_profile_manager.py` expects an `sd_card` argument in one function, so pytest treats it as a missing fixture even though the file is designed as a standalone hardware script.
- `tests/test_deployment_validation.py`: 14 checks passed and one failed because it still expects a 16-character profile name to be valid; production validation correctly enforces 14 characters.
- `python -m unittest discover` found zero tests because the files are not unittest test cases.
- No SD card was connected, so device discovery, backup, deployment, and profile mapping were not tested end to end.

- [ ] Convert script-style checks into a consistently discoverable test suite
- [ ] Fix the stale 16-character expectation in `tests/test_deployment_validation.py`
- [ ] Add hardware-independent fixtures for `ProfileInfoManager` parsing and `GOTO_PROFILE` transformation
- [ ] Separate hardware integration tests from unit tests with explicit markers or commands
- [ ] Add tests for YAML custom scripts, `STRING`, colors, inheritance, and all layer types

## Code Quality

### Profile Validation Logic

Profile validation code appears in multiple places but could be centralized.

- [ ] Review whether `tools/shared/yaml_loader.py` should coordinate all YAML validation
- [ ] Remove duplicate validation from individual scripts
- [ ] Ensure ASCII-only label requirements are enforced rather than only documented

### Type Hints

- [ ] Add type hints to functions missing them while maintaining consistency
- [ ] Ensure all public functions have type hints
- [ ] Replace broad `# type: ignore` comments with targeted ignores or importable package structure

### Error Handling Patterns

Current error handling is inconsistent across scripts: some paths print tracebacks, some provide minimal context, and some suppress failures.

- [ ] Standardize the error-handling pattern
- [ ] Keep traceback imports at module scope
- [ ] Ensure user-facing errors are clear and actionable
- [ ] Avoid silently continuing after state-changing backup, compilation, or deployment failures

### Project Structure

- [ ] Consider renaming `setup.py` to `bootstrap.py` to avoid confusion with legacy Python packaging metadata
- [ ] Evaluate packaging the shared modules to remove repeated `sys.path` manipulation
- [ ] Keep generated `.dsb`, compiler vendor files, sample profiles, workbench files, and `.venv` out of version control
