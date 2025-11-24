#!/usr/bin/env python3
"""
duckyScript Compiler
Compiles .txt duckyScript source files to .dsb bytecode using make_bytecode.py
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# Add shared directory to path for ProfileInfoManager
sys.path.insert(0, str(Path(__file__).parent))
try:
    from shared.profiles import ProfileInfoManager
    from shared.console import print_color, print_verbose
    from shared.validators import (
        ValidationError,
        validate_key_label,
        require_valid_key_label,
    )
    PROFILE_MANAGER_AVAILABLE = True
    VALIDATORS_AVAILABLE = True
except ImportError:
    PROFILE_MANAGER_AVAILABLE = False
    VALIDATORS_AVAILABLE = False


class CompilerStats:
    """Track compilation statistics"""
    def __init__(self):
        self.total = 0
        self.success = 0
        self.failed = 0
        self.validation_failed = 0
    
    def add_success(self):
        self.total += 1
        self.success += 1
    
    def add_failure(self):
        self.total += 1
        self.failed += 1
    
    def add_validation_failure(self):
        """Mark that validation failed (counts as failure but no files were compiled)"""
        self.validation_failed += 1
        self.failed += 1


class DuckyScriptCompiler:
    """Compile duckyScript files to bytecode"""
    
    # Configuration
    GITHUB_REPO = "duckyPad/duckyPad-Configurator"
    REQUIRED_FILES = [
        "make_bytecode.py",
        "ds3_preprocessor.py", 
        "attrdict.py",
        "duckypad_config.py"
    ]
    
    def __init__(self, verbose: bool = False, resolve_profiles: bool = True):
        """Initialize compiler
        
        Args:
            verbose: Enable verbose output
            resolve_profiles: Enable profile name to index resolution
        """
        self.verbose = verbose
        self.resolve_profiles = resolve_profiles
        self.script_dir = Path(__file__).parent
        self.vendor_dir = self.script_dir / "vendor"
        self.compiler_path = self.vendor_dir / "make_bytecode.py"
        self.profile_manager = None
        
        # Initialize ProfileInfoManager if available and enabled
        if self.resolve_profiles and PROFILE_MANAGER_AVAILABLE:
            try:
                self.profile_manager = ProfileInfoManager()
                if self.profile_manager.load_profile_mapping():
                    if self.verbose:
                        profile_count = len(self.profile_manager.profile_mapping)
                        print_verbose(f"✓ Loaded {profile_count} profile mappings from SD card", self.verbose, indent=False)
            except Exception as e:
                if self.verbose:
                    print_color(f"Warning: Could not initialize profile manager: {e}", "yellow")
    
    def test_python_available(self) -> bool:
        """Check if Python is available
        
        Returns:
            True if Python is available, False otherwise
        """
        try:
            result = subprocess.run(
                [sys.executable, "--version"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                print_verbose(f"Python found: {result.stdout.strip()}", self.verbose)
                return True
            return False
        except Exception as e:
            print_color(f"Error checking Python: {e}", "red")
            return False
    
    def get_latest_compiler(self) -> bool:
        """Download latest compiler from GitHub
        
        Returns:
            True if successful, False otherwise
        """
        print_color("\n→ Fetching latest compiler from GitHub...", "cyan")
        
        try:
            # Create vendor directory
            self.vendor_dir.mkdir(parents=True, exist_ok=True)
            
            # Get latest release info
            api_url = f"https://api.github.com/repos/{self.GITHUB_REPO}/releases/latest"
            req = Request(api_url)
            req.add_header("User-Agent", "duckyPad-Compiler")
            
            with urlopen(req, timeout=10) as response:
                release_data = json.loads(response.read().decode())
            
            # Find zipball URL
            zipball_url = release_data.get("zipball_url")
            if not zipball_url:
                print_color("Could not find release download URL", "red")
                return False
            
            print_verbose(f"Downloading from: {zipball_url}", self.verbose)
            
            # Download zipball
            zip_path = self.vendor_dir / "release.zip"
            req = Request(zipball_url)
            req.add_header("User-Agent", "duckyPad-Compiler")
            
            with urlopen(req, timeout=30) as response:
                with open(zip_path, "wb") as f:
                    f.write(response.read())
            
            print_verbose("Download complete, extracting files...", self.verbose)
            
            # Extract required files
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                # Find root folder in zip
                namelist = zip_ref.namelist()
                root_folder = namelist[0].split("/")[0] if namelist else ""
                
                for filename in self.REQUIRED_FILES:
                    source_path = f"{root_folder}/{filename}"
                    if source_path in namelist:
                        # Extract to vendor directory
                        zip_ref.extract(source_path, self.vendor_dir)
                        # Move from nested folder to vendor root
                        extracted_path = self.vendor_dir / source_path
                        target_path = self.vendor_dir / filename
                        shutil.move(str(extracted_path), str(target_path))
                        print_verbose(f"  ✓ {filename}", self.verbose)
            
            # Clean up
            zip_path.unlink()
            
            # Remove extracted folder if it exists
            extracted_folder = self.vendor_dir / root_folder
            if extracted_folder.exists():
                shutil.rmtree(extracted_folder)
            
            print_color("✓ Compiler fetched successfully", "green")
            return True
            
        except (URLError, HTTPError) as e:
            print_color(f"Network error: {e}", "red")
            return False
        except Exception as e:
            print_color(f"Error fetching compiler: {e}", "red")
            return False
    
    def _parse_config(self, config_path: Path) -> Tuple[str, Dict[int, Tuple[str, str]]]:
        """Parse config.txt to extract orientation and key labels
        
        Args:
            config_path: Path to config.txt file
            
        Returns:
            Tuple of (orientation, labels_dict) where:
            - orientation: 'portrait' or 'landscape'
            - labels_dict: {key_num: (z_line, x_line)}
        """
        orientation = 'portrait'  # Default
        labels = {}  # {key_num: (z_line, x_line)}
        
        if not config_path.exists():
            return orientation, labels
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Check for orientation
                    if line == 'IS_LANDSCAPE 1':
                        orientation = 'landscape'
                    
                    # Parse key labels (z1, x1, z2, x2, etc.)
                    parts = line.split(None, 1)  # Split on first whitespace
                    if len(parts) == 2:
                        directive, value = parts
                        
                        # Check for z labels (line 1)
                        if directive.startswith('z') and directive[1:].isdigit():
                            key_num = int(directive[1:])
                            if key_num not in labels:
                                labels[key_num] = ('', '')
                            labels[key_num] = (value, labels[key_num][1])
                        
                        # Check for x labels (line 2)
                        elif directive.startswith('x') and directive[1:].isdigit():
                            key_num = int(directive[1:])
                            if key_num not in labels:
                                labels[key_num] = ('', '')
                            labels[key_num] = (labels[key_num][0], value)
        
        except Exception as e:
            if self.verbose:
                print_color(f"Warning: Error parsing config.txt: {e}", "yellow")
        
        return orientation, labels
    
    def _validate_profile_config(self, profile_path: Path) -> bool:
        """Validate profile configuration before compilation
        
        Args:
            profile_path: Path to profile directory
            
        Returns:
            True if valid, False if validation errors found
        """
        if not VALIDATORS_AVAILABLE:
            return True  # Skip validation if validators not available
        
        config_path = profile_path / "config.txt"
        if not config_path.exists():
            if self.verbose:
                print_color("  No config.txt found, skipping validation", "yellow")
            return True
        
        # Parse config to get orientation and labels
        orientation, labels = self._parse_config(config_path)
        
        if not labels:
            return True  # No labels to validate
        
        # Validate each label
        has_errors = False
        for key_num, (z_line, x_line) in labels.items():
            if not z_line and not x_line:
                continue  # Skip empty labels
            
            valid, error = validate_key_label(z_line, x_line, orientation, key_num)
            if not valid:
                print_color(f"  ✗ Validation error: {error}", "red")
                has_errors = True
        
        return not has_errors
    
    def compile_file(self, txt_path: Path) -> bool:
        """Compile a single duckyScript file
        
        Args:
            txt_path: Path to .txt source file
            
        Returns:
            True if successful, False otherwise
        """
        if not txt_path.exists():
            print_color(f"File not found: {txt_path}", "red")
            return False
        
        if not txt_path.suffix == ".txt":
            print_verbose(f"Skipping non-.txt file: {txt_path.name}", self.verbose)
            return False
        
        # Check if this is a key file (not config.txt)
        if not txt_path.stem.startswith("key"):
            print_verbose(f"Skipping non-key file: {txt_path.name}", self.verbose)
            return False
        
        dsb_path = txt_path.with_suffix(".dsb")
        
        try:
            print_verbose(f"Compiling: {txt_path.name}", self.verbose)
            
            # Read and potentially transform the content
            content = txt_path.read_text(encoding="utf-8")
            
            # Apply profile name resolution if enabled
            if self.profile_manager and self.profile_manager.profile_mapping:
                transformed_content, warnings = self.profile_manager.transform_goto_commands(content)
                if transformed_content != content:
                    print_verbose(f"  → Resolved GOTO_PROFILE name(s) to index", self.verbose)
                    content = transformed_content
                # Display any warnings
                for warning in warnings:
                    print_color(f"  Warning: {warning}", "yellow")
            
            # Create a temporary file with the (potentially transformed) content
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as tmp:
                tmp.write(content)
                tmp_path = Path(tmp.name)
            
            try:
                result = subprocess.run(
                    [
                        sys.executable,
                        str(self.compiler_path),
                        str(tmp_path),
                        str(dsb_path)
                    ],
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                if result.returncode == 0:
                    print_color(f"  ✓ {txt_path.name} → {dsb_path.name}", "green")
                    return True
                else:
                    print_color(f"  ✗ {txt_path.name}", "red")
                    if result.stderr:
                        print_color(f"    Error: {result.stderr.strip()}", "red")
                    return False
            finally:
                # Clean up temporary file
                tmp_path.unlink(missing_ok=True)
                
        except Exception as e:
            print_color(f"  ✗ {txt_path.name}: {e}", "red")
            return False
    
    def compile_profile(self, profile_path: Path) -> CompilerStats:
        """Compile all duckyScript files in a profile directory
        
        Args:
            profile_path: Path to profile directory
            
        Returns:
            CompilerStats object with compilation results
        """
        stats = CompilerStats()
        
        if not profile_path.exists():
            print_color(f"Profile path not found: {profile_path}", "red")
            return stats
        
        if not profile_path.is_dir():
            print_color(f"Not a directory: {profile_path}", "red")
            return stats
        
        print_color(f"\n→ Compiling profile: {profile_path.name}", "cyan")
        
        # Validate profile configuration before compilation
        if not self._validate_profile_config(profile_path):
            print_color("  ✗ Profile validation failed, skipping compilation", "red")
            print_color("    Please fix the labels in config.txt to match orientation limits", "yellow")
            stats.add_validation_failure()
            return stats
        
        # Find all .txt files
        txt_files = sorted(profile_path.glob("*.txt"))
        key_files = [f for f in txt_files if f.stem.startswith("key")]
        
        if not key_files:
            print_color("  No key files found", "yellow")
            return stats
        
        print_verbose(f"  Found {len(key_files)} key file(s)", self.verbose)
        
        # Compile each file
        for txt_file in key_files:
            if self.compile_file(txt_file):
                stats.add_success()
            else:
                stats.add_failure()
        
        return stats
    
    def compile_profiles(self, profiles_path: Path) -> CompilerStats:
        """Compile all profiles in a directory
        
        Args:
            profiles_path: Path to profiles directory
            
        Returns:
            CompilerStats object with compilation results
        """
        total_stats = CompilerStats()
        
        if not profiles_path.exists():
            print_color(f"Profiles directory not found: {profiles_path}", "red")
            return total_stats
        
        # Find all profile directories (starting with "profile")
        profile_dirs = sorted([
            d for d in profiles_path.iterdir()
            if d.is_dir() and d.name.lower().startswith("profile")
        ])
        
        if not profile_dirs:
            print_color("No profile directories found", "yellow")
            return total_stats
        
        print_color(f"\nFound {len(profile_dirs)} profile(s)", "white")
        
        # Compile each profile
        for profile_dir in profile_dirs:
            stats = self.compile_profile(profile_dir)
            total_stats.total += stats.total
            total_stats.success += stats.success
            total_stats.failed += stats.failed
        
        return total_stats
    
    def run(self, profile_path: Optional[Path] = None) -> int:
        """Run the compiler
        
        Args:
            profile_path: Optional path to specific profile or profiles directory
            
        Returns:
            Exit code (0 for success, 1 for failure)
        """
        print_color("\n" + "=" * 60, "cyan")
        print_color("duckyScript Compiler", "cyan")
        print_color("=" * 60, "cyan")
        
        # Check Python availability
        if not self.test_python_available():
            print_color("\n✗ Python is not available", "red")
            return 1
        
        # Check if compiler exists, fetch if not
        if not self.compiler_path.exists():
            if not self.get_latest_compiler():
                print_color("\n✗ Failed to fetch compiler", "red")
                return 1
        else:
            print_verbose("\n→ Using existing compiler", self.verbose)
        
        # Compile profiles
        if profile_path is None:
            # Default to profiles directory
            profile_path = self.script_dir.parent.parent / "profiles"
        else:
            # Resolve relative paths from current working directory
            if not profile_path.is_absolute():
                profile_path = Path.cwd() / profile_path
        
        if not profile_path.exists():
            print_color(f"\nPath not found: {profile_path}", "red")
            return 1
        
        if not profile_path.is_dir():
            print_color(f"\nNot a directory: {profile_path}", "red")
            return 1
        
        # Check if this is a single profile or profiles directory
        # A profile directory should contain .txt files
        has_txt_files = any(profile_path.glob("*.txt"))
        
        if has_txt_files:
            # Single profile directory
            stats = self.compile_profile(profile_path)
        else:
            # Directory containing multiple profiles
            stats = self.compile_profiles(profile_path)
        
        # Print summary
        print_color("\n" + "=" * 60, "cyan")
        print_color("Compilation Summary", "cyan")
        print_color("=" * 60, "cyan")
        print_color(f"Total files:           {stats.total}", "white")
        print_color(f"Successfully compiled: {stats.success}", "green")
        
        compilation_failed = stats.failed - stats.validation_failed
        if compilation_failed > 0:
            print_color(f"Compilation failed:    {compilation_failed}", "red")
        
        if stats.validation_failed > 0:
            print_color(f"Validation failed:     {stats.validation_failed}", "red")
        
        if stats.failed > 0:
            print_color("\n✗ Compilation failed", "red")
            return 1
        
        print_color("\n✓ Compilation complete!", "green")
        return 0


def compile(profile_path: Optional[Path] = None, verbose: bool = False, resolve_profiles: bool = True) -> int:
    """Compile duckyScript files to bytecode (programmatic interface)
    
    Args:
        profile_path: Path to specific profile or profiles directory (default: profiles/)
        verbose: Enable verbose output
        resolve_profiles: Enable automatic GOTO_PROFILE name resolution
        
    Returns:
        Exit code (0 = success, 1 = failure)
    
    Note:
        If resolve_profiles is True, the compiler will automatically read profile_info.txt
        from the SD card to resolve GOTO_PROFILE name references.
    """
    compiler = DuckyScriptCompiler(verbose=verbose, resolve_profiles=resolve_profiles)
    return compiler.run(profile_path=profile_path)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Compile duckyScript files to bytecode"
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
    parser.add_argument(
        "--no-resolve-profiles",
        dest="resolve_profiles",
        action="store_false",
        default=True,
        help="Disable automatic profile name to index resolution in GOTO_PROFILE commands"
    )
    
    args = parser.parse_args()
    
    compiler = DuckyScriptCompiler(verbose=args.verbose, resolve_profiles=args.resolve_profiles)
    exit_code = compiler.run(profile_path=args.profile_path)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
