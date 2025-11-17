#!/usr/bin/env python3
"""
YAML to duckyPad Profile Converter

Converts YAML profile definitions to duckyPad Pro profile directories
with keyN.txt, keyN-release.txt, and config.txt files.

Author: JamesDBartlett3
Date: 2025-11-16
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.profile_loader import load_profile


class ProfileGenerator:
    """Generate duckyPad Pro profile files from YAML definition."""
    
    def __init__(self, loader, output_dir='.', profile_index=None, use_profile_prefix=False):
        """
        Initialize generator with loaded profile data.
        
        Args:
            loader: ProfileLoader instance with loaded YAML data
            output_dir: Base directory for profile output
            profile_index: Optional starting index for profile numbering (for GOTO_PROFILE commands)
            use_profile_prefix: If True, generate folders with profileN_ prefix
        """
        self.loader = loader
        self.output_dir = Path(output_dir)
        self.profile_name = self._sanitize_name(loader.get_profile_name())
        self.profile_index = profile_index
        self.use_profile_prefix = use_profile_prefix
        
        # Build mapping of layer_id to sanitized layer names and indices
        self.layer_names = {}
        self.layer_indices = {}
        current_index = profile_index + 1 if profile_index is not None else None
        
        for layer_id in loader.get_layers().keys():
            layer = loader.get_layer(layer_id)
            layer_name = layer.get('name', f"{self.profile_name}_{layer_id}")
            self.layer_names[layer_id] = self._sanitize_name(layer_name)
            
            # Assign indices if profile_index is set
            if current_index is not None:
                self.layer_indices[layer_id] = current_index
                current_index += 1
    
    @staticmethod
    def _sanitize_name(name):
        """
        Sanitize profile/layer names for folder names.
        Replace characters that might cause issues in filenames.
        
        Args:
            name: Original name
            
        Returns:
            Sanitized name safe for folder names
        """
        # Replace spaces and special characters with underscores
        return name.replace(' ', '_').replace('-', '_')
    
    def _get_goto_profile_ref(self, layer_id=None):
        """
        Get GOTO_PROFILE reference (numeric index or profile name).
        
        Args:
            layer_id: Layer identifier, or None for main profile
            
        Returns:
            String containing either numeric index or profile name
        """
        if self.profile_index is not None:
            # Use numeric indices
            if layer_id is None:
                return str(self.profile_index)
            else:
                return str(self.layer_indices.get(layer_id, 0))
        else:
            # Use profile names (won't compile locally but will work on device)
            if layer_id is None:
                folder_name = self._get_profile_folder_name()
                return folder_name
            else:
                folder_name = self._get_layer_folder_name(layer_id)
                return folder_name
    
    def _get_profile_folder_name(self):
        """Get the folder name for the main profile."""
        if self.use_profile_prefix and self.profile_index is not None:
            return f"profile{self.profile_index}_{self.profile_name}"
        return self.profile_name
    
    def _get_layer_folder_name(self, layer_id):
        """Get the folder name for a layer profile."""
        layer_name = self.layer_names[layer_id]
        if self.use_profile_prefix and layer_id in self.layer_indices:
            return f"profile{self.layer_indices[layer_id]}_{layer_name}"
        return layer_name
        
    def generate(self):
        """Generate all profile files."""
        print(f"Generating profile: {self.profile_name}")
        
        # Generate main profile
        main_path = self._generate_main_profile()
        
        # Generate layer profiles
        for layer_id in self.loader.get_layers().keys():
            self._generate_layer_profile(layer_id)
        
        print(f"\n✓ Profile generation complete!")
        return main_path
    
    def _generate_main_profile(self):
        """Generate main profile directory and files."""
        profile_folder = self._get_profile_folder_name()
        profile_path = self.output_dir / profile_folder
        profile_path.mkdir(parents=True, exist_ok=True)
        
        print(f"\nMain profile: {profile_path}")
        
        # Generate keys
        keys = self.loader.get_keys()
        for key_num, key_def in sorted(keys.items()):
            self._generate_key_files(profile_path, key_num, key_def, is_main=True)
        
        # Generate config.txt
        self._generate_config(profile_path, self.loader.get_config(), keys)
        
        return profile_path
    
    def _generate_layer_profile(self, layer_id):
        """Generate layer profile directory and files."""
        layer = self.loader.get_layer(layer_id)
        layer_folder = self._get_layer_folder_name(layer_id)
        layer_path = self.output_dir / layer_folder
        layer_path.mkdir(parents=True, exist_ok=True)
        
        print(f"\nLayer profile: {layer_path}")
        
        # Get layer keys
        keys = self.loader.get_layer_keys(layer_id)
        
        # Find switcher keys from main profile
        main_keys = self.loader.get_keys()
        switcher_keys = []
        layer_type = 'modifier_hold'  # Default
        for key_num, key_def in main_keys.items():
            if isinstance(key_def, dict):
                # Check if this key switches to this layer
                if key_def.get('layer') == layer_id:
                    switcher_keys.append((key_num, key_def))
                    layer_type = key_def.get('layer_type', 'modifier_hold')
        
        # Generate return switcher keys
        for key_num, key_def in switcher_keys:
            self._generate_return_switcher(layer_path, key_num, key_def)
        
        # Generate layer keys
        for key_num, key_def in sorted(keys.items()):
            # Skip switcher keys (keys with 'layer' field that switch to any layer)
            is_switcher = isinstance(key_def, dict) and 'layer' in key_def
            if not is_switcher and key_num not in [k for k, _ in switcher_keys]:
                self._generate_key_files(layer_path, key_num, key_def, is_main=False, layer_type=layer_type)
        
        # Generate config.txt
        layer_config = layer.get('config', {})
        # Merge with layer-level config
        if 'background_color' in layer:
            layer_config['background_color'] = layer['background_color']
        if 'dim_unused' in layer:
            layer_config['dim_unused'] = layer['dim_unused']
        
        # Merge keys: Start with switcher keys, then override with layer keys
        layer_keys_for_config = {}
        for key_num, key_def in switcher_keys:
            layer_keys_for_config[key_num] = key_def
        # Layer keys override switcher keys
        for key_num, key_def in keys.items():
            layer_keys_for_config[key_num] = key_def
        
        self._generate_config(layer_path, layer_config, layer_keys_for_config)
    
    def _generate_key_files(self, profile_path, key_num, key_def, is_main=True, layer_type='modifier_hold'):
        """
        Generate keyN.txt and optionally keyN-release.txt for a key.
        
        Args:
            profile_path: Path to profile directory
            key_num: Key number (1-26)
            key_def: Key definition dict
            is_main: Whether this is main profile or layer
            layer_type: Type of layer (for oneshot auto-return behavior)
        """
        # Handle different key definition types
        if not isinstance(key_def, dict):
            return
        
        # Check if this is a layer switcher
        if 'layer' in key_def and is_main:
            # This is a layer switcher
            self._generate_switcher_files(profile_path, key_num, key_def)
        elif 'key' in key_def:
            # Simple key press
            self._generate_simple_key(profile_path, key_num, key_def, layer_type=layer_type)
        elif 'action' in key_def:
            # Special action (media, etc.)
            self._generate_action_key(profile_path, key_num, key_def, layer_type=layer_type)
        elif 'label' in key_def or 'color' in key_def:
            # Label-only key (no action) - create empty file
            self._generate_empty_key(profile_path, key_num, key_def)
    
    def _generate_switcher_files(self, profile_path, key_num, key_def):
        """Generate layer switcher key files based on layer_type."""
        layer_id = key_def['layer']
        layer_type = key_def.get('layer_type', 'modifier_hold')
        
        # Generate different switcher types based on layer_type
        if layer_type == 'modifier_hold':
            self._generate_modifier_hold_switcher(profile_path, key_num, key_def, layer_id)
        elif layer_type == 'toggle':
            self._generate_toggle_switcher(profile_path, key_num, key_def, layer_id)
        elif layer_type == 'oneshot':
            self._generate_oneshot_switcher(profile_path, key_num, key_def, layer_id)
        elif layer_type == 'hold_toggle':
            self._generate_hold_toggle_switcher(profile_path, key_num, key_def, layer_id)
        elif layer_type == 'momentary':
            self._generate_momentary_switcher(profile_path, key_num, key_def, layer_id)
        else:
            print(f"  ! Warning: Unknown layer_type '{layer_type}' for key {key_num}, using modifier_hold")
            self._generate_modifier_hold_switcher(profile_path, key_num, key_def, layer_id)
    
    def _generate_modifier_hold_switcher(self, profile_path, key_num, key_def, layer_id):
        """Generate modifier_hold type switcher (hold modifier while layer is active)."""
        modifier = key_def.get('modifier', 'CTRL')
        layer_ref = self._get_goto_profile_ref(layer_id)
        layer_name = self.layer_names[layer_id]
        
        # Press: Hold modifier and switch to layer
        press_file = profile_path / f"key{key_num}.txt"
        press_content = f"DEFAULTDELAY 0\nKEYDOWN {modifier}\nGOTO_PROFILE {layer_ref}\n"
        press_file.write_text(press_content)
        
        # Release: Release modifier (return happens in layer)
        release_file = profile_path / f"key{key_num}-release.txt"
        release_content = f"DEFAULTDELAY 0\nKEYUP {modifier}\n"
        release_file.write_text(release_content)
        
        print(f"  ✓ Key {key_num} (modifier_hold → {layer_name})")
    
    def _generate_toggle_switcher(self, profile_path, key_num, key_def, layer_id):
        """Generate toggle type switcher (press to switch, press again to return)."""
        layer_ref = self._get_goto_profile_ref(layer_id)
        layer_name = self.layer_names[layer_id]
        
        # Press: Switch to layer
        press_file = profile_path / f"key{key_num}.txt"
        press_content = f"DEFAULTDELAY 0\nGOTO_PROFILE {layer_ref}\n"
        press_file.write_text(press_content)
        
        print(f"  ✓ Key {key_num} (toggle → {layer_name})")
    
    def _generate_oneshot_switcher(self, profile_path, key_num, key_def, layer_id):
        """Generate oneshot type switcher (switch for one key press, then return)."""
        layer_ref = self._get_goto_profile_ref(layer_id)
        layer_name = self.layer_names[layer_id]
        
        # Press: Switch to layer (layer will return after one key press)
        press_file = profile_path / f"key{key_num}.txt"
        press_content = f"DEFAULTDELAY 0\nGOTO_PROFILE {layer_ref}\n"
        press_file.write_text(press_content)
        
        print(f"  ✓ Key {key_num} (oneshot → {layer_name})")
    
    def _generate_hold_toggle_switcher(self, profile_path, key_num, key_def, layer_id):
        """Generate hold_toggle type switcher (tap to toggle, hold to momentary)."""
        layer_ref = self._get_goto_profile_ref(layer_id)
        layer_name = self.layer_names[layer_id]
        
        # Note: This requires more complex logic that duckyScript may not support natively
        # For now, implement as simple toggle with a note
        press_file = profile_path / f"key{key_num}.txt"
        press_content = f"DEFAULTDELAY 0\nREM hold_toggle not fully implemented yet\nGOTO_PROFILE {layer_ref}\n"
        press_file.write_text(press_content)
        
        print(f"  ✓ Key {key_num} (hold_toggle → {layer_name}) [simplified as toggle]")
    
    def _generate_momentary_switcher(self, profile_path, key_num, key_def, layer_id):
        """Generate momentary type switcher (hold to activate, release to return)."""
        layer_ref = self._get_goto_profile_ref(layer_id)
        main_ref = self._get_goto_profile_ref(None)
        layer_name = self.layer_names[layer_id]
        
        # Press: Switch to layer
        press_file = profile_path / f"key{key_num}.txt"
        press_content = f"DEFAULTDELAY 0\nGOTO_PROFILE {layer_ref}\n"
        press_file.write_text(press_content)
        
        # Release: Return to main
        release_file = profile_path / f"key{key_num}-release.txt"
        release_content = f"DEFAULTDELAY 0\nGOTO_PROFILE {main_ref}\n"
        release_file.write_text(release_content)
        
        print(f"  ✓ Key {key_num} (momentary → {layer_name})")
    
    def _generate_return_switcher(self, layer_path, key_num, key_def):
        """Generate return switcher in layer profile based on layer_type."""
        layer_type = key_def.get('layer_type', 'modifier_hold')
        
        if layer_type == 'modifier_hold':
            self._generate_modifier_hold_return(layer_path, key_num, key_def)
        elif layer_type == 'toggle':
            self._generate_toggle_return(layer_path, key_num, key_def)
        elif layer_type == 'oneshot':
            # Oneshot doesn't need a return switcher - it returns automatically
            pass
        elif layer_type == 'momentary':
            # Momentary return is handled in main profile release
            pass
        elif layer_type == 'hold_toggle':
            self._generate_toggle_return(layer_path, key_num, key_def)
        else:
            self._generate_modifier_hold_return(layer_path, key_num, key_def)
    
    def _generate_modifier_hold_return(self, layer_path, key_num, key_def):
        """Generate modifier_hold return switcher in layer."""
        modifier = key_def.get('modifier', 'CTRL')
        main_ref = self._get_goto_profile_ref(None)
        
        # Press: Keep modifier held
        press_file = layer_path / f"key{key_num}.txt"
        press_content = f"DEFAULTDELAY 0\nKEYDOWN {modifier}\n"
        press_file.write_text(press_content)
        
        # Release: Release modifier and return to main
        release_file = layer_path / f"key{key_num}-release.txt"
        release_content = f"DEFAULTDELAY 0\nKEYUP {modifier}\nGOTO_PROFILE {main_ref}\n"
        release_file.write_text(release_content)
        
        print(f"  ✓ Key {key_num} (return switcher)")
    
    def _generate_toggle_return(self, layer_path, key_num, key_def):
        """Generate toggle return switcher in layer."""
        main_ref = self._get_goto_profile_ref(None)
        
        # Press: Switch back to main
        press_file = layer_path / f"key{key_num}.txt"
        press_content = f"DEFAULTDELAY 0\nGOTO_PROFILE {main_ref}\n"
        press_file.write_text(press_content)
        
        print(f"  ✓ Key {key_num} (toggle return switcher)")
    
    def _generate_simple_key(self, profile_path, key_num, key_def, layer_type='modifier_hold'):
        """Generate simple key press file."""
        key_name = key_def['key']
        hold = key_def.get('hold', False)
        main_ref = self._get_goto_profile_ref(None)
        
        if hold:
            # Generate press file with KEYDOWN
            press_file = profile_path / f"key{key_num}.txt"
            press_content = f"DEFAULTDELAY 0\nKEYDOWN {key_name}\n"
            
            # For oneshot layers, auto-return after key press
            if layer_type == 'oneshot':
                press_content += f"GOTO_PROFILE {main_ref}\n"
            
            press_file.write_text(press_content)
            
            # Generate release file with KEYUP
            release_file = profile_path / f"key{key_num}-release.txt"
            release_content = f"DEFAULTDELAY 0\nKEYUP {key_name}\n"
            release_file.write_text(release_content)
        else:
            # Generate normal press file
            press_file = profile_path / f"key{key_num}.txt"
            # Single character keys need KEYDOWN/KEYUP like held keys
            if len(key_name) == 1:
                press_content = f"DEFAULTDELAY 0\nKEYDOWN {key_name}\n"
                
                # For oneshot layers, auto-return after key press
                if layer_type == 'oneshot':
                    press_content += f"GOTO_PROFILE {main_ref}\n"
                
                press_file.write_text(press_content)
                
                # Generate release file with KEYUP
                release_file = profile_path / f"key{key_num}-release.txt"
                release_content = f"DEFAULTDELAY 0\nKEYUP {key_name}\n"
                release_file.write_text(release_content)
            else:
                press_content = f"DEFAULTDELAY 0\n{key_name}\n"
            
            # For oneshot layers, auto-return after key press
            if layer_type == 'oneshot':
                press_content += f"GOTO_PROFILE {main_ref}\n"
            
            press_file.write_text(press_content)
        
        print(f"  ✓ Key {key_num} ({key_name})")
    
    def _generate_action_key(self, profile_path, key_num, key_def, layer_type='modifier_hold'):
        """Generate special action key file."""
        action = key_def['action']
        main_ref = self._get_goto_profile_ref(None)
        
        if action == 'media':
            command = key_def.get('command', '')
            press_file = profile_path / f"key{key_num}.txt"
            press_content = f"DEFAULTDELAY 0\nMEDIA_{command}\n"
            
            # For oneshot layers, auto-return after action
            if layer_type == 'oneshot':
                press_content += f"GOTO_PROFILE {main_ref}\n"
            
            press_file.write_text(press_content)
            print(f"  ✓ Key {key_num} (MEDIA_{command})")
    
    def _generate_empty_key(self, profile_path, key_num, key_def):
        """Generate empty key file (label/color only, no action)."""
        # Create empty key file
        key_file = profile_path / f"key{key_num}.txt"
        key_file.write_text("")
        
        label = key_def.get('label', [''])[0] if 'label' in key_def else 'empty'
        print(f"  ✓ Key {key_num} ({label} - label only)")
    
    def _generate_config(self, profile_path, config, keys_dict=None):
        """Generate config.txt file.
        
        Args:
            profile_path: Path to profile directory
            config: Profile configuration dict
            keys_dict: Optional dict of keys to include in config. If None, uses main profile keys.
        """
        config_file = profile_path / "config.txt"
        
        lines = []
        
        # Background color
        if 'background_color' in config:
            bg = config['background_color']
            lines.append(f"BG_COLOR {bg[0]} {bg[1]} {bg[2]}")
        
        # Dim unused keys
        if config.get('dim_unused'):
            lines.append("DIM_UNUSED_KEYS 1")
        
        # Orientation
        if config.get('orientation') == 'landscape':
            lines.append("IS_LANDSCAPE 1")
        
        # Get keys to add labels (use provided keys or main profile keys)
        if keys_dict is None:
            keys_dict = self.loader.get_keys()
        
        for key_num in sorted(keys_dict.keys()):
            key_def = keys_dict[key_num]
            if isinstance(key_def, dict) and 'label' in key_def:
                label = key_def['label']
                if isinstance(label, list):
                    if len(label) >= 1:
                        lines.append(f"z{key_num} {label[0]}")
                    if len(label) >= 2:
                        lines.append(f"x{key_num} {label[1]}")
                else:
                    lines.append(f"z{key_num} {label}")
            
            # Add no_repeat directive
            if isinstance(key_def, dict) and key_def.get('no_repeat'):
                lines.append(f"dr {key_num}")
            
            # Add allow_abort directive
            if isinstance(key_def, dict) and key_def.get('allow_abort'):
                lines.append(f"ab {key_num}")
            
            # Add color
            if isinstance(key_def, dict) and 'color' in key_def:
                color = key_def['color']
                if isinstance(color, str):
                    # Named color - convert to RGB
                    color_map = {
                        'red': [255, 0, 0],
                        'green': [0, 255, 0],
                        'blue': [0, 0, 255],
                        'yellow': [255, 255, 0],
                        'orange': [255, 128, 0],
                        'purple': [128, 0, 255],
                        'cyan': [0, 255, 255],
                        'white': [255, 255, 255],
                    }
                    color = color_map.get(color.lower(), [255, 255, 255])
                
                lines.append(f"SWCOLOR_{key_num} {color[0]} {color[1]} {color[2]}")
        
        if lines:
            config_file.write_text('\n'.join(lines) + '\n')
            print(f"  ✓ config.txt")


def main():
    parser = argparse.ArgumentParser(
        description="Convert YAML profile definition to duckyPad Pro profile files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate profile from YAML
  python yaml_to_profile.py foxhole.yaml
  
  # Specify output directory
  python yaml_to_profile.py foxhole.yaml --output profiles/
  
  # Dry run - show what would be generated
  python yaml_to_profile.py foxhole.yaml --dry-run
        """
    )
    
    parser.add_argument(
        'yaml_file',
        help='YAML profile definition file'
    )
    
    parser.add_argument(
        '--output',
        '-o',
        default='.',
        help='Output directory for generated profiles (default: current directory)'
    )
    
    parser.add_argument(
        '--profile-index',
        '-i',
        type=int,
        help='Starting profile index for GOTO_PROFILE commands (e.g., 0 for profile1)'
    )
    
    parser.add_argument(
        '--use-profile-prefix',
        '-p',
        action='store_true',
        help='Generate folders with profileN_ prefix for device deployment'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be generated without creating files'
    )
    
    args = parser.parse_args()
    
    # Load YAML profile
    try:
        loader = load_profile(args.yaml_file)
    except Exception as e:
        print(f"Error loading YAML file: {e}", file=sys.stderr)
        return 1
    
    # Generate profile
    if args.dry_run:
        print("DRY RUN - No files will be created")
        print(f"Would generate profile: {loader.get_profile_name()}")
        print(f"Keys: {len(loader.get_keys())}")
        print(f"Layers: {len(loader.get_layers())}")
        if args.profile_index is not None:
            print(f"Profile index: {args.profile_index} (will use numeric GOTO_PROFILE)")
        else:
            print("No profile index (will use profile names in GOTO_PROFILE - won't compile locally)")
        return 0
    
    try:
        generator = ProfileGenerator(
            loader, 
            args.output, 
            profile_index=args.profile_index,
            use_profile_prefix=args.use_profile_prefix
        )
        generator.generate()
        
        # Show helpful message about compilation
        if args.profile_index is not None:
            print(f"\n✓ Generated with numeric GOTO_PROFILE indices (starting at {args.profile_index})")
            print("  Files should compile locally with make_bytecode.py")
        else:
            print("\n⚠ Generated with profile name references in GOTO_PROFILE")
            print("  Files will NOT compile locally but will work on device")
            print("  Use --profile-index to generate compilable files")
        
        return 0
    except Exception as e:
        print(f"Error generating profile: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
