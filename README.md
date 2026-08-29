# duckyPadPro

A community repository for [duckyPad Pro](https://dekunukem.github.io/duckyPad-Pro/) profiles, settings, scripts, and helper utilities.

## Warning

This code is provided "as is" without warranty of any kind. Use at your own risk. The authors are not responsible for any damage to your device or data.

## About duckyPad Pro

The duckyPad Pro is a powerful macro keyboard that uses [duckyScript](https://dekunukem.github.io/duckyPad-Pro/doc/duckyscript_info.html) to automate tasks, execute keyboard shortcuts, and streamline workflows.

## Installation

### Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- duckyPad Pro device (for deployment)

### Setup

After cloning the repository, sync the locked environment and download the external resources:

```bash
git clone https://github.com/JamesDBartlett3/duckyPadPro.git
cd duckyPadPro
uv sync --locked
uv run --locked python setup.py
```

`uv sync` downloads a managed CPython 3.12 interpreter when needed, creates an isolated `.venv`, and installs the exact dependency versions from `uv.lock`. The setup script then downloads:

- **Compiler files** (`tools/vendor/`) - Required to compile duckyScript to bytecode
- **Sample profiles** (`profiles/sample_profiles/`) - Official example profiles
- **Workbench template** (`workbench/`) - Starter YAML template for your profiles

Use `uv add <package>` to change dependencies and commit the resulting `pyproject.toml` and `uv.lock` updates. Do not install packages directly into `.venv`.

## Quick Start

After setup, use the unified launcher to work with duckyPad Pro:

Use `.\dpp` in PowerShell, `dpp` in Command Prompt, or `./dpp.sh` in Bash on macOS/Linux. The examples below use PowerShell.

```powershell
# Create your first profile from the sample template
.\dpp workbench/my-first-profile.yaml

# Or try with sample profiles
.\dpp compile profiles/sample_profiles/profile1_Welcome
.\dpp deploy profiles/sample_profiles/profile1_Welcome

# Device control
.\dpp device scan
.\dpp device mount

# Backup and restore
.\dpp backup
.\dpp restore
```

Run `.\dpp --help` (PowerShell), `dpp --help` (Command Prompt), or `./dpp.sh --help` (Bash on macOS/Linux) to see all available commands.

## Repository Structure

```
duckyPadPro/
├── dpp.ps1 / dpp.bat  # PowerShell and Command Prompt launchers
├── dpp.sh             # Bash launcher for macOS/Linux
├── execute.py         # Unified command implementation
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
