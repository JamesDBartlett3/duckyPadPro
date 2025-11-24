#!/usr/bin/env python3
"""
Update Compiler Tool
Downloads the latest duckyPad Configurator Python files from GitHub and deploys them to the vendor folder.
"""

import argparse
import json
import shutil
import sys
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# Add shared directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from shared.console import print_color, print_verbose


class CompilerUpdater:
    """Download and update compiler files from GitHub"""
    
    # Configuration
    GITHUB_REPO = "duckyPad/duckyPad-Configurator"
    
    def __init__(self, verbose: bool = False, force: bool = False):
        """Initialize updater
        
        Args:
            verbose: Enable verbose output
            force: Force download even if files exist
        """
        self.verbose = verbose
        self.force = force
        self.script_dir = Path(__file__).parent
        self.vendor_dir = self.script_dir / "vendor"
    
    def check_existing_files(self) -> bool:
        """Check if any Python files exist in vendor directory
        
        Returns:
            True if Python files exist, False otherwise
        """
        if not self.vendor_dir.exists():
            return False
        
        py_files = list(self.vendor_dir.glob("*.py"))
        
        if not py_files:
            print_verbose("No Python files found in vendor directory", self.verbose)
            return False
        
        print_verbose(f"Found {len(py_files)} Python files in vendor directory", self.verbose)
        return True
    
    def download_compiler(self) -> bool:
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
            req.add_header("User-Agent", "duckyPad-Compiler-Updater")
            
            print_verbose(f"Fetching release info from: {api_url}", self.verbose)
            
            with urlopen(req, timeout=10) as response:
                release_data = json.loads(response.read().decode())
            
            # Display release info
            release_tag = release_data.get("tag_name", "unknown")
            release_name = release_data.get("name", "unknown")
            print_color(f"Latest release: {release_name} ({release_tag})", "cyan")
            
            # Find zipball URL
            zipball_url = release_data.get("zipball_url")
            if not zipball_url:
                print_color("✗ Could not find release download URL", "red")
                return False
            
            print_verbose(f"Downloading from: {zipball_url}", self.verbose)
            
            # Download zipball
            zip_path = self.vendor_dir / "release.zip"
            req = Request(zipball_url)
            req.add_header("User-Agent", "duckyPad-Compiler-Updater")
            
            print_color("Downloading release archive...", "cyan")
            with urlopen(req, timeout=30) as response:
                with open(zip_path, "wb") as f:
                    f.write(response.read())
            
            print_verbose("✓ Download complete", self.verbose)
            
            # Extract required files
            print_color("Extracting Python files...", "cyan")
            extracted_count = 0
            
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                # Find root folder in zip
                namelist = zip_ref.namelist()
                root_folder = namelist[0].split("/")[0] if namelist else ""
                
                if self.verbose:
                    print_verbose(f"Archive root folder: {root_folder}", self.verbose)
                    print_verbose(f"Total files in archive: {len(namelist)}", self.verbose)
                
                # Extract all .py files from src/ directory
                src_prefix = f"{root_folder}/src/"
                for file_path in namelist:
                    # Only process .py files in src/ directory
                    if not file_path.startswith(src_prefix) or not file_path.endswith(".py"):
                        continue
                    
                    # Get just the filename
                    filename = file_path.split("/")[-1]
                    
                    # Skip if it's a directory entry
                    if not filename:
                        continue
                    
                    if self.verbose:
                        print_verbose(f"  Extracting: {filename}", self.verbose)
                    
                    # Extract to vendor directory
                    zip_ref.extract(file_path, self.vendor_dir)
                    # Move from nested folder to vendor root
                    extracted_path = self.vendor_dir / file_path
                    target_path = self.vendor_dir / filename
                    
                    # Remove existing file if present
                    if target_path.exists():
                        target_path.unlink()
                    
                    shutil.move(str(extracted_path), str(target_path))
                    extracted_count += 1
                    print_color(f"  ✓ {filename}", "green")
            
            # Clean up
            zip_path.unlink()
            
            # Remove extracted folder if it exists
            extracted_folder = self.vendor_dir / root_folder
            if extracted_folder.exists():
                shutil.rmtree(extracted_folder)
            
            print_color(f"\n✓ Successfully extracted {extracted_count} Python files", "green")
            return extracted_count > 0
            
        except (URLError, HTTPError) as e:
            print_color(f"✗ Network error: {e}", "red")
            return False
        except Exception as e:
            print_color(f"✗ Error fetching compiler: {e}", "red")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False
    
    def update(self) -> int:
        """Update compiler files
        
        Returns:
            0 if successful, 1 if failed
        """
        print_color("duckyPad Compiler Updater", "cyan")
        print_color("=" * 60, "cyan")
        
        # Check if files exist
        files_exist = self.check_existing_files()
        
        if files_exist and not self.force:
            print_color("\n✓ Compiler files already present", "green")
            print_color("  Use --force to re-download", "yellow")
            return 0
        
        if files_exist and self.force:
            print_color("\n→ Force flag set, re-downloading compiler files...", "yellow")
        
        # Download compiler
        success = self.download_compiler()
        
        if success:
            print_color("\n✓ Compiler update complete!", "green")
            print_color(f"  Files installed to: {self.vendor_dir}", "cyan")
            return 0
        else:
            print_color("\n✗ Compiler update failed", "red")
            return 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Download and update duckyPad compiler files from GitHub",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check and download if missing
  python vendor.py
  
  # Force re-download
  python vendor.py -f
  
  # Verbose output
  python vendor.py -v
        """
    )
    
    parser.add_argument("-v", "--verbose", action="store_true", 
                       help="Verbose output")
    parser.add_argument("-f", "--force", action="store_true",
                       help="Force download even if files exist")
    
    args = parser.parse_args()
    
    updater = CompilerUpdater(verbose=args.verbose, force=args.force)
    return updater.update()


if __name__ == "__main__":
    sys.exit(main())
