#!/usr/bin/env python3
"""
duckyScript Compilation Validator
Validates duckyScript compilation by checking .txt to .dsb conversions
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add helpers directory to path for potential future imports
sys.path.insert(0, str(Path(__file__).parent.parent / "helpers"))


class ValidationResult:
    """Result of validating a single compilation pair"""
    
    def __init__(self):
        self.valid = True
        self.issues: List[str] = []
        self.txt_size = 0
        self.dsb_size = 0
        self.txt_modified = None
        self.dsb_modified = None


class ValidationStats:
    """Statistics for validation run"""
    
    def __init__(self):
        self.total = 0
        self.valid = 0
        self.invalid = 0
        self.missing = 0
        self.details: List[Dict] = []


class CompilationValidator:
    """Validate duckyScript compilation results"""
    
    def __init__(self, verbose: bool = False):
        """Initialize validator
        
        Args:
            verbose: Enable verbose output
        """
        self.verbose = verbose
        self.script_dir = Path(__file__).parent
    
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
    
    def test_compilation_pair(self, txt_file: Path, dsb_file: Path) -> ValidationResult:
        """Test a single .txt/.dsb compilation pair
        
        Args:
            txt_file: Path to .txt source file
            dsb_file: Path to .dsb bytecode file
            
        Returns:
            ValidationResult object
        """
        result = ValidationResult()
        
        # Check if .txt file exists
        if not txt_file.exists():
            result.issues.append("Missing source .txt file")
            result.valid = False
            return result
        
        # Check if .dsb file exists
        if not dsb_file.exists():
            result.issues.append("Missing compiled .dsb file")
            result.valid = False
            return result
        
        # Get file sizes
        try:
            result.txt_size = txt_file.stat().st_size
            result.dsb_size = dsb_file.stat().st_size
        except Exception as e:
            result.issues.append(f"Error reading file sizes: {e}")
            result.valid = False
            return result
        
        # Check .dsb file size
        if result.dsb_size == 0:
            result.issues.append("Empty .dsb file (0 bytes)")
            result.valid = False
        
        # Basic sanity check: minimum valid bytecode size
        # At minimum, we'd expect HALT instruction (3 bytes)
        if result.dsb_size < 3:
            result.issues.append(f"Invalid .dsb size ({result.dsb_size} bytes, minimum 3 expected)")
            result.valid = False
        
        # Check if sizes are reasonable
        if result.txt_size > 0 and result.dsb_size == 0:
            result.issues.append("Non-empty .txt compiled to empty .dsb")
            result.valid = False
        
        # Check .dsb is newer than .txt (or same age)
        try:
            txt_modified = txt_file.stat().st_mtime
            dsb_modified = dsb_file.stat().st_mtime
            result.txt_modified = txt_modified
            result.dsb_modified = dsb_modified
            
            if dsb_modified < txt_modified:
                result.issues.append(".dsb is older than .txt (needs recompilation)")
                result.valid = False
        except Exception as e:
            result.issues.append(f"Error comparing modification times: {e}")
            result.valid = False
        
        return result
    
    def test_profile_compilation(self, path: Path) -> ValidationStats:
        """Validate all compilations in a profile directory
        
        Args:
            path: Path to profile directory or profiles root
            
        Returns:
            ValidationStats object
        """
        self._print_color(f"\nValidating compilations in: {path}", "cyan")
        
        # Find all duckyScript .txt files
        txt_files = sorted([
            f for f in path.rglob("*.txt")
            if f.is_file() and f.name.startswith("key") and 
            (f.name.endswith(".txt") and not f.name.endswith("-release.txt") or 
             f.name.endswith("-release.txt"))
        ])
        
        if not txt_files:
            self._print_color("No duckyScript .txt files found", "yellow")
            return ValidationStats()
        
        stats = ValidationStats()
        
        for txt_file in txt_files:
            stats.total += 1
            
            # Construct .dsb file path
            dsb_file = txt_file.with_suffix(".dsb")
            
            # Test the pair
            result = self.test_compilation_pair(txt_file, dsb_file)
            
            # Get relative path for display
            try:
                relative_path = txt_file.relative_to(path)
            except ValueError:
                relative_path = txt_file.name
            
            # Display result
            if result.valid:
                stats.valid += 1
                self._print_color(f"  ✓ {relative_path}", "green")
                if result.dsb_size:
                    self._print_color(f"    ({result.txt_size} bytes → {result.dsb_size} bytes)", "gray")
            else:
                if "Missing compiled .dsb file" in result.issues:
                    stats.missing += 1
                    self._print_color(f"  ⚠ {relative_path}", "yellow")
                    for issue in result.issues:
                        self._print_color(f"    - {issue}", "yellow")
                else:
                    stats.invalid += 1
                    self._print_color(f"  ✗ {relative_path}", "red")
                    for issue in result.issues:
                        self._print_color(f"    - {issue}", "red")
            
            # Store details
            stats.details.append({
                "txt_file": txt_file,
                "dsb_file": dsb_file,
                "result": result
            })
        
        return stats
    
    def run(self, profile_path: Optional[Path] = None) -> int:
        """Run the validator
        
        Args:
            profile_path: Optional path to specific profile or profiles directory
            
        Returns:
            Exit code (0 for success, 1 for failure)
        """
        self._print_color("\n" + "=" * 60, "cyan")
        self._print_color("duckyScript Compilation Validator", "cyan")
        self._print_color("=" * 60, "cyan")
        
        # Determine validation scope
        if profile_path is None:
            # Default to profiles directory (now from tests/)
            profile_path = self.script_dir.parent / "profiles"
        else:
            # Resolve relative paths from current working directory
            if not profile_path.is_absolute():
                profile_path = Path.cwd() / profile_path
        
        if not profile_path.exists():
            self._print_color(f"\nError: Path not found: {profile_path}", "red")
            return 1
        
        # Validate compilations
        stats = self.test_profile_compilation(profile_path)
        
        # Print summary
        self._print_color("\n" + "=" * 60, "cyan")
        self._print_color("Validation Summary", "cyan")
        self._print_color("=" * 60, "cyan")
        self._print_color(f"Total .txt files: {stats.total}", "white")
        self._print_color(f"Valid pairs:      {stats.valid}", "green")
        self._print_color(f"Missing .dsb:     {stats.missing}", "yellow")
        
        invalid_color = "red" if stats.invalid > 0 else "green"
        self._print_color(f"Invalid/Issues:   {stats.invalid}", invalid_color)
        
        # Provide helpful tips
        if stats.missing > 0:
            self._print_color("\n💡 Tip: Run compile_duckyscript.py to compile missing files", "cyan")
        
        if stats.invalid > 0:
            self._print_color("\n⚠ Some compilations have issues. Review errors above.", "yellow")
            return 1
        
        if stats.missing == 0 and stats.invalid == 0:
            self._print_color("\n✓ All compilations are valid!", "green")
            return 0
        else:
            return 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Validate duckyScript compilation (.txt to .dsb conversions)"
    )
    parser.add_argument(
        "-p", "--profile-path",
        type=Path,
        help="Path to specific profile directory or profiles directory (default: profiles/)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    validator = CompilationValidator(verbose=args.verbose)
    exit_code = validator.run(profile_path=args.profile_path)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
