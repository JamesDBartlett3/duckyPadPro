#!/usr/bin/env python3
"""
duckyPad Pro Orchestrator
Complete workflow: generate → compile → deploy profiles

Usage examples:
    # Full workflow: generate, compile, and deploy
    python duckypad.py new discord-tools 20
    
    # Generate only
    python duckypad.py new discord-tools 20 --generate-only
    
    # Compile existing profiles
    python duckypad.py compile profiles/my-profile
    
    # Deploy existing profiles
    python duckypad.py deploy profiles/my-profile
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

# Add shared directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import tool functions
from generate_profile import generate_profile
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


def cmd_new(args):
    """Create new profile, compile, and optionally deploy"""
    profile_name = args.profile_name
    num_keys = args.num_keys
    output_dir = args.output or Path("profiles")
    
    # Step 1: Generate profile
    print_header(f"Step 1: Generating profile '{profile_name}'")
    try:
        profile_path = generate_profile(profile_name, num_keys, output_dir)
        print_color(f"✓ Profile generated: {profile_path}", Colors.GREEN)
    except Exception as e:
        print_color(f"✗ Generation failed: {e}", Colors.RED)
        return 1
    
    if args.generate_only:
        print_color("\n✓ Generation complete (--generate-only flag set)", Colors.GREEN)
        return 0
    
    # Step 2: Compile profile
    print_header(f"Step 2: Compiling profile '{profile_name}'")
    exit_code = compile_profiles(
        profile_path=profile_path,
        verbose=args.verbose,
        resolve_profiles=not args.no_resolve_profiles
    )
    
    if exit_code != 0:
        print_color("\n✗ Compilation failed", Colors.RED)
        return exit_code
    
    if args.compile_only:
        print_color("\n✓ Compilation complete (--compile-only flag set)", Colors.GREEN)
        return 0
    
    # Step 3: Deploy profile
    if not args.skip_deploy:
        print_header(f"Step 3: Deploying profile '{profile_name}'")
        exit_code = deploy_profiles(
            source_profiles=[profile_path],
            backup_path=args.backup_path,
            verbose=args.verbose,
            force=args.force
        )
        
        if exit_code != 0:
            print_color("\n✗ Deployment failed", Colors.RED)
            return exit_code
    
    print_header("✓ All steps complete!")
    print_color(f"Profile '{profile_name}' is ready on your duckyPad Pro", Colors.GREEN)
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
  # Create, compile, and deploy new profile
  python duckypad.py new discord-tools 20
  
  # Create and compile only (skip deployment)
  python duckypad.py new discord-tools 20 --skip-deploy
  
  # Create only (no compilation or deployment)
  python duckypad.py new discord-tools 20 --generate-only
  
  # Compile existing profiles
  python duckypad.py compile profiles/my-profile
  
  # Deploy existing profiles
  python duckypad.py deploy profiles/profile1 profiles/profile2
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # 'new' command - create new profile
    new_parser = subparsers.add_parser("new", help="Create new profile")
    new_parser.add_argument("profile_name", help="Profile name")
    new_parser.add_argument("num_keys", type=int, help="Number of keys (1-26)")
    new_parser.add_argument("-o", "--output", type=Path, help="Output directory (default: profiles/)")
    new_parser.add_argument("--generate-only", action="store_true", help="Only generate, skip compile and deploy")
    new_parser.add_argument("--compile-only", action="store_true", help="Generate and compile, skip deploy")
    new_parser.add_argument("--skip-deploy", action="store_true", help="Skip deployment step")
    new_parser.add_argument("--no-resolve-profiles", action="store_true", help="Disable GOTO_PROFILE name resolution")
    new_parser.add_argument("-b", "--backup-path", type=Path, help="Custom backup location")
    new_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    new_parser.add_argument("-f", "--force", action="store_true", help="Skip confirmation prompts")
    new_parser.set_defaults(func=cmd_new)
    
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
