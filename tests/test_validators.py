#!/usr/bin/env python3
"""
Unit Tests for duckyPad Pro Validators

Tests validation functions against edge cases, boundary conditions,
and orientation-specific limits.

Author: JamesDBartlett3
Date: 2025-11-23
"""

import sys
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))

from shared.validators import ( # type: ignore
    validate_profile_name,
    validate_key_label,
    validate_profile_count,
    validate_label_list,
    ValidationError,
    require_valid_profile_name,
    require_valid_key_label,
    require_valid_profile_count,
    MAX_PROFILES,
    MAX_PROFILE_NAME_LENGTH,
    MAX_LABEL_CHARS_PORTRAIT,
    MAX_LABEL_CHARS_PER_LINE_PORTRAIT,
    MAX_LABEL_CHARS_LANDSCAPE,
    MAX_LABEL_CHARS_PER_LINE_LANDSCAPE,
)


class TestResults:
    """Track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def pass_test(self, name: str):
        self.passed += 1
        print(f"  ✓ {name}")
    
    def fail_test(self, name: str, reason: str):
        self.failed += 1
        self.errors.append(f"{name}: {reason}")
        print(f"  ✗ {name}: {reason}")
    
    def print_summary(self):
        print("\n" + "=" * 60)
        print(f"Results: {self.passed} passed, {self.failed} failed")
        if self.errors:
            print("\nFailures:")
            for error in self.errors:
                print(f"  • {error}")
        print("=" * 60)
        return self.failed == 0


results = TestResults()


def test_profile_name_valid():
    """Test valid profile names"""
    print("\n--- Profile Name Validation (Valid Cases) ---")
    
    test_cases = [
        ("A", "Single character"),
        ("Test", "Short name"),
        ("MyProfile", "Standard name"),
        ("12345678901234", "Exactly 14 chars"),
        ("Profile-123", "With hyphen"),
        ("My_Profile", "With underscore"),
    ]
    
    for name, description in test_cases:
        valid, error = validate_profile_name(name)
        if valid and error == "":
            results.pass_test(f"{description}: '{name}'")
        else:
            results.fail_test(f"{description}: '{name}'", f"Expected valid, got error: {error}")


def test_profile_name_invalid():
    """Test invalid profile names"""
    print("\n--- Profile Name Validation (Invalid Cases) ---")
    
    test_cases = [
        ("", "Empty string"),
        ("ThisNameIsWayTooLongForDuckyPad", "Too long (30 chars)"),
        ("FifteenCharsHer", "15 chars (over limit)"),
        ("A" * 100, "Extremely long"),
    ]
    
    for name, description in test_cases:
        valid, error = validate_profile_name(name)
        if not valid and error:
            results.pass_test(f"{description}: rejected")
        else:
            results.fail_test(f"{description}: '{name}'", "Expected invalid, but passed")


def test_key_label_portrait_valid():
    """Test valid key labels in portrait mode"""
    print("\n--- Key Label Validation (Portrait - Valid) ---")
    
    test_cases = [
        ("", "", "Both empty"),
        ("A", "", "Single char line 1"),
        ("", "B", "Single char line 2"),
        ("Hello", "World", "Exactly at limit (10 total)"),
        ("ABCDE", "FGHIJ", "Both lines max (5 each)"),
        ("12345", "", "Line 1 max only"),
        ("", "67890", "Line 2 max only"),
        ("Test", "Key", "Normal label"),
    ]
    
    for z, x, description in test_cases:
        valid, error = validate_key_label(z, x, "portrait")
        if valid and error == "":
            results.pass_test(f"{description}: '{z}'/'{x}'")
        else:
            results.fail_test(f"{description}: '{z}'/'{x}'", f"Expected valid, got: {error}")


def test_key_label_portrait_invalid():
    """Test invalid key labels in portrait mode"""
    print("\n--- Key Label Validation (Portrait - Invalid) ---")
    
    test_cases = [
        ("ABCDEF", "", "Line 1 too long (6 chars)"),
        ("", "ABCDEF", "Line 2 too long (6 chars)"),
        ("ABCDE", "FGHIJK", "Total too long (11 chars)"),
        ("Hello!", "World!", "Both lines over (12 total)"),
        ("123456", "789012", "Way over limit"),
    ]
    
    for z, x, description in test_cases:
        valid, error = validate_key_label(z, x, "portrait")
        if not valid and error:
            results.pass_test(f"{description}: rejected")
        else:
            results.fail_test(f"{description}: '{z}'/'{x}'", "Expected invalid, but passed")


def test_key_label_landscape_valid():
    """Test valid key labels in landscape mode"""
    print("\n--- Key Label Validation (Landscape - Valid) ---")
    
    test_cases = [
        ("", "", "Both empty"),
        ("A", "", "Single char line 1"),
        ("", "B", "Single char line 2"),
        ("ABCD", "EFGH", "Exactly at limit (8 total)"),
        ("1234", "", "Line 1 max only"),
        ("", "5678", "Line 2 max only"),
        ("Test", "Key", "Normal label"),
    ]
    
    for z, x, description in test_cases:
        valid, error = validate_key_label(z, x, "landscape")
        if valid and error == "":
            results.pass_test(f"{description}: '{z}'/'{x}'")
        else:
            results.fail_test(f"{description}: '{z}'/'{x}'", f"Expected valid, got: {error}")


def test_key_label_landscape_invalid():
    """Test invalid key labels in landscape mode"""
    print("\n--- Key Label Validation (Landscape - Invalid) ---")
    
    test_cases = [
        ("ABCDE", "", "Line 1 too long (5 chars)"),
        ("", "ABCDE", "Line 2 too long (5 chars)"),
        ("ABCD", "EFGHI", "Total too long (9 chars)"),
        ("Hello", "World", "Both over (10 total)"),
        ("12345", "67890", "Way over limit"),
    ]
    
    for z, x, description in test_cases:
        valid, error = validate_key_label(z, x, "landscape")
        if not valid and error:
            results.pass_test(f"{description}: rejected")
        else:
            results.fail_test(f"{description}: '{z}'/'{x}'", "Expected invalid, but passed")


def test_unicode_and_emojis():
    """Test Unicode and emoji handling"""
    print("\n--- Unicode and Emoji Handling ---")
    
    test_cases = [
        ("Café", "", "portrait", "Accented chars (4 chars)"),
        ("日本語", "", "portrait", "CJK characters (3 chars)"),
        ("😀", "", "portrait", "Emoji (1 char)"),
        ("Test😀", "", "portrait", "Mixed ASCII+emoji (5 chars)"),
        ("🎮🎯🎲🎪", "", "portrait", "Multiple emojis (4 chars)"),
        ("Ñoño", "", "landscape", "Spanish chars (4 chars)"),
    ]
    
    for z, x, orientation, description in test_cases:
        valid, error = validate_key_label(z, x, orientation)
        char_count = len(z) + len(x)
        max_per_line = 4 if orientation == "landscape" else 5
        
        if len(z) <= max_per_line and len(x) <= max_per_line:
            if valid:
                results.pass_test(f"{description}: accepted")
            else:
                results.fail_test(f"{description}", f"Should be valid but got: {error}")
        else:
            if not valid:
                results.pass_test(f"{description}: rejected")
            else:
                results.fail_test(f"{description}", "Should be invalid but passed")


def test_profile_count_valid():
    """Test valid profile counts"""
    print("\n--- Profile Count Validation (Valid) ---")
    
    test_cases = [
        (1, "Single profile"),
        (10, "Ten profiles"),
        (32, "Half capacity"),
        (64, "Exactly at limit"),
    ]
    
    for count, description in test_cases:
        valid, error = validate_profile_count(count)
        if valid and error == "":
            results.pass_test(f"{description}: {count}")
        else:
            results.fail_test(f"{description}: {count}", f"Expected valid, got: {error}")


def test_profile_count_invalid():
    """Test invalid profile counts"""
    print("\n--- Profile Count Validation (Invalid) ---")
    
    test_cases = [
        (65, "One over limit"),
        (100, "Way over limit"),
        (128, "Double limit"),
    ]
    
    for count, description in test_cases:
        valid, error = validate_profile_count(count)
        if not valid and error:
            results.pass_test(f"{description}: {count} rejected")
        else:
            results.fail_test(f"{description}: {count}", "Expected invalid, but passed")


def test_label_list_helper():
    """Test validate_label_list convenience function"""
    print("\n--- Label List Helper Function ---")
    
    test_cases = [
        (["Test"], "portrait", True, "Single line label"),
        (["Line1", "Line2"], "portrait", True, "Two line label"),
        (["ABCDE", "FGHIJ"], "portrait", True, "Portrait max"),
        (["ABCDEF"], "portrait", False, "Over portrait limit"),
        (["ABCD", "EFGH"], "landscape", True, "Landscape max"),
        (["ABCDE"], "landscape", False, "Over landscape limit"),
    ]
    
    for labels, orientation, should_pass, description in test_cases:
        valid, error = validate_label_list(labels, orientation)
        if should_pass:
            if valid:
                results.pass_test(f"{description}")
            else:
                results.fail_test(f"{description}", f"Expected valid, got: {error}")
        else:
            if not valid:
                results.pass_test(f"{description}: rejected")
            else:
                results.fail_test(f"{description}", "Expected invalid, but passed")


def test_require_functions():
    """Test require_* functions that raise exceptions"""
    print("\n--- Require Functions (Exception Raising) ---")
    
    # Valid cases should not raise
    try:
        require_valid_profile_name("TestProfile")
        results.pass_test("require_valid_profile_name: valid name passes")
    except ValidationError as e:
        results.fail_test("require_valid_profile_name: valid name", f"Unexpected error: {e}")
    
    # Invalid cases should raise
    try:
        require_valid_profile_name("ThisNameIsWayTooLongForDuckyPad")
        results.fail_test("require_valid_profile_name: invalid name", "Should have raised ValidationError")
    except ValidationError:
        results.pass_test("require_valid_profile_name: invalid name raises")
    
    # Valid label should not raise
    try:
        require_valid_key_label("Test", "Key", "portrait")
        results.pass_test("require_valid_key_label: valid label passes")
    except ValidationError as e:
        results.fail_test("require_valid_key_label: valid label", f"Unexpected error: {e}")
    
    # Invalid label should raise
    try:
        require_valid_key_label("ABCDEF", "", "portrait")
        results.fail_test("require_valid_key_label: invalid label", "Should have raised ValidationError")
    except ValidationError:
        results.pass_test("require_valid_key_label: invalid label raises")
    
    # Valid count should not raise
    try:
        require_valid_profile_count(50)
        results.pass_test("require_valid_profile_count: valid count passes")
    except ValidationError as e:
        results.fail_test("require_valid_profile_count: valid count", f"Unexpected error: {e}")
    
    # Invalid count should raise
    try:
        require_valid_profile_count(100)
        results.fail_test("require_valid_profile_count: invalid count", "Should have raised ValidationError")
    except ValidationError:
        results.pass_test("require_valid_profile_count: invalid count raises")


def test_constants():
    """Test that constants are correct"""
    print("\n--- Constants Validation ---")
    
    if MAX_PROFILES == 64:
        results.pass_test("MAX_PROFILES = 64")
    else:
        results.fail_test("MAX_PROFILES", f"Expected 64, got {MAX_PROFILES}")
    
    if MAX_PROFILE_NAME_LENGTH == 14:
        results.pass_test("MAX_PROFILE_NAME_LENGTH = 14")
    else:
        results.fail_test("MAX_PROFILE_NAME_LENGTH", f"Expected 14, got {MAX_PROFILE_NAME_LENGTH}")
    
    if MAX_LABEL_CHARS_PORTRAIT == 10:
        results.pass_test("MAX_LABEL_CHARS_PORTRAIT = 10")
    else:
        results.fail_test("MAX_LABEL_CHARS_PORTRAIT", f"Expected 10, got {MAX_LABEL_CHARS_PORTRAIT}")
    
    if MAX_LABEL_CHARS_PER_LINE_PORTRAIT == 5:
        results.pass_test("MAX_LABEL_CHARS_PER_LINE_PORTRAIT = 5")
    else:
        results.fail_test("MAX_LABEL_CHARS_PER_LINE_PORTRAIT", f"Expected 5, got {MAX_LABEL_CHARS_PER_LINE_PORTRAIT}")
    
    if MAX_LABEL_CHARS_LANDSCAPE == 8:
        results.pass_test("MAX_LABEL_CHARS_LANDSCAPE = 8")
    else:
        results.fail_test("MAX_LABEL_CHARS_LANDSCAPE", f"Expected 8, got {MAX_LABEL_CHARS_LANDSCAPE}")
    
    if MAX_LABEL_CHARS_PER_LINE_LANDSCAPE == 4:
        results.pass_test("MAX_LABEL_CHARS_PER_LINE_LANDSCAPE = 4")
    else:
        results.fail_test("MAX_LABEL_CHARS_PER_LINE_LANDSCAPE", f"Expected 4, got {MAX_LABEL_CHARS_PER_LINE_LANDSCAPE}")


def main():
    """Run all tests"""
    print("=" * 60)
    print("duckyPad Pro Validator Unit Tests")
    print("=" * 60)
    
    test_constants()
    test_profile_name_valid()
    test_profile_name_invalid()
    test_key_label_portrait_valid()
    test_key_label_portrait_invalid()
    test_key_label_landscape_valid()
    test_key_label_landscape_invalid()
    test_unicode_and_emojis()
    test_profile_count_valid()
    test_profile_count_invalid()
    test_label_list_helper()
    test_require_functions()
    
    success = results.print_summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
