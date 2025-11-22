#!/usr/bin/env python3
"""
README Generator
Automatically generates readme-{dirname}.md files for directories
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Tuple


class ReadmeInfo:
    """Information about a readme file"""
    
    def __init__(self, directory: Path):
        """Initialize readme info
        
        Args:
            directory: Directory path
        """
        self.name = directory.name
        self.fullname = str(directory)
        self.path = directory / f"readme-{self.name}.md"


class ReadmeGenerator:
    """Generate README files for directory structure"""
    
    def __init__(self, root_path: Path, overwrite: bool = False, force: bool = False, verbose: bool = False):
        """Initialize generator
        
        Args:
            root_path: Root directory to process
            overwrite: Overwrite existing files
            force: Skip confirmation prompts
            verbose: Enable verbose output
        """
        self.root_path = root_path
        self.overwrite = overwrite
        self.force = force
        self.verbose = verbose
    
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
            self._print_color(f"  {message}", "cyan")
    
    def _get_directories(self) -> List[Path]:
        """Get all directories recursively
        
        Returns:
            List of directory paths
        """
        if not self.root_path.exists():
            self._print_color(f"Path not found: {self.root_path}", "red")
            return []
        
        if not self.root_path.is_dir():
            self._print_color(f"Not a directory: {self.root_path}", "red")
            return []
        
        # Get all subdirectories recursively
        directories = [d for d in self.root_path.rglob("*") if d.is_dir()]
        return sorted(directories)
    
    def _get_files_to_overwrite(self, directories: List[Path]) -> List[Path]:
        """Get list of existing readme files that would be overwritten
        
        Args:
            directories: List of directories to check
            
        Returns:
            List of readme file paths that exist
        """
        files = []
        for directory in directories:
            readme_info = ReadmeInfo(directory)
            if readme_info.path.exists():
                files.append(readme_info.path)
        return files
    
    def _prompt_overwrite(self, files: List[Path]) -> bool:
        """Prompt user to confirm overwrite
        
        Args:
            files: List of files that will be overwritten
            
        Returns:
            True if user confirms, False otherwise
        """
        if not files:
            return True
        
        self._print_color("The following files will be overwritten:", "yellow")
        for file in files:
            print(f"  {file}")
        print()
        
        try:
            response = input("Continue? (Y/n): ").strip()
            return response.upper() == 'Y' or response == ''
        except (KeyboardInterrupt, EOFError):
            print()
            return False
    
    def _is_file_empty(self, path: Path) -> bool:
        """Check if file is empty or whitespace-only
        
        Args:
            path: File path to check
            
        Returns:
            True if file doesn't exist or is empty/whitespace-only
        """
        if not path.exists():
            return True
        
        try:
            content = path.read_text(encoding='utf-8').strip()
            return len(content) == 0
        except Exception:
            return True
    
    def _get_subdirectories(self, directory: Path) -> List[Path]:
        """Get immediate subdirectories (non-recursive)
        
        Args:
            directory: Directory to check
            
        Returns:
            List of subdirectory paths
        """
        try:
            subdirs = [d for d in directory.iterdir() if d.is_dir()]
            return sorted(subdirs)
        except Exception:
            return []
    
    def _create_parent_readme(self, readme_info: ReadmeInfo, subdirs: List[Path]) -> str:
        """Create README content for parent directory with table of contents
        
        Args:
            readme_info: Readme information
            subdirs: List of subdirectories
            
        Returns:
            README content
        """
        content = f"# {readme_info.name}\n\n"
        
        for subdir in subdirs:
            subdir_name = subdir.name
            content += f"## [{subdir_name}]({subdir_name}/readme-{subdir_name}.md)\n\n"
        
        return content
    
    def _create_leaf_readme(self, readme_info: ReadmeInfo) -> str:
        """Create README content for leaf directory (no subdirectories)
        
        Args:
            readme_info: Readme information
            
        Returns:
            README content
        """
        return f"# {readme_info.name}\n"
    
    def _write_readme(self, path: Path, content: str) -> bool:
        """Write README file
        
        Args:
            path: File path
            content: Content to write
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure content ends without trailing newline (matches PowerShell -NoNewline)
            content = content.rstrip('\n')
            path.write_text(content, encoding='utf-8')
            return True
        except Exception as e:
            self._print_color(f"Error writing {path}: {e}", "red")
            return False
    
    def process_directory(self, directory: Path) -> bool:
        """Process a single directory
        
        Args:
            directory: Directory to process
            
        Returns:
            True if readme was created/updated, False otherwise
        """
        readme_info = ReadmeInfo(directory)
        subdirs = self._get_subdirectories(directory)
        
        if subdirs:
            # Parent directory: check if file is empty or whitespace-only
            file_exists = readme_info.path.exists()
            file_is_empty = self._is_file_empty(readme_info.path)
            should_write = (not file_exists) or self.overwrite or file_is_empty
            
            if should_write:
                content = self._create_parent_readme(readme_info, subdirs)
                if self._write_readme(readme_info.path, content):
                    self._print_verbose(f"Created parent README: {readme_info.path}")
                    return True
            else:
                self._print_verbose(f"Skipped (exists): {readme_info.path}")
        else:
            # Leaf directory: create simple heading
            if not readme_info.path.exists() or self.overwrite:
                content = self._create_leaf_readme(readme_info)
                if self._write_readme(readme_info.path, content):
                    self._print_verbose(f"Created leaf README: {readme_info.path}")
                    return True
            else:
                self._print_verbose(f"Skipped (exists): {readme_info.path}")
        
        return False
    
    def run(self) -> int:
        """Run the generator
        
        Returns:
            Exit code (0 for success, 1 for failure)
        """
        self._print_color("\n" + "=" * 60, "cyan")
        self._print_color("README Generator", "cyan")
        self._print_color("=" * 60, "cyan")
        
        # Get all directories
        directories = self._get_directories()
        
        if not directories:
            self._print_color("\nNo directories found", "yellow")
            return 0
        
        self._print_color(f"\nFound {len(directories)} director{'y' if len(directories) == 1 else 'ies'}", "white")
        
        # Check for existing files if overwrite without force
        if self.overwrite and not self.force:
            files_to_overwrite = self._get_files_to_overwrite(directories)
            if files_to_overwrite:
                if not self._prompt_overwrite(files_to_overwrite):
                    self._print_color("\nOperation cancelled.", "red")
                    return 1
        
        # Process directories
        created = 0
        for directory in directories:
            if self.process_directory(directory):
                created += 1
        
        # Print summary
        self._print_color("\n" + "=" * 60, "cyan")
        self._print_color("Summary", "cyan")
        self._print_color("=" * 60, "cyan")
        self._print_color(f"Processed: {len(directories)} director{'y' if len(directories) == 1 else 'ies'}", "white")
        self._print_color(f"Created:   {created} README file{'s' if created != 1 else ''}", "green")
        self._print_color("\n✓ Complete!", "green")
        
        return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate readme-{dirname}.md files for directories"
    )
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=Path.cwd(),
        help="Root directory to process (default: current directory)"
    )
    parser.add_argument(
        "-o", "--overwrite",
        action="store_true",
        help="Overwrite existing README files"
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Skip confirmation prompts"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Resolve path
    root_path = args.path
    if not root_path.is_absolute():
        root_path = Path.cwd() / root_path
    
    generator = ReadmeGenerator(
        root_path=root_path,
        overwrite=args.overwrite,
        force=args.force,
        verbose=args.verbose
    )
    
    exit_code = generator.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
