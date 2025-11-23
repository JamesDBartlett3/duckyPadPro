# duckyPadPro

A community repository for [duckyPad Pro](https://dekunukem.github.io/duckyPad-Pro/) profiles, settings, scripts, and helper utilities.

## Warning

This code is provided "as is" without warranty of any kind. Use at your own risk. The authors are not responsible for any damage to your device or data.

## About duckyPad Pro

The duckyPad Pro is a powerful macro keyboard that uses [duckyScript](https://dekunukem.github.io/duckyPad-Pro/doc/duckyscript_info.html) to automate tasks, execute keyboard shortcuts, and streamline workflows.

## Quick Start

The easiest way to work with duckyPad Pro is using the unified launcher:

```bash
# YAML workflow: generate, compile, and deploy profiles
python execute.py yaml workbench/my-profile.yaml

# Device control
python execute.py device scan
python execute.py device mount

# Backup and restore
python execute.py backup
python execute.py restore

# Individual operations
python execute.py compile profiles/my-profile
python execute.py deploy profiles/my-profile
```

Run `python execute.py --help` to see all available commands.

## Repository Structure

```
duckyPadPro/
├── execute.py         # Main launcher (unified interface to all tools)
├── profiles/          # Complete duckyPad Pro profiles
├── scripts/           # Standalone duckyScript files
├── tools/             # Helper utilities and development tools
└── docs/              # Documentation and guides
```

### 📁 Profiles

Complete profile packages for the duckyPad Pro, organized by use case. Each profile contains:

- Configuration file (`config.txt`)
- Key scripts (`key1.txt`, `key2.txt`, etc.)
- Documentation (`README.md`)

See the [profiles directory](profiles/readme-profiles.md) for available profiles.

### 📜 Scripts

Standalone duckyScript files organized by category:

- **productivity**: Workflow automation and productivity enhancers
- **development**: Developer tools and shortcuts
- **system**: System administration tasks
- **media**: Media control scripts

See the [scripts directory](scripts/readme-scripts.md) for available scripts.

### 🛠️ Tools

Helper utilities and development tools written in Python:

- **Profile generation**: Generate profiles from YAML templates
- **Compilation**: Compile duckyScript to bytecode
- **Deployment**: Deploy profiles to duckyPad Pro
- **Backup/Restore**: Backup and restore SD card contents

See the [tools directory](tools/readme-tools.md) for available utilities.

## Getting Started

1. **Explore** the [documentation](docs/readme-docs.md) to learn about duckyPad Pro
2. **Browse** [profiles](profiles/readme-profiles.md) and [scripts](scripts/readme-scripts.md) for ideas
3. **Create** your own profiles using the [YAML workflow](profiles/readme-profiles.md#yaml-profile-system)
4. **Use** the [tools](tools/readme-tools.md) to compile and deploy your profiles

For complete setup instructions, see the [Getting Started Guide](docs/getting-started.md).

## Contributing

Contributions are welcome! Whether you have:

- A new profile to share
- Useful scripts
- Helper utilities
- Documentation improvements

Please feel free to submit a pull request.

### Contribution Guidelines

1. **Profiles**: Include a README describing the profile's purpose
2. **Scripts**: Add comments explaining what the script does
3. **Tools**: Include usage instructions and requirements
4. **Test**: Verify your contributions work on duckyPad Pro

## Resources

- [duckyPad Pro Official Site](https://dekunukem.github.io/duckyPad-Pro/)
- [duckyScript Documentation](https://dekunukem.github.io/duckyPad-Pro/doc/duckyscript_info.html)
- [duckyPad Pro User Guide](https://dekunukem.github.io/duckyPad-Pro/doc/getting_started.html)

## License

This repository is licensed under the GNU General Public License v3.0. See [LICENSE](LICENSE) for details.
