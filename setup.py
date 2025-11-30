#!/usr/bin/env python3
"""
duckyPad Pro Repository Setup

Downloads and configures all external dependencies needed to use this repository:
1. Python packages (PyYAML, hidapi)
2. Compiler files from duckyPad-Configurator (tools/vendor/)
3. Sample profiles from duckyPad-Pro (profiles/sample_profiles/)
4. Creates workbench directory structure

Run this script after cloning the repository to set up your development environment.
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent / "tools"))


def print_color(message: str, color: str = "white"):
    """Print colored message"""
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "gray": "\033[90m",
        "reset": "\033[0m",
    }
    print(f"{colors.get(color, colors['white'])}{message}{colors['reset']}")


def check_package_installed(package_name: str) -> bool:
    """Check if a Python package is installed
    
    Args:
        package_name: The import name of the package (e.g., 'yaml' for PyYAML)
    
    Returns:
        True if package is installed, False otherwise
    """
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False


def install_dependencies(verbose: bool = False, force: bool = False) -> bool:
    """Install required Python packages from requirements.txt
    
    Returns:
        True if successful (or all packages already installed), False on error
    """
    print_color("\n" + "=" * 60, "cyan")
    print_color("Step 1: Installing Python dependencies", "cyan")
    print_color("=" * 60, "cyan")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    # Check if requirements.txt exists
    if not requirements_file.exists():
        print_color("✗ requirements.txt not found", "red")
        return False
    
    # Package mapping: pip package name -> import name
    packages = {
        "PyYAML": "yaml",
        "hidapi": "hid"
    }
    
    # Check which packages need installation
    packages_to_install = []
    for pip_name, import_name in packages.items():
        if force or not check_package_installed(import_name):
            packages_to_install.append(pip_name)
            if verbose:
                print_color(f"  Need to install: {pip_name}", "gray")
        else:
            print_color(f"  ✓ {pip_name} already installed", "green")
    
    if not packages_to_install:
        print_color("✓ All Python dependencies already installed", "green")
        return True
    
    # Install missing packages
    print_color(f"  Installing: {', '.join(packages_to_install)}", "yellow")
    
    try:
        cmd = [sys.executable, "-m", "pip", "install"]
        if not verbose:
            cmd.append("-q")  # Quiet mode
        cmd.extend(packages_to_install)
        
        result = subprocess.run(cmd, capture_output=not verbose, text=True)
        
        if result.returncode != 0:
            print_color(f"✗ pip install failed", "red")
            if result.stderr:
                print_color(f"  {result.stderr}", "red")
            print_color("\nTry installing manually:", "yellow")
            print_color(f"  pip install -r {requirements_file}", "white")
            return False
        
        # Verify installation
        all_installed = True
        for pip_name, import_name in packages.items():
            if pip_name in packages_to_install:
                if check_package_installed(import_name):
                    print_color(f"  ✓ {pip_name} installed successfully", "green")
                else:
                    print_color(f"  ✗ {pip_name} installation verification failed", "red")
                    all_installed = False
        
        if all_installed:
            print_color("✓ Python dependencies installed", "green")
        return all_installed
        
    except Exception as e:
        print_color(f"✗ Failed to install dependencies: {e}", "red")
        print_color("\nTry installing manually:", "yellow")
        print_color(f"  pip install -r {requirements_file}", "white")
        return False


def setup_compiler(verbose: bool = False, force: bool = False) -> bool:
    """Download compiler files from duckyPad-Configurator
    
    Returns:
        True if successful, False otherwise
    """
    print_color("\n" + "=" * 60, "cyan")
    print_color("Step 2: Setting up duckyScript compiler", "cyan")
    print_color("=" * 60, "cyan")
    
    try:
        from vendor import CompilerUpdater
        
        updater = CompilerUpdater(verbose=verbose, force=force)
        success = updater.update()
        
        if success:
            print_color("✓ Compiler setup complete", "green")
        return success
        
    except Exception as e:
        print_color(f"✗ Compiler setup failed: {e}", "red")
        return False


def setup_sample_profiles(verbose: bool = False, force: bool = False) -> bool:
    """Download sample profiles from duckyPad-Pro repository
    
    Returns:
        True if successful, False otherwise
    """
    print_color("\n" + "=" * 60, "cyan")
    print_color("Step 3: Downloading sample profiles", "cyan")
    print_color("=" * 60, "cyan")
    
    # Add tests directory to path
    tests_dir = Path(__file__).parent / "tests"
    sys.path.insert(0, str(tests_dir))
    
    try:
        from get_sample_profiles import SampleProfilesDownloader
        
        downloader = SampleProfilesDownloader(force=force, verbose=verbose)
        success = downloader.download()
        
        if success:
            print_color("✓ Sample profiles setup complete", "green")
        return success
        
    except Exception as e:
        print_color(f"✗ Sample profiles setup failed: {e}", "red")
        return False


def setup_workbench(verbose: bool = False) -> bool:
    """Create workbench directory structure
    
    Returns:
        True if successful, False otherwise
    """
    print_color("\n" + "=" * 60, "cyan")
    print_color("Step 4: Setting up workbench directory", "cyan")
    print_color("=" * 60, "cyan")
    
    workbench_dir = Path(__file__).parent / "workbench"
    profiles_dir = workbench_dir / "profiles"
    
    try:
        # Create workbench directories
        workbench_dir.mkdir(exist_ok=True)
        profiles_dir.mkdir(exist_ok=True)
        
        # Create a sample YAML template if none exists
        sample_yaml = workbench_dir / "my-first-profile.yaml"
        if not sample_yaml.exists():
            sample_yaml.write_text("""# My First duckyPad Pro Profile
# Edit this file and run: python execute.py yaml workbench/my-first-profile.yaml

profile:
  name: MyFirstProfile
  
  config:
    orientation: portrait
    background_color: [50, 50, 80]
  
  keys:
    # Key 1: Type "Hello World"
    1:
      label: [Hello]
      color: [0, 255, 0]
      script: |
        STRING Hello World!
        ENTER
    
    # Key 2: Copy (Ctrl+C)
    2:
      label: [Copy]
      color: [100, 100, 255]
      script: |
        CONTROL C
    
    # Key 3: Paste (Ctrl+V)
    3:
      label: [Paste]
      color: [100, 100, 255]
      script: |
        CONTROL V
    
    # Volume control on first rotary encoder
    21:
      script: MK_VOLUP
    
    22:
      script: MK_VOLDOWN
    
    23:
      script: MK_MUTE
""")
            if verbose:
                print_color(f"  Created: {sample_yaml}", "gray")
        
        print_color(f"✓ Workbench directory ready: {workbench_dir}", "green")
        print_color(f"  Sample template: {sample_yaml.name}", "gray")
        return True
        
    except Exception as e:
        print_color(f"✗ Workbench setup failed: {e}", "red")
        return False


def main():
    """Main setup entry point"""
    parser = argparse.ArgumentParser(
        description="Set up duckyPad Pro repository after cloning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script installs and downloads dependencies not included in the repository:

  1. Python packages (PyYAML, hidapi)
    - Required for YAML parsing and USB device communication
    - Installed via pip from requirements.txt
  
  2. Compiler files (tools/vendor/)
    - Downloads from duckyPad/duckyPad-Configurator GitHub releases
    - Required to compile duckyScript to bytecode
  
  3. Sample profiles (profiles/sample_profiles/)  
    - Downloads from dekuNukem/duckyPad-Pro repository
    - Official example profiles for reference
  
  4. Workbench directory (workbench/)
    - Creates directory structure for your YAML profile templates
    - Includes a starter template to get you going

After setup, try:
  python execute.py yaml workbench/my-first-profile.yaml --generate-only
        """
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Force re-download/reinstall even if files exist"
    )
    parser.add_argument(
        "--skip-deps",
        action="store_true",
        help="Skip Python dependency installation"
    )
    parser.add_argument(
        "--skip-compiler",
        action="store_true",
        help="Skip compiler setup"
    )
    parser.add_argument(
        "--skip-samples",
        action="store_true",
        help="Skip sample profiles download"
    )
    parser.add_argument(
        "--skip-workbench",
        action="store_true",
        help="Skip workbench setup"
    )
    
    args = parser.parse_args()
    
    print_color("\n" + "=" * 60, "cyan")
    print_color("duckyPad Pro Repository Setup", "cyan")
    print_color("=" * 60, "cyan")
    
    success = True
    
    # Step 1: Python dependencies
    if not args.skip_deps:
        if not install_dependencies(args.verbose, args.force):
            success = False
    else:
        print_color("\n⏭ Skipping dependency installation (--skip-deps)", "yellow")
    
    # Step 2: Compiler
    if not args.skip_compiler:
        if not setup_compiler(args.verbose, args.force):
            success = False
    else:
        print_color("\n⏭ Skipping compiler setup (--skip-compiler)", "yellow")
    
    # Step 3: Sample profiles
    if not args.skip_samples:
        if not setup_sample_profiles(args.verbose, args.force):
            success = False
    else:
        print_color("\n⏭ Skipping sample profiles (--skip-samples)", "yellow")
    
    # Step 4: Workbench
    if not args.skip_workbench:
        if not setup_workbench(args.verbose):
            success = False
    else:
        print_color("\n⏭ Skipping workbench setup (--skip-workbench)", "yellow")
    
    # Summary
    print_color("\n" + "=" * 60, "cyan")
    if success:
        print_color("✓ Setup complete!", "green")
        print_color("\nNext steps:", "cyan")
        print_color("  1. Edit workbench/my-first-profile.yaml", "white")
        print_color("  2. Run: python execute.py yaml workbench/my-first-profile.yaml", "white")
        print_color("  3. Connect your duckyPad Pro and test!", "white")
        print_color("\nFor help: python execute.py --help", "gray")
    else:
        print_color("⚠ Setup completed with some errors", "yellow")
        print_color("  Check the messages above for details", "gray")
    print_color("=" * 60, "cyan")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
