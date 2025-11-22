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
    from shared.profile_info_manager import ProfileInfoManager
    PROFILE_MANAGER_AVAILABLE = True
except ImportError:
    PROFILE_MANAGER_AVAILABLE = False


class CompilerStats:
    """Track compilation statistics"""
    def __init__(self):
        self.total = 0
        self.success = 0
        self.failed = 0
    
    def add_success(self):
        self.total += 1
        self.success += 1
    
    def add_failure(self):
        self.total += 1
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
                        self._print_color(f"✓ Loaded {profile_count} profile mappings from SD card", "green")
            except Exception as e:
                if self.verbose:
                    self._print_color(f"Warning: Could not initialize profile manager: {e}", "yellow")
    
    def _print_color(self, message: str, color: str = "white"):
        """Print colored message
        
        Args:
            message: Message to print
            color: Color name (green, red, yellow, cyan, white)
        """
        colors = {
            "green": "\033[92m",
            "red": "\033[91m",
            "yellow": "\033[93m",
            "cyan": "\033[96m",
            "white": "\033[97m",
            "reset": "\033[0m"
        }
        print(f"{colors.get(color, colors['white'])}{message}{colors['reset']}")
    
    def _print_verbose(self, message: str):
        """Print verbose message if verbose mode enabled
        
        Args:
            message: Message to print
        """
        if self.verbose:
            self._print_color(message, "cyan")
    
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
                self._print_verbose(f"Python found: {result.stdout.strip()}")
                return True
            return False
        except Exception as e:
            self._print_color(f"Error checking Python: {e}", "red")
            return False
    
    def get_latest_compiler(self) -> bool:
        """Download latest compiler from GitHub
        
        Returns:
            True if successful, False otherwise
        """
        self._print_color("\n→ Fetching latest compiler from GitHub...", "cyan")
        
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
                self._print_color("Could not find release download URL", "red")
                return False
            
            self._print_verbose(f"Downloading from: {zipball_url}")
            
            # Download zipball
            zip_path = self.vendor_dir / "release.zip"
            req = Request(zipball_url)
            req.add_header("User-Agent", "duckyPad-Compiler")
            
            with urlopen(req, timeout=30) as response:
                with open(zip_path, "wb") as f:
                    f.write(response.read())
            
            self._print_verbose("Download complete, extracting files...")
            
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
                        self._print_verbose(f"  ✓ {filename}")
            
            # Clean up
            zip_path.unlink()
            
            # Remove extracted folder if it exists
            extracted_folder = self.vendor_dir / root_folder
            if extracted_folder.exists():
                shutil.rmtree(extracted_folder)
            
            self._print_color("✓ Compiler fetched successfully", "green")
            return True
            
        except (URLError, HTTPError) as e:
            self._print_color(f"Network error: {e}", "red")
            return False
        except Exception as e:
            self._print_color(f"Error fetching compiler: {e}", "red")
            return False
    
    def compile_file(self, txt_path: Path) -> bool:
        """Compile a single duckyScript file
        
        Args:
            txt_path: Path to .txt source file
            
        Returns:
            True if successful, False otherwise
        """
        if not txt_path.exists():
            self._print_color(f"File not found: {txt_path}", "red")
            return False
        
        if not txt_path.suffix == ".txt":
            self._print_verbose(f"Skipping non-.txt file: {txt_path.name}")
            return False
        
        # Check if this is a key file (not config.txt)
        if not txt_path.stem.startswith("key"):
            self._print_verbose(f"Skipping non-key file: {txt_path.name}")
            return False
        
        dsb_path = txt_path.with_suffix(".dsb")
        
        try:
            self._print_verbose(f"Compiling: {txt_path.name}")
            
            # Read and potentially transform the content
            content = txt_path.read_text(encoding="utf-8")
            
            # Apply profile name resolution if enabled
            if self.profile_manager and self.profile_manager.profile_mapping:
                transformed_content, warnings = self.profile_manager.transform_goto_commands(content)
                if transformed_content != content:
                    self._print_verbose(f"  → Resolved GOTO_PROFILE name(s) to index")
                    content = transformed_content
                # Display any warnings
                for warning in warnings:
                    self._print_color(f"  Warning: {warning}", "yellow")
            
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
                    self._print_color(f"  ✓ {txt_path.name} → {dsb_path.name}", "green")
                    return True
                else:
                    self._print_color(f"  ✗ {txt_path.name}", "red")
                    if result.stderr:
                        self._print_color(f"    Error: {result.stderr.strip()}", "red")
                    return False
            finally:
                # Clean up temporary file
                tmp_path.unlink(missing_ok=True)
                
        except Exception as e:
            self._print_color(f"  ✗ {txt_path.name}: {e}", "red")
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
            self._print_color(f"Profile path not found: {profile_path}", "red")
            return stats
        
        if not profile_path.is_dir():
            self._print_color(f"Not a directory: {profile_path}", "red")
            return stats
        
        self._print_color(f"\n→ Compiling profile: {profile_path.name}", "cyan")
        
        # Find all .txt files
        txt_files = sorted(profile_path.glob("*.txt"))
        key_files = [f for f in txt_files if f.stem.startswith("key")]
        
        if not key_files:
            self._print_color("  No key files found", "yellow")
            return stats
        
        self._print_verbose(f"  Found {len(key_files)} key file(s)")
        
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
            self._print_color(f"Profiles directory not found: {profiles_path}", "red")
            return total_stats
        
        # Find all profile directories (starting with "profile")
        profile_dirs = sorted([
            d for d in profiles_path.iterdir()
            if d.is_dir() and d.name.lower().startswith("profile")
        ])
        
        if not profile_dirs:
            self._print_color("No profile directories found", "yellow")
            return total_stats
        
        self._print_color(f"\nFound {len(profile_dirs)} profile(s)", "white")
        
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
        self._print_color("\n" + "=" * 60, "cyan")
        self._print_color("duckyScript Compiler", "cyan")
        self._print_color("=" * 60, "cyan")
        
        # Check Python availability
        if not self.test_python_available():
            self._print_color("\n✗ Python is not available", "red")
            return 1
        
        # Check if compiler exists, fetch if not
        if not self.compiler_path.exists():
            if not self.get_latest_compiler():
                self._print_color("\n✗ Failed to fetch compiler", "red")
                return 1
        else:
            self._print_verbose("\n→ Using existing compiler")
        
        # Compile profiles
        if profile_path is None:
            # Default to profiles directory
            profile_path = self.script_dir.parent.parent / "profiles"
        else:
            # Resolve relative paths from current working directory
            if not profile_path.is_absolute():
                profile_path = Path.cwd() / profile_path
        
        if not profile_path.exists():
            self._print_color(f"\nPath not found: {profile_path}", "red")
            return 1
        
        if not profile_path.is_dir():
            self._print_color(f"\nNot a directory: {profile_path}", "red")
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
        self._print_color("\n" + "=" * 60, "cyan")
        self._print_color("Compilation Summary", "cyan")
        self._print_color("=" * 60, "cyan")
        self._print_color(f"Total files:           {stats.total}", "white")
        self._print_color(f"Successfully compiled: {stats.success}", "green")
        
        failed_color = "red" if stats.failed > 0 else "green"
        self._print_color(f"Failed:                {stats.failed}", failed_color)
        
        if stats.failed > 0:
            self._print_color("\n✗ Compilation completed with errors", "red")
            return 1
        
        self._print_color("\n✓ Compilation complete!", "green")
        return 0


def compile(profile_path: Optional[Path] = None, verbose: bool = False, resolve_profiles: bool = True) -> int:
    """Compile duckyScript files to bytecode (programmatic interface)
    
    Args:
        profile_path: Path to specific profile or profiles directory (default: profiles/)
        verbose: Enable verbose output
        resolve_profiles: Enable automatic GOTO_PROFILE name resolution
        
    Returns:
        Exit code (0 = success, 1 = failure)
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
