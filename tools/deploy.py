#!/usr/bin/env python3
"""
Profile Deployment Manager
Backs up SD card, deploys profiles to duckyPad, updates profile_info.txt
"""

import argparse
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add shared directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from shared.profiles import ProfileInfoManager
from shared.console import print_color, print_verbose, prompt_yes_no
from shared.validators import (
    ValidationError,
    validate_profile_count,
    validate_profile_name,
    require_valid_profile_count,
    require_valid_profile_name,
    MAX_PROFILES,
)
from backup import backup_sd_card


class DeploymentStats:
    """Track deployment statistics"""
    def __init__(self):
        self.backed_up = 0
        self.deployed = 0
        self.skipped = 0
        self.failed = 0
        self.validation_failed = 0
    
    def add_validation_failure(self):
        """Mark validation failure"""
        self.validation_failed += 1
        self.failed += 1


class ProfileDeployer:
    """Deploy profiles to duckyPad SD card with backup"""
    
    def __init__(self, verbose: bool = False, force: bool = False, auto_unmount: bool = False):
        """Initialize deployer
        
        Args:
            verbose: Enable verbose output
            force: Skip confirmations
            auto_unmount: Always unmount SD card after deployment (even if already mounted)
        """
        self.verbose = verbose
        self.force = force
        self.auto_unmount = auto_unmount
        self.profile_manager = ProfileInfoManager()
    
    def find_next_profile_number(self, sd_card_path: Path) -> int:
        """Find next available profile number on SD card
        
        Args:
            sd_card_path: Path to SD card
            
        Returns:
            Next available profile number (1-based)
        """
        existing_profiles = [
            d for d in sd_card_path.iterdir()
            if d.is_dir() and d.name.lower().startswith("profile")
        ]
        
        if not existing_profiles:
            return 1
        
        # Extract numbers from profile directories
        numbers = []
        for profile_dir in existing_profiles:
            try:
                # Extract number from "profileN_Name" format
                name_parts = profile_dir.name.split("_", 1)
                if name_parts[0].lower().startswith("profile"):
                    num_str = name_parts[0][7:]  # Skip "profile" prefix
                    if num_str.isdigit():
                        numbers.append(int(num_str))
            except (ValueError, IndexError):
                continue
        
        if not numbers:
            return 1
        
        return max(numbers) + 1
    
    def deploy_profile(self, source_path: Path, sd_card_path: Path, profile_number: int) -> bool:
        """Deploy a single profile to SD card
        
        Args:
            source_path: Path to source profile directory
            sd_card_path: Path to SD card
            profile_number: Profile number to assign (unused, kept for compatibility)
            
        Returns:
            True if successful, False otherwise
        """
        # Generate profile directory name (just profile_<name>, no number)
        profile_name = source_path.name
        dest_name = f"profile_{profile_name}"
        dest_path = sd_card_path / dest_name
        
        print_verbose(f"Deploying: {profile_name} → {dest_name}", self.verbose)
        
        try:
            # Check if destination already exists
            if dest_path.exists():
                print_color(f"  Warning: {dest_name} already exists", "yellow")
                if not prompt_yes_no(f"  Overwrite {dest_name}?", default=True, force=self.force):
                    print_color(f"  Skipped: {profile_name}", "yellow")
                    return False
                shutil.rmtree(dest_path)
            
            # Copy profile directory (excluding README files)
            def ignore_readme(directory, files):
                """Ignore README.md and readme files during copy"""
                return [f for f in files if f.upper().startswith('README')]
            
            shutil.copytree(source_path, dest_path, ignore=ignore_readme)
            
            print_color(f"  ✓ Deployed: {dest_name}", "green")
            return True
            
        except Exception as e:
            print_color(f"  ✗ Failed to deploy {profile_name}: {e}", "red")
            return False
    
    def update_profile_info(self, sd_card_path: Path) -> bool:
        """Update profile_info.txt with all profiles on SD card
        
        Automatically reads existing profile_info.txt from SD card, scans for all
        profile directories, and updates the file with all profiles (preserving
        existing profile numbers and adding new profiles at the end).
        
        Args:
            sd_card_path: Path to SD card
            
        Returns:
            True if successful, False otherwise
        """
        print_color("\n→ Updating profile_info.txt...", "cyan")
        
        try:
            profile_info_path = sd_card_path / "profile_info.txt"
            
            # Read existing profile_info.txt to preserve order
            existing_profiles = {}  # name -> number mapping
            if profile_info_path.exists():
                try:
                    with open(profile_info_path, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            parts = line.split(maxsplit=1)
                            if len(parts) == 2:
                                try:
                                    num = int(parts[0])
                                    name = parts[1]
                                    existing_profiles[name] = num
                                    print_verbose(f"Existing: {num} {name}", self.verbose)
                                except ValueError:
                                    continue
                except Exception as e:
                    print_verbose(f"Could not read existing profile_info.txt: {e}", self.verbose)
            
            # Find all profile directories on SD card
            all_dirs = sorted([
                d for d in sd_card_path.iterdir()
                if d.is_dir()
            ])
            
            if not all_dirs:
                print_color("  No directories found", "yellow")
                return False
            
            # Extract profile names from directories
            profile_names = []
            for profile_dir in all_dirs:
                dir_name = profile_dir.name
                
                # Extract name from "profileN_Name" format or use directory name
                if dir_name.lower().startswith("profile") and "_" in dir_name:
                    name_parts = dir_name.split("_", 1)
                    if len(name_parts) == 2:
                        profile_name = name_parts[1]
                    else:
                        continue
                elif dir_name.lower().startswith("profile"):
                    # Legacy format: use the whole directory name
                    profile_name = dir_name
                else:
                    # Not a profile directory, skip
                    continue
                
                profile_names.append(profile_name)
            
            if not profile_names:
                print_color("  No valid profiles found", "yellow")
                return False
            
            # Build final entries list
            # 1. Keep existing profiles in their original order
            # 2. Append new profiles at the end
            final_entries = []
            used_numbers = set()
            
            # Add existing profiles first (preserving order)
            for name in profile_names:
                if name in existing_profiles:
                    num = existing_profiles[name]
                    final_entries.append((num, name))
                    used_numbers.add(num)
                    print_verbose(f"Preserved: {num} {name}", self.verbose)
            
            # Sort existing entries by number to maintain order
            final_entries.sort(key=lambda x: x[0])
            
            # Find next available number for new profiles
            if used_numbers:
                next_number = max(used_numbers) + 1
            else:
                next_number = 1
            
            # Add new profiles at the end
            for name in profile_names:
                if name not in existing_profiles:
                    # Validate profile name before adding
                    valid, error = validate_profile_name(name)
                    if not valid:
                        print_color(f"  ⚠ Skipping invalid profile name '{name}': {error}", "yellow")
                        continue
                    
                    final_entries.append((next_number, name))
                    print_verbose(f"Added: {next_number} {name}", self.verbose)
                    next_number += 1
            
            # Write profile_info.txt
            with open(profile_info_path, "w", encoding="utf-8") as f:
                for profile_num, profile_name in final_entries:
                    f.write(f"{profile_num} {profile_name}\n")
            
            print_color(f"✓ Updated profile_info.txt with {len(final_entries)} profile(s)", "green")
            return True
            
        except Exception as e:
            print_color(f"✗ Failed to update profile_info.txt: {e}", "red")
            return False
    
    def run(self, source_profiles: List[Path], backup_path: Optional[Path] = None) -> int:
        """Run the deployment process
        
        Args:
            source_profiles: List of profile directories to deploy
            backup_path: Optional custom backup location
            
        Returns:
            Exit code (0 for success, 1 for failure)
        """
        print_color("\n" + "=" * 60, "cyan")
        print_color("duckyPad Profile Deployment", "cyan")
        print_color("=" * 60, "cyan")
        
        # Track if we auto-mounted (so we can auto-unmount later)
        auto_mounted = False
        
        # Detect SD card
        sd_card_path = self.profile_manager.detect_sd_card()
        
        # If SD card not detected, try to mount it
        if not sd_card_path:
            print_color("\n⚠ SD card not detected, attempting to mount...", "yellow")
            
            # Import device controller
            from device import DuckyPadDevice
            device = DuckyPadDevice(verbose=self.verbose)
            
            # Try to mount
            if not device.mount_sd_card():
                print_color("✗ Failed to mount SD card", "red")
                print_color("  Please ensure duckyPad is connected and try again", "yellow")
                return 1
            
            auto_mounted = True
            
            # Wait for SD card to appear
            print_color("  Waiting for SD card to appear...", "cyan")
            max_wait = 10  # seconds
            for i in range(max_wait):
                time.sleep(1)
                sd_card_path = self.profile_manager.detect_sd_card()
                if sd_card_path:
                    break
                if self.verbose:
                    print_color(f"  Waiting... ({i+1}/{max_wait})", "gray")
            
            if not sd_card_path:
                print_color("✗ SD card did not appear after mounting", "red")
                print_color("  Please check duckyPad connection and try again", "yellow")
                return 1
            
            print_color("✓ SD card mounted successfully", "green")
        
        print_color(f"\n✓ SD card detected: {sd_card_path}", "green")
        
        # Validate source profiles
        valid_profiles = []
        for profile_path in source_profiles:
            if not profile_path.exists():
                print_color(f"✗ Profile not found: {profile_path}", "red")
                continue
            
            if not profile_path.is_dir():
                print_color(f"✗ Not a directory: {profile_path}", "red")
                continue
            
            # Check for required files (config.txt and at least one key file)
            config_file = profile_path / "config.txt"
            key_files = list(profile_path.glob("key*.txt"))
            
            if not config_file.exists():
                print_color(f"⚠ {profile_path.name}: Missing config.txt", "yellow")
            
            if not key_files:
                print_color(f"⚠ {profile_path.name}: No key files found", "yellow")
            
            valid_profiles.append(profile_path)
        
        if not valid_profiles:
            print_color("\n✗ No valid profiles to deploy", "red")
            return 1
        
        # Count existing profiles on SD card
        existing_profile_dirs = [
            d for d in sd_card_path.iterdir()
            if d.is_dir() and d.name.lower().startswith("profile")
        ]
        existing_count = len(existing_profile_dirs)
        total_after_deployment = existing_count + len(valid_profiles)
        
        # Validate profile count
        try:
            require_valid_profile_count(
                total_after_deployment,
                context=f"deployment ({existing_count} existing + {len(valid_profiles)} new)"
            )
        except ValidationError as e:
            print_color(f"\n✗ Validation error: {e}", "red")
            print_color(f"  Current profiles on SD card: {existing_count}", "yellow")
            print_color(f"  Attempting to deploy: {len(valid_profiles)}", "yellow")
            print_color(f"  Total would be: {total_after_deployment}", "yellow")
            print_color(f"  Maximum allowed: {MAX_PROFILES}", "yellow")
            return 1
        
        # Display deployment plan
        print_color(f"\nProfiles to deploy: {len(valid_profiles)}", "white")
        for profile in valid_profiles:
            print_color(f"  • {profile.name}", "white")
        print_color(f"\nCurrent profiles on SD card: {existing_count}", "white")
        print_color(f"Total after deployment: {total_after_deployment}/{MAX_PROFILES}", "white")
        
        # Confirm deployment
        if not prompt_yes_no("\nProceed with deployment?", default=True, force=self.force):
            print_color("\n✗ Deployment cancelled", "yellow")
            return 1
        
        # Backup SD card
        backup_result = backup_sd_card(sd_card_path=sd_card_path, backup_path=backup_path, verbose=self.verbose)
        if not backup_result:
            print_color("\n✗ Backup failed", "red")
            if not prompt_yes_no("Continue without backup?", default=False, force=self.force):
                return 1
        
        # Deploy profiles
        print_color("\n→ Deploying profiles...", "cyan")
        next_number = self.find_next_profile_number(sd_card_path)
        
        stats = DeploymentStats()
        for profile_path in valid_profiles:
            if self.deploy_profile(profile_path, sd_card_path, next_number):
                stats.deployed += 1
                next_number += 1
            else:
                stats.failed += 1
        
        # Update profile_info.txt
        if not self.update_profile_info(sd_card_path):
            print_color("\n⚠ Failed to update profile_info.txt", "yellow")
        
        # Print summary
        print_color("\n" + "=" * 60, "cyan")
        print_color("Deployment Summary", "cyan")
        print_color("=" * 60, "cyan")
        print_color(f"Profiles deployed:  {stats.deployed}", "green")
        
        if stats.failed > 0:
            print_color(f"Failed:             {stats.failed}", "red")
        
        # Handle unmounting
        should_unmount = False
        
        if auto_mounted:
            # We auto-mounted, so always auto-unmount
            should_unmount = True
        elif self.auto_unmount:
            # SD card was already mounted, ask user if they want to unmount
            if prompt_yes_no("\nUnmount SD card?", default=True, force=self.force):
                should_unmount = True
        
        if should_unmount:
            print_color("\n→ Unmounting SD card...", "cyan")
            from device import DuckyPadDevice
            device = DuckyPadDevice(verbose=self.verbose)
            if device.unmount_sd_card():
                print_color("✓ SD card unmounted, duckyPad rebooting to normal mode", "green")
            else:
                print_color("⚠ Failed to unmount SD card", "yellow")
        
        if stats.deployed > 0:
            print_color("\n✓ Deployment complete!", "green")
            return 0
        else:
            print_color("\n✗ No profiles were deployed", "red")
            return 1


def deploy(source_profiles: List[Path], backup_path: Optional[Path] = None, verbose: bool = False, force: bool = False, auto_unmount: bool = False) -> int:
    """Deploy profiles to duckyPad SD card (programmatic interface)
    
    Args:
        source_profiles: List of profile directories to deploy
        backup_path: Custom backup location (default: ~/.duckypad/backups/backup_TIMESTAMP)
        verbose: Enable verbose output
        force: Skip confirmation prompts
        auto_unmount: Always unmount SD card after deployment (even if already mounted)
        
    Returns:
        Exit code (0 = success, 1 = failure)
    
    Note:
        The function automatically reads profile_info.txt from the SD card, scans for
        all profiles, and updates the file with all profiles on the card.
    """
    deployer = ProfileDeployer(verbose=verbose, force=force, auto_unmount=auto_unmount)
    return deployer.run(source_profiles=source_profiles, backup_path=backup_path)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Deploy profiles to duckyPad SD card with automatic backup"
    )
    parser.add_argument(
        "profiles",
        type=Path,
        nargs="+",
        help="Profile directories to deploy"
    )
    parser.add_argument(
        "-b", "--backup-path",
        type=Path,
        help="Custom backup location (default: ~/.duckypad/backups/backup_TIMESTAMP)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Skip confirmation prompts"
    )
    
    args = parser.parse_args()
    
    deployer = ProfileDeployer(verbose=args.verbose, force=args.force)
    exit_code = deployer.run(source_profiles=args.profiles, backup_path=args.backup_path)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()




