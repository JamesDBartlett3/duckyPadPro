#!/usr/bin/env python3
"""
duckyPad Pro Repository Setup

Downloads and configures all external dependencies needed to use this repository:
1. Compiler files from duckyPad-Configurator (tools/vendor/)
2. Sample profiles from duckyPad-Pro (profiles/sample_profiles/)
3. Creates workbench directory structure

Run this script through uv after syncing the managed Python environment.
"""

import argparse
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


def setup_compiler(verbose: bool = False, force: bool = False) -> bool:
    """Download compiler files from duckyPad-Configurator
    
    Returns:
        True if successful, False otherwise
    """
    print_color("\n" + "=" * 60, "cyan")
    print_color("Step 1: Setting up duckyScript compiler", "cyan")
    print_color("=" * 60, "cyan")
    
    try:
        from vendor import CompilerUpdater
        
        updater = CompilerUpdater(verbose=verbose, force=force)
        success = updater.update() == 0
        
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
    print_color("Step 2: Downloading sample profiles", "cyan")
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
    print_color("Step 3: Setting up workbench directory", "cyan")
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
# Edit this file, then run with the dpp launcher:
#   PowerShell: .\\dpp workbench/my-first-profile.yaml
#   Command Prompt: dpp workbench/my-first-profile.yaml
#   Bash (macOS/Linux): ./dpp.sh workbench/my-first-profile.yaml

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
This script downloads resources not included in the repository:

    1. Compiler files (tools/vendor/)
    - Downloads from duckyPad/duckyPad-Configurator GitHub releases
    - Required to compile duckyScript to bytecode
  
    2. Sample profiles (profiles/sample_profiles/)
    - Downloads from dekuNukem/duckyPad-Pro repository
    - Official example profiles for reference
  
    3. Workbench directory (workbench/)
    - Creates directory structure for your YAML profile templates
    - Includes a starter template to get you going

After setup, try:
    PowerShell: .\\dpp generate workbench/my-first-profile.yaml
    Command Prompt: dpp generate workbench/my-first-profile.yaml
    Bash (macOS/Linux): ./dpp.sh generate workbench/my-first-profile.yaml
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
    
    # Step 1: Compiler
    if not args.skip_compiler:
        if not setup_compiler(args.verbose, args.force):
            success = False
    else:
        print_color("\n⏭ Skipping compiler setup (--skip-compiler)", "yellow")
    
    # Step 2: Sample profiles
    if not args.skip_samples:
        if not setup_sample_profiles(args.verbose, args.force):
            success = False
    else:
        print_color("\n⏭ Skipping sample profiles (--skip-samples)", "yellow")
    
    # Step 3: Workbench
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
        print_color("  2. Run: .\\dpp workbench/my-first-profile.yaml (PowerShell)", "white")
        print_color("          dpp workbench/my-first-profile.yaml (Command Prompt)", "white")
        print_color("          ./dpp.sh workbench/my-first-profile.yaml (Bash on macOS/Linux)", "white")
        print_color("  3. Connect your duckyPad Pro and test!", "white")
        print_color("\nFor help: .\\dpp --help (PowerShell), dpp --help (Command Prompt),", "gray")
        print_color("          or ./dpp.sh --help (Bash on macOS/Linux)", "gray")
    else:
        print_color("⚠ Setup completed with some errors", "yellow")
        print_color("  Check the messages above for details", "gray")
    print_color("=" * 60, "cyan")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
