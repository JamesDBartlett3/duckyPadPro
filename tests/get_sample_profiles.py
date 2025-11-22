#!/usr/bin/env python3
"""
Sample Profiles Downloader
Downloads official sample profiles from the duckyPad-Pro repository
"""

import argparse
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


class SampleProfilesDownloader:
    """Download sample profiles from GitHub"""
    
    # Configuration
    REPO = "dekuNukem/duckyPad-Pro"
    SAMPLE_PROFILES_URL = f"https://github.com/{REPO}/raw/master/resources/sample_profiles/sample_profiles.zip"
    
    def __init__(self, force: bool = False, verbose: bool = False):
        """Initialize downloader
        
        Args:
            force: Force re-download even if profiles exist
            verbose: Enable verbose output
        """
        self.force = force
        self.verbose = verbose
        # Destination is profiles/sample_profiles/ from tests/ directory
        self.script_dir = Path(__file__).parent
        self.sample_profiles_dir = self.script_dir.parent / "profiles" / "sample_profiles"
    
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
    
    def _check_existing(self) -> bool:
        """Check if sample profiles already exist
        
        Returns:
            True if exists and should skip download, False otherwise
        """
        if self.sample_profiles_dir.exists() and not self.force:
            self._print_color(f"✓ Sample profiles already exist at: {self.sample_profiles_dir}", "green")
            self._print_color("  Use --force to re-download", "gray")
            return True
        return False
    
    def _download_zip(self, temp_zip: Path) -> bool:
        """Download sample profiles ZIP file
        
        Args:
            temp_zip: Path to save downloaded ZIP
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._print_color("Downloading sample_profiles.zip...", "cyan")
            self._print_verbose(f"URL: {self.SAMPLE_PROFILES_URL}")
            
            req = Request(self.SAMPLE_PROFILES_URL)
            req.add_header("User-Agent", "duckyPad-SampleProfiles-Downloader")
            
            with urlopen(req, timeout=30) as response:
                with open(temp_zip, "wb") as f:
                    f.write(response.read())
            
            self._print_verbose(f"Downloaded to: {temp_zip}")
            return True
            
        except (URLError, HTTPError) as e:
            self._print_color(f"Network error: {e}", "red")
            return False
        except Exception as e:
            self._print_color(f"Download error: {e}", "red")
            return False
    
    def _extract_zip(self, temp_zip: Path, temp_extract: Path) -> bool:
        """Extract ZIP file
        
        Args:
            temp_zip: Path to ZIP file
            temp_extract: Path to extract to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._print_color("Extracting sample profiles...", "cyan")
            
            # Clean up old extraction
            if temp_extract.exists():
                self._print_verbose(f"Removing old extraction: {temp_extract}")
                shutil.rmtree(temp_extract)
            
            # Extract ZIP
            with zipfile.ZipFile(temp_zip, "r") as zip_ref:
                zip_ref.extractall(temp_extract)
            
            self._print_verbose(f"Extracted to: {temp_extract}")
            return True
            
        except Exception as e:
            self._print_color(f"Extraction error: {e}", "red")
            return False
    
    def _count_profiles(self) -> int:
        """Count profile directories
        
        Returns:
            Number of profile directories found
        """
        if not self.sample_profiles_dir.exists():
            return 0
        
        try:
            profile_dirs = [
                d for d in self.sample_profiles_dir.iterdir()
                if d.is_dir()
            ]
            return len(profile_dirs)
        except Exception:
            return 0
    
    def download(self) -> bool:
        """Download sample profiles
        
        Returns:
            True if successful, False otherwise
        """
        # Check if already exists
        if self._check_existing():
            return True
        
        self._print_color("Downloading sample profiles from GitHub...", "cyan")
        self._print_color(f"Repository: {self.REPO}\n", "gray")
        
        # Create temporary files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            temp_zip = temp_dir_path / "sample_profiles.zip"
            temp_extract = temp_dir_path / "sample_profiles_extract"
            
            # Download ZIP
            if not self._download_zip(temp_zip):
                return False
            
            # Remove existing sample_profiles if using force
            if self.sample_profiles_dir.exists():
                self._print_color("Removing existing sample_profiles...", "yellow")
                shutil.rmtree(self.sample_profiles_dir)
            
            # Extract ZIP
            if not self._extract_zip(temp_zip, temp_extract):
                return False
            
            # Move extracted content to sample_profiles folder
            try:
                shutil.move(str(temp_extract), str(self.sample_profiles_dir))
                self._print_verbose(f"Moved to: {self.sample_profiles_dir}")
            except Exception as e:
                self._print_color(f"Error moving files: {e}", "red")
                return False
        
        # Count profiles
        profile_count = self._count_profiles()
        
        if profile_count > 0:
            self._print_color(f"✓ Successfully downloaded {profile_count} sample profile{'s' if profile_count != 1 else ''}", "green")
        else:
            self._print_color("✓ Sample profiles downloaded", "green")
        
        self._print_color(f"  Location: {self.sample_profiles_dir}", "gray")
        
        return True
    
    def run(self) -> int:
        """Run the downloader
        
        Returns:
            Exit code (0 for success, 1 for failure)
        """
        self._print_color("\n=== duckyPad Pro Sample Profiles Downloader ===", "cyan")
        
        if not self.download():
            self._print_color("\n✗ Failed to download sample profiles", "red")
            return 1
        
        self._print_color("\n✓ Sample profiles ready!", "green")
        self._print_color("  You can now reference these profiles when creating your own.", "gray")
        
        return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Download official sample profiles from duckyPad-Pro repository"
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Force re-download even if profiles exist"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    downloader = SampleProfilesDownloader(
        force=args.force,
        verbose=args.verbose
    )
    
    exit_code = downloader.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
