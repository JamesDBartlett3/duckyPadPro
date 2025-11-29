#!/usr/bin/env python3
"""
Backup and Restore duckyPad Pro SD card

Create backups of duckyPad Pro SD card contents and restore from backups.
Backups are stored in ~/.duckypad/backups/ by default.

Author: JamesDBartlett3
Date: 2025-11-22
"""

import argparse
import shutil
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from shared.profiles import ProfileInfoManager
from shared.console import print_color, print_verbose, prompt_yes_no


class BackupStats:
    """Track backup/restore statistics"""
    def __init__(self):
        self.backed_up = 0
        self.restored = 0
        self.failed = 0


class SDCardBackupRestore:
    """Backup and restore duckyPad Pro SD card."""
    
    def __init__(self, verbose: bool = False, force: bool = False):
        """
        Initialize backup/restore manager.
        
        Args:
            verbose: Enable verbose output
            force: Skip confirmation prompts
        """
        self.verbose = verbose
        self.force = force
        self.profile_manager = ProfileInfoManager()
    
    def backup(self, sd_card_path: Optional[Path] = None, backup_path: Optional[Path] = None) -> Optional[Path]:
        """
        Backup SD card contents.
        
        Args:
            sd_card_path: Path to SD card (auto-detected if not provided)
            backup_path: Optional custom backup location
            
        Returns:
            Path to backup directory if successful, None otherwise
        """
        print_color("\n→ Creating SD card backup...", "cyan")
        
        # Auto-detect SD card if not provided
        if sd_card_path is None:
            sd_card_path = self.profile_manager.detect_sd_card()
            if sd_card_path is None:
                print_color("\n✗ SD card not found", "red")
                print_color("  Please insert duckyPad SD card and try again", "yellow")
                return None
        
        print_color(f"✓ SD card detected: {sd_card_path}", "green")
        
        # Generate backup path if not provided
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = Path.home() / ".duckypad" / "backups" / f"backup_{timestamp}"
        
        backup_path.mkdir(parents=True, exist_ok=True)
        
        print_verbose(f"Backup location: {backup_path}", self.verbose)
        
        stats = BackupStats()
        
        # Print disclaimer about what gets backed up
        print_color("  Note: Backing up config and source files only (bytecode .dsb files excluded)", "gray")
        
        try:
            # Copy all files and directories except .dsb (can be regenerated)
            for item in sd_card_path.rglob("*"):
                if item.is_file():
                    # Skip .dsb bytecode files (they can be regenerated from source)
                    if item.suffix == ".dsb":
                        continue
                    
                    # Calculate relative path
                    rel_path = item.relative_to(sd_card_path)
                    dest_path = backup_path / rel_path
                    
                    # Create parent directory
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(item, dest_path)
                    stats.backed_up += 1
                    print_verbose(f"Backed up: {rel_path}", self.verbose)
            
            print_color(f"✓ Backup complete: {stats.backed_up} files backed up", "green")
            print_color(f"  Location: {backup_path}", "gray")
            
            return backup_path
            
        except Exception as e:
            print_color(f"✗ Backup failed: {e}", "red")
            return None
    
    def list_backups(self, backup_root: Path = None) -> list:
        """
        List available backups.
        
        Args:
            backup_root: Root backup directory (default: ~/.duckypad/backups)
            
        Returns:
            List of backup directory paths, sorted by date (newest first)
        """
        if backup_root is None:
            backup_root = Path.home() / ".duckypad" / "backups"
        
        if not backup_root.exists():
            return []
        
        backups = [d for d in backup_root.iterdir() if d.is_dir() and d.name.startswith("backup_")]
        backups.sort(reverse=True)  # Newest first
        
        return backups
    
    def restore(self, backup_path: Path, sd_card_path: Path = None, force: bool = False) -> bool:
        """
        Restore SD card from backup.
        
        Args:
            backup_path: Path to backup directory
            sd_card_path: Path to SD card (auto-detected if not provided)
            force: Skip confirmation prompts
            
        Returns:
            True if successful, False otherwise
        """
        print_color("\n" + "=" * 60, "cyan")
        print_color("duckyPad SD Card Restore", "cyan")
        print_color("=" * 60, "cyan")
        
        # Validate backup path
        if not backup_path.exists():
            print_color(f"\n✗ Backup not found: {backup_path}", "red")
            return False
        
        # Auto-detect SD card if not provided
        if sd_card_path is None:
            sd_card_path = self.profile_manager.detect_sd_card()
            if sd_card_path is None:
                print_color("\n✗ SD card not found", "red")
                print_color("  Please insert duckyPad SD card and try again", "yellow")
                return False
        
        print_color(f"\n✓ SD card detected: {sd_card_path}", "green")
        print_color(f"\nBackup: {backup_path.name}", "cyan")
        
        # Count files in backup
        backup_files = list(backup_path.rglob("*"))
        file_count = len([f for f in backup_files if f.is_file()])
        
        print_color(f"Files to restore: {file_count}", "cyan")
        
        # Confirm restore
        if not force:
            print_color("\n⚠ WARNING: This will DELETE ALL current files on the SD card!", "yellow")
            if not prompt_yes_no("Proceed with restore?", default=False, force=self.force):
                print_color("\nRestore cancelled", "yellow")
                return False
        
        # Clear SD card (except System Volume Information)
        print_color("\n→ Clearing SD card...", "cyan")
        cleared = 0
        for item in sd_card_path.iterdir():
            # Skip system folders
            if item.name == "System Volume Information":
                continue
            
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
                cleared += 1
                print_verbose(f"  Removed: {item.name}", self.verbose)
            except Exception as e:
                print_color(f"  Warning: Could not remove {item.name}: {e}", "yellow")
        
        print_color(f"✓ Cleared {cleared} items", "green")
        
        # Restore files from backup
        print_color("\n→ Restoring files from backup...", "cyan")
        stats = BackupStats()
        
        for src_path in backup_files:
            if not src_path.is_file():
                continue
            
            # Calculate relative path
            rel_path = src_path.relative_to(backup_path)
            dest_path = sd_card_path / rel_path
            
            # Create parent directory if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            try:
                shutil.copy2(src_path, dest_path)
                stats.restored += 1
                print_verbose(f"  Restored: {rel_path}", self.verbose)
            except Exception as e:
                print_color(f"  Warning: Could not restore {rel_path}: {e}", "yellow")
                stats.failed += 1
        
        print_color(f"✓ Restored {stats.restored} files", "green")
        
        # Summary
        print_color("\n" + "=" * 60, "cyan")
        print_color("Restore Summary", "cyan")
        print_color("=" * 60, "cyan")
        print_color(f"Files restored: {stats.restored}", "green")
        if stats.failed > 0:
            print_color(f"Files failed:   {stats.failed}", "red")
        
        print_color("\n✓ Restore complete!", "green")
        
        return True


def backup_sd_card(sd_card_path: Optional[Path] = None, backup_path: Optional[Path] = None, verbose: bool = False) -> Optional[Path]:
    """
    Backup SD card contents (programmatic interface).
    
    Args:
        sd_card_path: Path to SD card (auto-detected if not provided)
        backup_path: Custom backup location (default: ~/.duckypad/backups/backup_TIMESTAMP)
        verbose: Enable verbose output
        
    Returns:
        Path to backup directory if successful, None otherwise
    """
    manager = SDCardBackupRestore(verbose=verbose)
    return manager.backup(sd_card_path=sd_card_path, backup_path=backup_path)


def restore_sd_card(backup_path: Path, sd_card_path: Optional[Path] = None, force: bool = False, verbose: bool = False) -> bool:
    """
    Restore SD card from backup (programmatic interface).
    
    Args:
        backup_path: Path to backup directory
        sd_card_path: Path to SD card (auto-detected if not provided)
        force: Skip confirmation prompts
        verbose: Enable verbose output
        
    Returns:
        True if successful, False otherwise
    """
    manager = SDCardBackupRestore(verbose=verbose)
    return manager.restore(backup_path=backup_path, sd_card_path=sd_card_path, force=force)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Backup and restore duckyPad Pro SD card',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create backup
  python backup.py --backup
  
  # List available backups
  python backup.py --list
  
  # Restore from latest backup
  python backup.py --restore --latest
  
  # Restore from specific backup
  python backup.py --restore backup_20251122_153000
  
  # Restore with custom backup directory
  python backup.py --restore backup_20251122_153000 --backup-dir /path/to/backups
  
  # Skip confirmation
  python backup.py --restore --latest -f
        """
    )
    
    parser.add_argument(
        'backup',
        nargs='?',
        help='Backup directory name or path (for restore mode)'
    )
    
    parser.add_argument(
        '--backup', '-b',
        dest='do_backup',
        action='store_true',
        help='Create a backup of the SD card'
    )
    
    parser.add_argument(
        '--restore', '-r',
        action='store_true',
        help='Restore SD card from backup'
    )
    
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List available backups and exit'
    )
    
    parser.add_argument(
        '--latest',
        action='store_true',
        help='Use the most recent backup (for restore mode)'
    )
    
    parser.add_argument(
        '--backup-dir',
        type=Path,
        help='Backup root directory (default: ~/.duckypad/backups)'
    )
    
    parser.add_argument(
        '--sd-card',
        type=Path,
        help='SD card path (auto-detected if not provided)'
    )
    
    parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='Skip confirmation prompts'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    manager = SDCardBackupRestore(verbose=args.verbose)
    
    # Determine backup root
    backup_root = args.backup_dir if args.backup_dir else Path.home() / ".duckypad" / "backups"
    
    # List backups mode
    if args.list:
        backups = manager.list_backups(backup_root)
        
        if not backups:
            print(f"No backups found in {backup_root}")
            sys.exit(0)
        
        print(f"\nAvailable backups in {backup_root}:\n")
        for i, backup in enumerate(backups, 1):
            # Parse timestamp from backup name
            try:
                timestamp_str = backup.name.replace("backup_", "")
                timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                formatted_time = "Unknown"
            
            marker = " (latest)" if i == 1 else ""
            print(f"  {i}. {backup.name}{marker}")
            print(f"     Created: {formatted_time}")
        
        print()
        sys.exit(0)
    
    # Backup mode
    if args.do_backup:
        try:
            backup_path = manager.backup(
                sd_card_path=args.sd_card,
                backup_path=backup_root / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}" if backup_root else None
            )
            
            sys.exit(0 if backup_path else 1)
            
        except Exception as e:
            print(f"\n✗ Error during backup: {e}")
            if args.verbose:
                traceback.print_exc()
            sys.exit(1)
    
    # Restore mode
    if args.restore:
        # Determine which backup to restore
        backup_path = None
        
        if args.latest:
            backups = manager.list_backups(backup_root)
            if not backups:
                print(f"No backups found in {backup_root}")
                sys.exit(1)
            backup_path = backups[0]
            print(f"Using latest backup: {backup_path.name}")
        
        elif args.backup:
            # Check if it's a full path or just a name
            backup_arg = Path(args.backup)
            if backup_arg.is_absolute() and backup_arg.exists():
                backup_path = backup_arg
            else:
                # Assume it's a backup name
                backup_path = backup_root / args.backup
        
        else:
            parser.print_help()
            sys.exit(1)
        
        # Restore
        try:
            success = manager.restore(
                backup_path=backup_path,
                sd_card_path=args.sd_card,
                force=args.force
            )
            
            sys.exit(0 if success else 1)
            
        except Exception as e:
            print(f"\n✗ Error during restore: {e}")
            if args.verbose:
                traceback.print_exc()
            sys.exit(1)
    
    # No mode specified
    parser.print_help()
    sys.exit(1)


if __name__ == '__main__':
    main()


