# duckyPadPro

A community repository for [duckyPad Pro](https://dekunukem.github.io/duckyPad-Pro/) profiles, settings, scripts, and helper utilities.

## Warning

This code is provided "as is" without warranty of any kind. Use at your own risk. The authors are not responsible for any damage to your device or data.

## About duckyPad Pro

The duckyPad Pro is a powerful macro keyboard that uses [duckyScript](https://dekunukem.github.io/duckyPad-Pro/doc/duckyscript_info.html) to automate tasks, execute keyboard shortcuts, and streamline workflows.

## Installation

### Prerequisites

- Python 3.8 or higher
- duckyPad Pro device (for deployment)

### Setup

After cloning the repository, run the setup script to download required dependencies:

```bash
git clone https://github.com/JamesDBartlett3/duckyPadPro.git
cd duckyPadPro
python setup.py
```

This installs and downloads:

- **Python packages** - PyYAML (for profile generation), hidapi (for USB device control)
- **Compiler files** (`tools/vendor/`) - Required to compile duckyScript to bytecode
- **Sample profiles** (`profiles/sample_profiles/`) - Official example profiles
- **Workbench template** (`workbench/`) - Starter YAML template for your profiles

**Alternative manual installation:**

```bash
pip install -r requirements.txt
python tools/vendor.py
python tests/get_sample_profiles.py
```

## Quick Start

After setup, use the unified launcher to work with duckyPad Pro:

```bash
# Create your first profile from the sample template
python execute.py yaml workbench/my-first-profile.yaml

# Or try with sample profiles
python execute.py compile profiles/sample_profiles/profile1_Welcome
python execute.py deploy profiles/sample_profiles/profile1_Welcome

# Device control
python execute.py device scan
python execute.py device mount

# Backup and restore
python execute.py backup
python execute.py restore
```

Run `python execute.py --help` to see all available commands.

## Repository Structure

```
duckyPadPro/
├── execute.py         # Main launcher (unified interface to all tools)
├── profiles/          # Complete duckyPad Pro profiles
├── tools/             # Helper utilities and development tools
└── docs/              # Documentation and guides
```

### 📁 Profiles

Complete profile packages for the duckyPad Pro, organized by use case. Each profile contains:

- Configuration file (`config.txt`)
- Key scripts (`key1.txt`, `key2.txt`, etc.)

See the [profiles directory](profiles/readme-profiles.md) for available profiles.

### 🛠️ Tools

Helper utilities and development tools written in Python:

- **Profile generation**: Generate profiles from YAML templates
- **Compilation**: Compile duckyScript to bytecode
- **Deployment**: Deploy profiles to duckyPad Pro
- **Backup/Restore**: Backup and restore SD card contents

See the [tools directory](tools/readme-tools.md) for available utilities.

## Getting Started

1. **Explore** the [documentation](docs/readme-docs.md) to learn about duckyPad Pro
2. **Browse** [profiles](profiles/readme-profiles.md) for ideas
3. **Create** your own profiles using the [YAML workflow](profiles/readme-profiles.md#yaml-profile-system)
4. **Use** the [tools](tools/readme-tools.md) to compile and deploy your profiles

For complete setup instructions, see the [Getting Started Guide](docs/getting-started.md).

## Contributing

Contributions are welcome! Whether you have:

- A new profile to share
- Helper utilities
- Documentation improvements

Please see the [Contributing Guide](docs/readme-contributing.md) for detailed guidelines.

## Resources

- [duckyPad Pro Official Site](https://dekunukem.github.io/duckyPad-Pro/)
- [duckyScript Documentation](https://dekunukem.github.io/duckyPad-Pro/doc/duckyscript_info.html)
- [duckyPad Pro User Guide](https://dekunukem.github.io/duckyPad-Pro/doc/getting_started.html)

## License

This repository is licensed under the GNU General Public License v3.0. See [LICENSE](LICENSE) for details.
