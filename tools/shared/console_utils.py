#!/usr/bin/env python3
"""
Console Utilities
Shared functions for colored terminal output and user interaction
"""

from typing import Optional


# ANSI color codes
COLORS = {
    "green": "\033[92m",
    "red": "\033[91m",
    "yellow": "\033[93m",
    "cyan": "\033[96m",
    "white": "\033[97m",
    "gray": "\033[90m",
    "reset": "\033[0m"
}


def print_color(message: str, color: str = "white") -> None:
    """Print colored message to console
    
    Args:
        message: Message to print
        color: Color name (green, red, yellow, cyan, white, gray)
    """
    color_code = COLORS.get(color, COLORS["white"])
    print(f"{color_code}{message}{COLORS['reset']}")


def print_success(message: str) -> None:
    """Print success message in green
    
    Args:
        message: Success message to print
    """
    print_color(message, "green")


def print_error(message: str) -> None:
    """Print error message in red
    
    Args:
        message: Error message to print
    """
    print_color(message, "red")


def print_warning(message: str) -> None:
    """Print warning message in yellow
    
    Args:
        message: Warning message to print
    """
    print_color(message, "yellow")


def print_info(message: str) -> None:
    """Print info message in cyan
    
    Args:
        message: Info message to print
    """
    print_color(message, "cyan")


def print_verbose(message: str, verbose: bool = True, indent: bool = True) -> None:
    """Print verbose message if verbose mode enabled
    
    Args:
        message: Message to print
        verbose: Whether to print the message
        indent: Whether to indent the message with spaces
    """
    if verbose:
        prefix = "  " if indent else ""
        print_color(f"{prefix}{message}", "cyan")


def prompt_yes_no(question: str, default: bool = True, force: bool = False) -> bool:
    """Prompt user for yes/no confirmation
    
    Args:
        question: Question to ask user
        default: Default answer if user just presses Enter (True=yes, False=no)
        force: Skip prompt and return True
        
    Returns:
        True for yes, False for no
    """
    if force:
        return True
    
    default_str = "Y/n" if default else "y/N"
    response = input(f"{question} [{default_str}]: ").strip().lower()
    
    if not response:
        return default
    
    return response in ("y", "yes")
