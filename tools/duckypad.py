#!/usr/bin/env python3
"""
duckyPad Pro Orchestrator
Complete workflow: generate → compile → deploy profiles

Usage examples:
    # Full YAML workflow: generate, compile, and deploy
    python duckypad.py yaml workbench/my-profile.yaml -f
    
    # Generate from YAML only
    python duckypad.py yaml workbench/my-profile.yaml --generate-only
    
    # Compile existing profiles
    python duckypad.py compile workbench/profiles/my-profile
    
    # Deploy existing profiles
    python duckypad.py deploy workbench/profiles/my-profile
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

# Add shared directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import tool functions
from generate_profile_from_yaml import YAMLToProfileConverter
from compile import compile as compile_profiles
from deploy import deploy as deploy_profiles


class Colors:
    """ANSI color codes"""
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RESET = "\033[0m"


def print_color(message: str, color: str):
    """Print colored message"""
    print(f"{color}{message}{Colors.RESET}")


def print_header(message: str):
    """Print section header"""
    print()
    print("=" * 60)
    print_color(message, Colors.CYAN)
    print("=" * 60)


def cmd_yaml(args):
    """Generate profiles from YAML, compile, and optionally deploy"""
    yaml_path = args.yaml_file
    
    if not yaml_path.exists():
        print_color(f"✗ YAML file not found: {yaml_path}", Colors.RED)
        return 1
    
    # Step 1: Generate profiles from YAML
    print_header(f"Step 1: Generating profiles from '{yaml_path.name}'")
    try:
        converter = YAMLToProfileConverter(yaml_path, verbose=args.verbose)
        profile_paths = converter.convert()
        
        print_color(f"✓ Generated {len(profile_paths)} profile(s):", Colors.GREEN)
        for path in profile_paths:
            print_color(f"  • {path}", Colors.CYAN)
    except Exception as e:
        print_color(f"✗ Generation failed: {e}", Colors.RED)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    if args.generate_only:
        print_color("\n✓ Generation complete (--generate-only flag set)", Colors.GREEN)
        return 0
    
    # Step 2: Compile all generated profiles
    print_header(f"Step 2: Compiling {len(profile_paths)} profile(s)")
    
    for profile_path in profile_paths:
        print_color(f"\nCompiling: {profile_path.name}", Colors.CYAN)
        exit_code = compile_profiles(
            profile_path=profile_path,
            verbose=args.verbose,
            resolve_profiles=not args.no_resolve_profiles
        )
        
        if exit_code != 0:
            print_color(f"\n✗ Compilation failed for {profile_path.name}", Colors.RED)
            return exit_code
    
    if args.compile_only:
        print_color("\n✓ Compilation complete (--compile-only flag set)", Colors.GREEN)
        return 0
    
    # Step 3: Deploy all profiles and update profile_info.txt
    if not args.skip_deploy:
        print_header(f"Step 3: Deploying {len(profile_paths)} profile(s)")
        
        exit_code = deploy_profiles(
            source_profiles=profile_paths,
            backup_path=args.backup_path,
            verbose=args.verbose,
            force=args.force
        )
        
        if exit_code != 0:
            print_color("\n✗ Deployment failed", Colors.RED)
            return exit_code
    
    print_header("✓ All steps complete!")
    print_color(f"YAML workflow complete: {len(profile_paths)} profile(s) ready", Colors.GREEN)
    return 0


def cmd_compile(args):
    """Compile existing profiles"""
    print_header("Compiling profiles")
    return compile_profiles(
        profile_path=args.profile_path,
        verbose=args.verbose,
        resolve_profiles=not args.no_resolve_profiles
    )


def cmd_deploy(args):
    """Deploy existing profiles"""
    print_header("Deploying profiles")
    return deploy_profiles(
        source_profiles=args.profiles,
        backup_path=args.backup_path,
        verbose=args.verbose,
        force=args.force
    )


def main():
    """Main orchestrator entry point"""
    parser = argparse.ArgumentParser(
        description="duckyPad Pro workflow orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate, compile, and deploy from YAML
  python duckypad.py yaml workbench/layer_type_test.yaml -f
  
  # Generate from YAML only (no compile/deploy)
  python duckypad.py yaml workbench/layer_type_test.yaml --generate-only
  
  # Compile existing profiles
  python duckypad.py compile workbench/profiles/my-profile
  
  # Deploy existing profiles
  python duckypad.py deploy workbench/profiles/profile1 workbench/profiles/profile2
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # 'yaml' command - generate from YAML template
    yaml_parser = subparsers.add_parser("yaml", help="Generate profiles from YAML template")
    yaml_parser.add_argument("yaml_file", type=Path, help="YAML template file")
    yaml_parser.add_argument("--generate-only", action="store_true", help="Only generate, skip compile and deploy")
    yaml_parser.add_argument("--compile-only", action="store_true", help="Generate and compile, skip deploy")
    yaml_parser.add_argument("--skip-deploy", action="store_true", help="Skip deployment step")
    yaml_parser.add_argument("--no-resolve-profiles", action="store_true", help="Disable GOTO_PROFILE name resolution")
    yaml_parser.add_argument("-b", "--backup-path", type=Path, help="Custom backup location")
    yaml_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    yaml_parser.add_argument("-f", "--force", action="store_true", help="Skip confirmation prompts")
    yaml_parser.set_defaults(func=cmd_yaml)
    
    # 'compile' command - compile existing profiles
    compile_parser = subparsers.add_parser("compile", help="Compile existing profiles")
    compile_parser.add_argument("profile_path", type=Path, nargs="?", help="Profile path (default: profiles/)")
    compile_parser.add_argument("--no-resolve-profiles", action="store_true", help="Disable GOTO_PROFILE name resolution")
    compile_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    compile_parser.set_defaults(func=cmd_compile)
    
    # 'deploy' command - deploy existing profiles
    deploy_parser = subparsers.add_parser("deploy", help="Deploy existing profiles")
    deploy_parser.add_argument("profiles", type=Path, nargs="+", help="Profile directories to deploy")
    deploy_parser.add_argument("-b", "--backup-path", type=Path, help="Custom backup location")
    deploy_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    deploy_parser.add_argument("-f", "--force", action="store_true", help="Skip confirmation prompts")
    deploy_parser.set_defaults(func=cmd_deploy)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Run the selected command
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
