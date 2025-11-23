#!/usr/bin/env python3
"""
Validation Module for duckyPad Pro

Validates profiles, labels, and configurations against duckyPad Pro OS limitations.

Limits enforced:
- Profile count: 64 maximum
- Profile/layer names: 16 characters maximum
- Key labels (portrait): 10 chars total (5 per line)
- Key labels (landscape): 8 chars total (4 per line)

Author: JamesDBartlett3
Date: 2025-11-23
"""

from typing import Tuple, List, Optional
from pathlib import Path


class ValidationError(Exception):
    """Exception raised when validation fails"""
    pass


# System limits
MAX_PROFILES = 64
MAX_PROFILE_NAME_LENGTH = 16
MAX_LABEL_CHARS_PORTRAIT = 10
MAX_LABEL_CHARS_PER_LINE_PORTRAIT = 5
MAX_LABEL_CHARS_LANDSCAPE = 8
MAX_LABEL_CHARS_PER_LINE_LANDSCAPE = 4


def validate_profile_name(name: str, context: str = "Profile") -> Tuple[bool, str]:
    """Validate profile or layer name length.
    
    Args:
        name: Profile or layer name to validate
        context: Context string for error message (e.g., "Profile", "Layer")
        
    Returns:
        Tuple of (is_valid, error_message)
        error_message is empty string if valid
        
    Example:
        >>> validate_profile_name("MyProfile")
        (True, '')
        >>> validate_profile_name("ThisNameIsWayTooLongForDuckyPad")
        (False, 'Profile name "ThisNameIsWayTooLongForDuckyPad" exceeds 16 character limit (35 chars)')
    """
    if not name:
        return False, f"{context} name cannot be empty"
    
    char_count = len(name)
    
    if char_count > MAX_PROFILE_NAME_LENGTH:
        return False, (
            f'{context} name "{name}" exceeds {MAX_PROFILE_NAME_LENGTH} character limit '
            f'({char_count} chars)'
        )
    
    return True, ''


def validate_key_label(
    z_line: str,
    x_line: str,
    orientation: str = "portrait",
    key_num: Optional[int] = None
) -> Tuple[bool, str]:
    """Validate key label against orientation-specific limits.
    
    Args:
        z_line: First line of label (z directive)
        x_line: Second line of label (x directive)
        orientation: "portrait" or "landscape"
        key_num: Optional key number for error message
        
    Returns:
        Tuple of (is_valid, error_message)
        error_message is empty string if valid
        
    Example:
        >>> validate_key_label("Hello", "World", "portrait")
        (True, '')
        >>> validate_key_label("TooLong", "Label", "landscape")
        (False, 'Label line 1 "TooLong" exceeds 4 character limit for landscape (7 chars)')
    """
    z_line = z_line or ""
    x_line = x_line or ""
    
    # Determine limits based on orientation
    if orientation.lower() == "landscape":
        max_per_line = MAX_LABEL_CHARS_PER_LINE_LANDSCAPE
        max_total = MAX_LABEL_CHARS_LANDSCAPE
    else:  # portrait (default)
        max_per_line = MAX_LABEL_CHARS_PER_LINE_PORTRAIT
        max_total = MAX_LABEL_CHARS_PORTRAIT
    
    key_context = f"Key {key_num} l" if key_num else "L"
    
    # Check individual line limits
    z_count = len(z_line)
    if z_count > max_per_line:
        return False, (
            f'{key_context}abel line 1 "{z_line}" exceeds {max_per_line} character limit '
            f'for {orientation} ({z_count} chars)'
        )
    
    x_count = len(x_line)
    if x_count > max_per_line:
        return False, (
            f'{key_context}abel line 2 "{x_line}" exceeds {max_per_line} character limit '
            f'for {orientation} ({x_count} chars)'
        )
    
    # Check total character limit
    total_count = z_count + x_count
    if total_count > max_total:
        return False, (
            f'{key_context}abel total "{z_line}/{x_line}" exceeds {max_total} character limit '
            f'for {orientation} ({total_count} chars total)'
        )
    
    return True, ''


def validate_profile_count(profile_count: int, context: str = "Total profiles") -> Tuple[bool, str]:
    """Validate profile count against system limit.
    
    Args:
        profile_count: Number of profiles
        context: Context string for error message
        
    Returns:
        Tuple of (is_valid, error_message)
        error_message is empty string if valid
        
    Example:
        >>> validate_profile_count(50)
        (True, '')
        >>> validate_profile_count(65)
        (False, 'Total profiles (65) exceeds maximum limit of 64')
    """
    if profile_count > MAX_PROFILES:
        return False, (
            f'{context} ({profile_count}) exceeds maximum limit of {MAX_PROFILES}'
        )
    
    return True, ''


def get_char_count(text: str) -> int:
    """Get character count for validation.
    
    Currently uses simple len() which counts Unicode code points.
    May need adjustment if duckyPad Pro counts bytes or display width differently.
    
    Args:
        text: Text to count
        
    Returns:
        Character count
    """
    return len(text)


def validate_label_list(
    labels: List[str],
    orientation: str = "portrait",
    key_num: Optional[int] = None
) -> Tuple[bool, str]:
    """Validate label array (convenience wrapper).
    
    Args:
        labels: List of label strings [z_line, x_line] (or [z_line] for single line)
        orientation: "portrait" or "landscape"
        key_num: Optional key number for error message
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    z_line = labels[0] if len(labels) >= 1 else ""
    x_line = labels[1] if len(labels) >= 2 else ""
    
    return validate_key_label(z_line, x_line, orientation, key_num)


# Convenience functions for raising exceptions
def require_valid_profile_name(name: str, context: str = "Profile"):
    """Validate profile name and raise ValidationError if invalid.
    
    Args:
        name: Profile or layer name
        context: Context string for error message
        
    Raises:
        ValidationError: If name is invalid
    """
    valid, error = validate_profile_name(name, context)
    if not valid:
        raise ValidationError(error)


def require_valid_key_label(
    z_line: str,
    x_line: str,
    orientation: str = "portrait",
    key_num: Optional[int] = None
):
    """Validate key label and raise ValidationError if invalid.
    
    Args:
        z_line: First line of label
        x_line: Second line of label  
        orientation: "portrait" or "landscape"
        key_num: Optional key number for error message
        
    Raises:
        ValidationError: If label is invalid
    """
    valid, error = validate_key_label(z_line, x_line, orientation, key_num)
    if not valid:
        raise ValidationError(error)


def require_valid_profile_count(profile_count: int, context: str = "Total profiles"):
    """Validate profile count and raise ValidationError if invalid.
    
    Args:
        profile_count: Number of profiles
        context: Context string for error message
        
    Raises:
        ValidationError: If count exceeds limit
    """
    valid, error = validate_profile_count(profile_count, context)
    if not valid:
        raise ValidationError(error)
