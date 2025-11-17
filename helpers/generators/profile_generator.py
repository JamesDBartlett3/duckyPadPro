#!/usr/bin/env python3
"""
DuckyScript Profile Generator
Author: JamesDBartlett3

This helper script generates a basic duckyPad Pro profile structure
from a template.

Usage:
    python profile_generator.py <profile-name> <number-of-keys>
    
Examples:
    python profile_generator.py discord-tools 20
    python profile_generator.py photo-editing 15
    
Note: Use descriptive names. When deploying to duckyPad Pro, users rename
    to profileN_Name format based on their preferred order.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.key_layout import TOTAL_KEYS, get_key_description

# Maximum number of keys (including rotary encoders)
MAX_KEYS = TOTAL_KEYS


def generate_profile(profile_name, num_keys, output_dir=None):
    """
    Generate a duckyPad Pro profile structure.
    
    Args:
        profile_name: Name of the profile (use descriptive name like 'discord-tools')
        num_keys: Number of keys to configure
        output_dir: Directory to create profile in (default: current directory)
    
    Note: Profile will be created with the provided name. Users should rename
          to profileN_Name format when deploying to duckyPad Pro SD card.
    """
    if output_dir is None:
        output_dir = os.getcwd()
    
    profile_path = os.path.join(output_dir, profile_name)
    
    # Create profile directory
    os.makedirs(profile_path, exist_ok=True)
    
    # Create config file
    config_content = f"""BG_COLOR 100 100 200
DIM_UNUSED_KEYS 1
"""
    
    # Add key labels for generated keys
    for i in range(1, min(num_keys + 1, 27)):
        if i <= 20:
            config_content += f"z{i} Key{i}\n"
        elif i == 21:
            config_content += f"z{i} Vol+\n"
        elif i == 22:
            config_content += f"z{i} Vol-\n"
        elif i == 23:
            config_content += f"z{i} Mute\n"
        elif i == 24:
            config_content += f"z{i} Zoom+\n"
        elif i == 25:
            config_content += f"z{i} Zoom-\n"
        elif i == 26:
            config_content += f"z{i} Reset\n"
    config_content += "\n"
    
    with open(os.path.join(profile_path, 'config.txt'), 'w') as f:
        f.write(config_content)
    
    # Create key files
    for i in range(1, num_keys + 1):
        # Use centralized key descriptions
        key_desc = get_key_description(i)
        
        key_content = f"""REM {key_desc}
REM Description: Add your description here
REM Author: Your Name

REM Add your duckyScript commands here
"""
        with open(os.path.join(profile_path, f'key{i}.txt'), 'w') as f:
            f.write(key_content)
    
    # Create README
    readme_content = f"""# {profile_name.replace('-', ' ').title()} Profile

## Description

Add a description of what this profile does here.

## Keys

"""
    
    for i in range(1, num_keys + 1):
        readme_content += f"- **Key {i}**: Description\n"
    
    readme_content += """
## Usage

1. Copy this profile to your duckyPad Pro device
2. Select the profile from the device menu
3. Customize the key scripts as needed

## Notes

Add any additional notes or requirements here.
"""
    
    with open(os.path.join(profile_path, 'README.md'), 'w') as f:
        f.write(readme_content)
    
    print(f"Profile '{profile_name}' created successfully at {profile_path}")
    print(f"Created {num_keys} key files")


def main():
    if len(sys.argv) != 3:
        print("Usage: python profile_generator.py <profile-name> <number-of-keys>")
        print("Example: python profile_generator.py discord-tools 20")
        print("")
        print("Note: Use descriptive names. Rename to profileN_Name when deploying to device.")
        sys.exit(1)
    
    profile_name = sys.argv[1]
    
    try:
        num_keys = int(sys.argv[2])
        if num_keys < 1 or num_keys > 26:
            print("Error: Number of keys must be between 1 and 26")
            print("  Keys 1-20: Physical keys in 4x5 grid")
            print("  Keys 21-26: Rotary encoder inputs (optional)")
            sys.exit(1)
    except ValueError:
        print("Error: Number of keys must be a valid integer")
        sys.exit(1)
    
    generate_profile(profile_name, num_keys)
    print(f"Profile '{profile_name}' created successfully!")
    print(f"Rename to 'profileN_{profile_name}' when deploying to duckyPad Pro.")


if __name__ == '__main__':
    main()
