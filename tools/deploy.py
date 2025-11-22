#!/usr/bin/env python3
"""
Profile Deployment Manager
Backs up SD card, deploys profiles to duckyPad, updates profile_info.txt
"""

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add shared directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from shared.profile_info_manager import ProfileInfoManager


class DeploymentStats:
    """Track deployment statistics"""
    def __init__(self):
        self.backed_up = 0
        self.deployed = 0
        self.skipped = 0
        self.failed = 0


class ProfileDeployer:
    """Deploy profiles to duckyPad SD card with backup"""
    
    def __init__(self, verbose: bool = False, force: bool = False):
        """Initialize deployer
        
        Args:
            verbose: Enable verbose output
            force: Skip confirmations
        """
        self.verbose = verbose
        self.force = force
        self.profile_manager = ProfileInfoManager()
    
    def _print_color(self, message: str, color: str = "white"):
        """Print colored message
        
        Args:
            message: Message to print
            color: Color name (green, red, yellow, cyan, white, gray)
        """
        colors = {
            "green": "\033[92m",
            "red": "\033[91m",
            "yellow": "\033[93m",
            "cyan": "\033[96m",
            "white": "\033[97m",
            "gray": "\033[90m",
            "reset": "\033[0m"
        }
        print(f"{colors.get(color, colors['white'])}{message}{colors['reset']}")
    
    def _print_verbose(self, message: str):
        """Print verbose message if verbose mode enabled
        
        Args:
            message: Message to print
        """
        if self.verbose:
            self._print_color(f"  {message}", "cyan")
    
    def _prompt_yes_no(self, question: str, default: bool = True) -> bool:
        """Prompt user for yes/no confirmation
        
        Args:
            question: Question to ask
            default: Default answer if user just presses Enter
            
        Returns:
            True for yes, False for no
        """
        if self.force:
            return True
        
        default_str = "Y/n" if default else "y/N"
        response = input(f"{question} [{default_str}]: ").strip().lower()
        
        if not response:
            return default
        
        return response in ("y", "yes")
    
    def backup_sd_card(self, sd_card_path: Path, backup_path: Optional[Path] = None) -> Optional[Path]:
        """Backup SD card contents
        
        Args:
            sd_card_path: Path to SD card
            backup_path: Optional custom backup location
            
        Returns:
            Path to backup directory if successful, None otherwise
        """
        self._print_color("\n→ Creating SD card backup...", "cyan")
        
        # Generate backup path if not provided
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = Path.home() / ".duckypad" / "backups" / f"backup_{timestamp}"
        
        backup_path.mkdir(parents=True, exist_ok=True)
        
        self._print_verbose(f"Backup location: {backup_path}")
        
        stats = DeploymentStats()
        
        try:
            # Copy all files and directories except .dsb (can be regenerated)
            for item in sd_card_path.rglob("*"):
                if item.is_file():
                    # Skip .dsb bytecode files
                    if item.suffix == ".dsb":
                        self._print_verbose(f"Skipping: {item.name} (bytecode)")
                        stats.skipped += 1
                        continue
                    
                    # Calculate relative path
                    rel_path = item.relative_to(sd_card_path)
                    dest_path = backup_path / rel_path
                    
                    # Create parent directory
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(item, dest_path)
                    stats.backed_up += 1
                    self._print_verbose(f"Backed up: {rel_path}")
            
            self._print_color(f"✓ Backup complete: {stats.backed_up} files backed up, {stats.skipped} skipped", "green")
            self._print_color(f"  Location: {backup_path}", "gray")
            
            return backup_path
            
        except Exception as e:
            self._print_color(f"✗ Backup failed: {e}", "red")
            return None
    
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
            profile_number: Profile number to assign
            
        Returns:
            True if successful, False otherwise
        """
        # Generate profile directory name
        profile_name = source_path.name
        dest_name = f"profile{profile_number}_{profile_name}"
        dest_path = sd_card_path / dest_name
        
        self._print_verbose(f"Deploying: {profile_name} → {dest_name}")
        
        try:
            # Check if destination already exists
            if dest_path.exists():
                self._print_color(f"  Warning: {dest_name} already exists", "yellow")
                if not self._prompt_yes_no(f"  Overwrite {dest_name}?", default=False):
                    self._print_color(f"  Skipped: {profile_name}", "yellow")
                    return False
                shutil.rmtree(dest_path)
            
            # Copy profile directory
            shutil.copytree(source_path, dest_path)
            
            self._print_color(f"  ✓ Deployed: {dest_name}", "green")
            return True
            
        except Exception as e:
            self._print_color(f"  ✗ Failed to deploy {profile_name}: {e}", "red")
            return False
    
    def update_profile_info(self, sd_card_path: Path) -> bool:
        """Update profile_info.txt with all profiles on SD card
        
        Args:
            sd_card_path: Path to SD card
            
        Returns:
            True if successful, False otherwise
        """
        self._print_color("\n→ Updating profile_info.txt...", "cyan")
        
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
                                    self._print_verbose(f"Existing: {num} {name}")
                                except ValueError:
                                    continue
                except Exception as e:
                    self._print_verbose(f"Could not read existing profile_info.txt: {e}")
            
            # Find all profile directories on SD card
            all_dirs = sorted([
                d for d in sd_card_path.iterdir()
                if d.is_dir()
            ])
            
            if not all_dirs:
                self._print_color("  No directories found", "yellow")
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
                self._print_color("  No valid profiles found", "yellow")
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
                    self._print_verbose(f"Preserved: {num} {name}")
            
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
                    final_entries.append((next_number, name))
                    self._print_verbose(f"Added: {next_number} {name}")
                    next_number += 1
            
            # Write profile_info.txt
            with open(profile_info_path, "w", encoding="utf-8") as f:
                for profile_num, profile_name in final_entries:
                    f.write(f"{profile_num} {profile_name}\n")
            
            self._print_color(f"✓ Updated profile_info.txt with {len(final_entries)} profile(s)", "green")
            return True
            
        except Exception as e:
            self._print_color(f"✗ Failed to update profile_info.txt: {e}", "red")
            return False
    
    def run(self, source_profiles: List[Path], backup_path: Optional[Path] = None) -> int:
        """Run the deployment process
        
        Args:
            source_profiles: List of profile directories to deploy
            backup_path: Optional custom backup location
            
        Returns:
            Exit code (0 for success, 1 for failure)
        """
        self._print_color("\n" + "=" * 60, "cyan")
        self._print_color("duckyPad Profile Deployment", "cyan")
        self._print_color("=" * 60, "cyan")
        
        # Detect SD card
        sd_card_path = self.profile_manager.detect_sd_card()
        
        if not sd_card_path:
            self._print_color("\n✗ SD card not detected", "red")
            self._print_color("  Please insert duckyPad SD card and try again", "yellow")
            return 1
        
        self._print_color(f"\n✓ SD card detected: {sd_card_path}", "green")
        
        # Validate source profiles
        valid_profiles = []
        for profile_path in source_profiles:
            if not profile_path.exists():
                self._print_color(f"✗ Profile not found: {profile_path}", "red")
                continue
            
            if not profile_path.is_dir():
                self._print_color(f"✗ Not a directory: {profile_path}", "red")
                continue
            
            # Check for required files (config.txt and at least one key file)
            config_file = profile_path / "config.txt"
            key_files = list(profile_path.glob("key*.txt"))
            
            if not config_file.exists():
                self._print_color(f"⚠ {profile_path.name}: Missing config.txt", "yellow")
            
            if not key_files:
                self._print_color(f"⚠ {profile_path.name}: No key files found", "yellow")
            
            valid_profiles.append(profile_path)
        
        if not valid_profiles:
            self._print_color("\n✗ No valid profiles to deploy", "red")
            return 1
        
        # Display deployment plan
        self._print_color(f"\nProfiles to deploy: {len(valid_profiles)}", "white")
        for profile in valid_profiles:
            self._print_color(f"  • {profile.name}", "white")
        
        # Confirm deployment
        if not self._prompt_yes_no("\nProceed with deployment?", default=True):
            self._print_color("\n✗ Deployment cancelled", "yellow")
            return 1
        
        # Backup SD card
        backup_result = self.backup_sd_card(sd_card_path, backup_path)
        if not backup_result:
            self._print_color("\n✗ Backup failed", "red")
            if not self._prompt_yes_no("Continue without backup?", default=False):
                return 1
        
        # Deploy profiles
        self._print_color("\n→ Deploying profiles...", "cyan")
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
            self._print_color("\n⚠ Failed to update profile_info.txt", "yellow")
        
        # Print summary
        self._print_color("\n" + "=" * 60, "cyan")
        self._print_color("Deployment Summary", "cyan")
        self._print_color("=" * 60, "cyan")
        self._print_color(f"Profiles deployed:  {stats.deployed}", "green")
        
        if stats.failed > 0:
            self._print_color(f"Failed:             {stats.failed}", "red")
        
        if stats.deployed > 0:
            self._print_color("\n✓ Deployment complete!", "green")
            self._print_color("  You can now eject the SD card and insert it into your duckyPad", "gray")
            return 0
        else:
            self._print_color("\n✗ No profiles were deployed", "red")
            return 1


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
