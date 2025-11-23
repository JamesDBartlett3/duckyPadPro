#!/usr/bin/env python3
"""
Test ProfileInfoManager
"""

import sys
from pathlib import Path

# Add tools directory to path
tools_path = Path(__file__).parent.parent / "tools"
sys.path.insert(0, str(tools_path))

from shared.profiles import ProfileInfoManager  # type: ignore

def test_sd_detection():
    """Test SD card detection"""
    print("=" * 60)
    print("Testing SD Card Detection")
    print("=" * 60)
    
    manager = ProfileInfoManager()
    sd_card = manager.detect_sd_card()
    
    if sd_card:
        print(f"✓ SD card found: {sd_card}")
        return sd_card
    else:
        print("✗ SD card not found")
        return None


def test_profile_parsing(sd_card: Path):
    """Test profile_info.txt parsing"""
    print("\n" + "=" * 60)
    print("Testing profile_info.txt Parsing")
    print("=" * 60)
    
    manager = ProfileInfoManager()
    mapping = manager.parse_profile_info(sd_card)
    
    if mapping:
        print(f"✓ Loaded {len(mapping)} profiles:")
        for name, index in sorted(mapping.items(), key=lambda x: x[1]):
            print(f"  {index:2d}: {name}")
        return mapping
    else:
        print("✗ No profiles loaded")
        return {}


def test_transform():
    """Test GOTO_PROFILE transformation"""
    print("\n" + "=" * 60)
    print("Testing GOTO_PROFILE Transformation")
    print("=" * 60)
    
    manager = ProfileInfoManager()
    
    if not manager.load_profile_mapping():
        print("✗ Could not load profile mapping")
        return
    
    test_scripts = [
        "GOTO_PROFILE Welcome",
        "GOTO_PROFILE Firefox",
        "GOTO_PROFILE NonExistent",
        "GOTO_PROFILE 5",
        "KEYDOWN CTRL\nGOTO_PROFILE Chrome\nKEYUP CTRL",
    ]
    
    for script in test_scripts:
        transformed, warnings = manager.transform_goto_commands(script)
        print(f"\nOriginal:    {repr(script)}")
        print(f"Transformed: {repr(transformed)}")
        if warnings:
            for warning in warnings:
                print(f"  Warning: {warning}")


def main():
    """Run all tests"""
    sd_card = test_sd_detection()
    
    if sd_card:
        mapping = test_profile_parsing(sd_card)
        if mapping:
            test_transform()
    
    print("\n" + "=" * 60)
    print("Tests Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
