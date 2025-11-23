# TODO

Future improvements and code quality enhancements for the project.

## Code Quality

### Profile Validation Logic

Profile validation code appears in multiple places but could be centralized.

- [ ] Review if `tools/shared/yaml_loader.py` should handle all validation
- [ ] Remove duplicate validation from individual scripts

### Type Hints

- [ ] Add type hints to functions missing them (maintain consistency)
- [ ] Ensure all public functions have type hints

### Error Handling Patterns

Current state: Inconsistent patterns across scripts

- Some use inline `import traceback` in except blocks
- Some have minimal error handling
- Some suppress errors silently

**Action Items:**

- [ ] Standardize error handling pattern
- [ ] Move traceback imports to top of files (not inline)
- [ ] Ensure user-facing errors are clear and actionable
