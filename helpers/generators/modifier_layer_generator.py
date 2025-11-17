#!/usr/bin/env python3
"""
duckyPad Pro Modifier Layer Generator

Generates paired profiles for modifier layer functionality:
- Main profile: Contains switcher key(s) that hold modifier and switch to layer
- Layer profile: Contains simple keys that combine with held modifier

Example use case: Foxhole game controls
- Main profile has CTRL key (key 1) that holds CTRL and switches to Foxhole-Ctrl
- Foxhole-Ctrl profile has A, B, C, etc. that work as CTRL+A, CTRL+B, CTRL+C
- Release CTRL key to return to main profile

Author: duckyPad Pro Community
Date: 2025-11-16
"""

import argparse
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.key_layout import (
    PHYSICAL_KEYS,
    TOTAL_KEYS,
    print_both_layouts,
    parse_key_list,
    get_key_description,
)


def create_profile_directories(base_path, main_name, layer_name):
    """
    Create profile directories.
    
    Args:
        base_path: Base directory for profiles
        main_name: Main profile name
        layer_name: Layer profile name
    
    Returns:
        Tuple of (main_path, layer_path)
    """
    main_path = Path(base_path) / main_name
    layer_path = Path(base_path) / layer_name
    
    main_path.mkdir(parents=True, exist_ok=True)
    layer_path.mkdir(parents=True, exist_ok=True)
    
    return main_path, layer_path


def generate_switcher_press(modifier, layer_name):
    """
    Generate switcher key press script.
    
    Args:
        modifier: Modifier key name (CTRL, SHIFT, ALT, etc.)
        layer_name: Target layer profile name
    
    Returns:
        duckyScript content
    """
    return f"""DEFAULTDELAY 0
KEYDOWN {modifier}
GOTO_PROFILE {layer_name}
"""


def generate_switcher_release(modifier, main_name):
    """
    Generate switcher key release script.
    
    Args:
        modifier: Modifier key name (CTRL, SHIFT, ALT, etc.)
        main_name: Main profile name to return to
    
    Returns:
        duckyScript content
    """
    return f"""DEFAULTDELAY 0
KEYUP {modifier}
GOTO_PROFILE {main_name}
"""


def generate_simple_key(key_name):
    """
    Generate simple key press script.
    
    Args:
        key_name: Key name (A, B, C, F1, etc.)
    
    Returns:
        duckyScript content
    """
    return f"""DEFAULTDELAY 0
{key_name}
"""


def main():
    parser = argparse.ArgumentParser(
        description="Generate duckyPad Pro modifier layer profiles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show key layouts
  python modifier_layer_generator.py --show-layout

  # Create Ctrl layer with key 1 as switcher
  python modifier_layer_generator.py Foxhole --modifier CTRL --switcher 1 \\
    --layer-keys 6,8,10,11,12,14,16

  # Create Shift layer with multiple switchers in landscape mode
  python modifier_layer_generator.py MyProfile --modifier SHIFT \\
    --switcher 1,2 --layer-keys 3-10 --landscape

  # Full example with colors
  python modifier_layer_generator.py Gaming --modifier ALT --switcher 5 \\
    --layer-keys 1,2,3,6,7,8 --bg-color 128,0,255 --switcher-color 255,0,0
        """
    )
    
    # Positional arguments
    parser.add_argument(
        'main_profile',
        nargs='?',
        help='Main profile name (e.g., "Foxhole", "Gaming")'
    )
    
    # Layout display
    parser.add_argument(
        '--show-layout',
        action='store_true',
        help='Show key layout diagrams and exit'
    )
    
    # Required configuration
    parser.add_argument(
        '--modifier',
        choices=['CTRL', 'SHIFT', 'ALT', 'COMMAND', 'WINDOWS', 'GUI'],
        help='Modifier key to hold (CTRL, SHIFT, ALT, COMMAND, WINDOWS, GUI)'
    )
    
    parser.add_argument(
        '--switcher',
        help='Switcher key(s) in main profile (e.g., "1" or "1,2,5")'
    )
    
    parser.add_argument(
        '--layer-keys',
        help='Keys to include in layer profile (e.g., "6,8,10" or "1-10")'
    )
    
    # Optional configuration
    parser.add_argument(
        '--layer-suffix',
        default=None,
        help='Suffix for layer profile name (default: "-{modifier}")'
    )
    
    parser.add_argument(
        '--output-dir',
        default='.',
        help='Output directory for profiles (default: current directory)'
    )
    
    parser.add_argument(
        '--landscape',
        action='store_true',
        help='Use landscape orientation'
    )
    
    parser.add_argument(
        '--bg-color',
        help='Background color as R,G,B (e.g., "100,150,200")'
    )
    
    parser.add_argument(
        '--switcher-color',
        help='Switcher key color as R,G,B (e.g., "255,0,0")'
    )
    
    parser.add_argument(
        '--layer-color',
        help='Layer key color as R,G,B (e.g., "0,255,0")'
    )
    
    parser.add_argument(
        '--key-mapping',
        help='JSON file with key-to-action mappings'
    )
    
    args = parser.parse_args()
    
    # Show layout and exit if requested
    if args.show_layout:
        print_both_layouts()
        return 0
    
    # Validate required arguments
    if not args.main_profile:
        parser.error("main_profile is required (use --show-layout to see key layouts)")
    
    if not args.modifier:
        parser.error("--modifier is required")
    
    if not args.switcher:
        parser.error("--switcher is required")
    
    if not args.layer_keys:
        parser.error("--layer-keys is required")
    
    # Parse arguments
    switcher_keys = parse_key_list(args.switcher)
    layer_keys = parse_key_list(args.layer_keys)
    
    # Check for overlap
    overlap = set(switcher_keys) & set(layer_keys)
    if overlap:
        print(f"Warning: Keys {overlap} are in both switcher and layer lists")
    
    # Determine layer profile name
    layer_suffix = args.layer_suffix or f"-{args.modifier}"
    layer_name = args.main_profile + layer_suffix
    
    print(f"Generating modifier layer profiles:")
    print(f"  Main profile: {args.main_profile}")
    print(f"  Layer profile: {layer_name}")
    print(f"  Modifier: {args.modifier}")
    print(f"  Switcher keys: {switcher_keys}")
    print(f"  Layer keys: {layer_keys}")
    print(f"  Orientation: {'Landscape' if args.landscape else 'Portrait'}")
    print()
    
    # Create directories
    main_path, layer_path = create_profile_directories(
        args.output_dir,
        args.main_profile,
        layer_name
    )
    
    print(f"Created directories:")
    print(f"  {main_path}")
    print(f"  {layer_path}")
    print()
    
    # Generate switcher keys in main profile
    print("Generating switcher keys in main profile...")
    for key_num in switcher_keys:
        # Press: Hold modifier and switch to layer
        press_file = main_path / f"key{key_num}.txt"
        with open(press_file, 'w') as f:
            f.write(generate_switcher_press(args.modifier, layer_name))
        
        # Release: Release modifier (returns to main automatically)
        release_file = main_path / f"key{key_num}-release.txt"
        with open(release_file, 'w') as f:
            f.write(generate_switcher_release(args.modifier, args.main_profile))
        
        print(f"  ✓ Key {key_num} (switcher)")
    
    # Generate return switchers in layer profile
    print("\nGenerating return switchers in layer profile...")
    for key_num in switcher_keys:
        # Press: Keep modifier held
        press_file = layer_path / f"key{key_num}.txt"
        with open(press_file, 'w') as f:
            f.write(f"DEFAULTDELAY 0\nKEYDOWN {args.modifier}\n")
        
        # Release: Release modifier and return to main
        release_file = layer_path / f"key{key_num}-release.txt"
        with open(release_file, 'w') as f:
            f.write(f"DEFAULTDELAY 0\nKEYUP {args.modifier}\nGOTO_PROFILE {args.main_profile}\n")
        
        print(f"  ✓ Key {key_num} (return switcher)")
    
    # Generate simple keys in layer profile
    print("\nGenerating layer keys...")
    for key_num in layer_keys:
        # Skip if this is also a switcher
        if key_num in switcher_keys:
            continue
        
        # Simple key press (will combine with held modifier)
        press_file = layer_path / f"key{key_num}.txt"
        # TODO: Get actual key mapping from args.key_mapping or use default
        key_name = f"KEY{key_num}"  # Placeholder
        with open(press_file, 'w') as f:
            f.write(generate_simple_key(key_name))
        
        print(f"  ✓ Key {key_num} (layer key)")
    
    # TODO: Generate config files
    # TODO: Generate README files
    
    print("\n✓ Profile generation complete!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
