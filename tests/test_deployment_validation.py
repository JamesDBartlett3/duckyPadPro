#!/usr/bin/env python3
"""
Test deployment validation without SD card

Tests profile count and name validation logic.
"""
import sys
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))

from shared.validators import ( # type: ignore
    ValidationError,
    validate_profile_count,
    validate_profile_name,
    require_valid_profile_count,
    require_valid_profile_name,
    MAX_PROFILES,
)
from shared.console import print_color # type: ignore


def test_profile_count_validation():
    """Test profile count validation"""
    print_color("\n--- Profile Count Validation ---", "cyan")
    
    # Simulate deployment scenarios
    test_cases = [
        (10, 5, True, "Deploy 5 profiles to SD card with 10 existing"),
        (50, 10, True, "Deploy 10 profiles to SD card with 50 existing"),
        (64, 0, True, "Deploy 0 profiles to SD card with 64 existing (at limit)"),
        (60, 4, True, "Deploy 4 profiles to SD card with 60 existing (reaches limit)"),
        (60, 5, False, "Deploy 5 profiles to SD card with 60 existing (exceeds by 1)"),
        (64, 1, False, "Deploy 1 profile to SD card with 64 existing (already at limit)"),
        (50, 20, False, "Deploy 20 profiles to SD card with 50 existing (exceeds by 6)"),
    ]
    
    passed = 0
    failed = 0
    
    for existing, to_deploy, should_pass, description in test_cases:
        total = existing + to_deploy
        try:
            require_valid_profile_count(total, context=f"test ({existing} + {to_deploy})")
            if should_pass:
                print_color(f"  ✓ {description}", "green")
                passed += 1
            else:
                print_color(f"  ✗ {description} - should have failed", "red")
                failed += 1
        except ValidationError as e:
            if not should_pass:
                print_color(f"  ✓ {description} - correctly rejected", "green")
                passed += 1
            else:
                print_color(f"  ✗ {description} - incorrectly rejected: {e}", "red")
                failed += 1
    
    return passed, failed


def test_profile_name_validation():
    """Test profile name validation"""
    print_color("\n--- Profile Name Validation ---", "cyan")
    
    test_cases = [
        ("ValidName", True, "Valid profile name"),
        ("Test123", True, "Name with numbers"),
        ("My-Profile", True, "Name with hyphen"),
        ("Profile_1", True, "Name with underscore"),
        ("1234567890123456", True, "Exactly 16 chars"),
        ("12345678901234567", False, "17 chars (over limit)"),
        ("ThisNameIsTooLong", False, "Name too long (17 chars)"),
        ("", False, "Empty name"),
    ]
    
    passed = 0
    failed = 0
    
    for name, should_pass, description in test_cases:
        try:
            require_valid_profile_name(name, context="test")
            if should_pass:
                print_color(f"  ✓ {description}: '{name}'", "green")
                passed += 1
            else:
                print_color(f"  ✗ {description}: '{name}' - should have failed", "red")
                failed += 1
        except ValidationError as e:
            if not should_pass:
                print_color(f"  ✓ {description}: correctly rejected", "green")
                passed += 1
            else:
                print_color(f"  ✗ {description}: '{name}' - incorrectly rejected", "red")
                failed += 1
    
    return passed, failed


def main():
    """Run all tests"""
    print_color("=" * 60, "cyan")
    print_color("Deployment Validation Tests", "cyan")
    print_color("=" * 60, "cyan")
    
    count_passed, count_failed = test_profile_count_validation()
    name_passed, name_failed = test_profile_name_validation()
    
    total_passed = count_passed + name_passed
    total_failed = count_failed + name_failed
    
    print_color("\n" + "=" * 60, "cyan")
    print_color(f"Results: {total_passed} passed, {total_failed} failed", "white")
    print_color("=" * 60, "cyan")
    
    if total_failed > 0:
        print_color(f"\n✗ {total_failed} test(s) failed", "red")
        return 1
    else:
        print_color("\n✓ All tests passed!", "green")
        return 0


if __name__ == "__main__":
    sys.exit(main())
