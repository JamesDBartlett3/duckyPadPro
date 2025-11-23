# Contributing to duckyPadPro

Thank you for your interest in contributing to the duckyPadPro repository! This guide will help you get started.

## Ways to Contribute

- **Share Profiles**: Submit complete profile packages
- **Add Scripts**: Contribute useful standalone scripts
- **Create Helpers**: Develop tools and utilities
- **Improve Documentation**: Enhance guides and examples
- **Report Issues**: Help identify bugs or problems
- **Suggest Enhancements**: Propose new features or improvements

## Getting Started

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create a branch** for your contribution
4. **Make your changes**
5. **Test** your contribution
6. **Submit** a pull request

## Contribution Guidelines

### For Profiles

When submitting a profile:

1. **Create a directory** in `profiles/` with a descriptive name:
   - Example: `discord-bots`, `photo-editing`, `productivity-tools`
   - Use lowercase with hyphens for consistency
   - **Do NOT use** the `profileN_Name` format in this repository
   - Users will rename profiles to `profileN_Name` when deploying to their device based on their preferences
2. **Include all necessary files**:
   - `config.txt` - Profile configuration
   - `keyN.txt` - Key scripts (one per key)
   - `README.md` - Profile description and usage instructions
3. **Document the profile**:
   - Describe what it does
   - List prerequisites
   - Note platform compatibility (Windows/macOS/Linux)
   - Provide usage instructions
4. **Test thoroughly** on actual duckyPad Pro hardware if possible

Example structure:

```
profiles/
└── developer-tools/
    ├── config.txt
    ├── key1.txt
    ├── key2.txt
    ├── key3.txt
    ├── key4.txt
    └── README.md
```

**Note**: Each profile's README should explain the deployment naming convention (users rename to `profileN_Name` when copying to SD card).

### For Scripts

When submitting standalone scripts:

1. **Place in appropriate category**:
2. **Use descriptive filenames**: `my-workflow.txt`, not `profile1.txt`
3. **Add comments** explaining:
   - What the script does
   - Platform requirements
   - Any prerequisites
4. **Test the script** before submitting

Example script:

```
REM Script: Open VS Code
REM Description: Opens Visual Studio Code using Spotlight
REM Platform: macOS
REM Prerequisites: VS Code installed

COMMAND SPACE
DELAY 500
STRING visual studio code
DELAY 300
ENTER
```

### For Helper Utilities

When submitting helper tools:

1. **Place in appropriate category**:
   - `helpers/converters/` - Format converters
   - `helpers/generators/` - Template generators
   - `helpers/validators/` - Validation tools
   - `helpers/utilities/` - General utilities
2. **Include a README** with:
   - Purpose and functionality
   - Installation instructions
   - Usage examples
   - Dependencies
3. **List dependencies** in appropriate file:
   - Python: `requirements.txt`
   - Node.js: `package.json`
   - Others: Document in README
4. **Make scripts executable** (if applicable):
   ```bash
   chmod +x script.py
   ```
5. **Use shebang lines**:
   ```python
   #!/usr/bin/env python3
   ```

### For Documentation

When improving documentation:

1. **Use clear language**: Write for all skill levels
2. **Provide examples**: Show, don't just tell
3. **Test instructions**: Verify steps work as written
4. **Update existing docs**: Keep documentation current
5. **Fix typos and errors**: Every improvement helps

## Code Style

### duckyScript

- Use `REM` comments to document scripts
- Use consistent indentation for readability
- Include delays between commands
- Use UPPERCASE for commands

### Python

- Follow PEP 8 style guide
- Include docstrings for functions
- Use meaningful variable names
- Add type hints where helpful

### JavaScript

- Use modern ES6+ syntax
- Follow standard JavaScript conventions
- Include JSDoc comments
- Handle errors appropriately

## Testing

Before submitting:

1. **Test on actual hardware** if possible
2. **Verify platform compatibility**
3. **Check for errors** in scripts and code
4. **Review documentation** for clarity

## Pull Request Process

1. **Update documentation** if you're adding new features
2. **Test your changes** thoroughly
3. **Commit with clear messages**:
   - ✅ Good: "Add Windows productivity profile with 8 shortcuts"
   - ❌ Bad: "Update files"
4. **Submit PR** with description of changes
5. **Respond to feedback** from reviewers

## Commit Message Guidelines

Use clear, descriptive commit messages:

```
Add productivity profile for macOS developers

- Includes shortcuts for VS Code, Terminal, and Browser
- Tested on macOS Sonoma
- Includes configuration for 8 keys
```

## Questions?

- Check existing [issues](https://github.com/JamesDBartlett3/duckyPadPro/issues)
- Review [documentation](docs/)
- Open a new issue for questions

## License

By contributing, you agree that your contributions will be licensed under the GNU General Public License v3.0.

## Thank You!

Your contributions help make this resource valuable for the entire duckyPad Pro community!
