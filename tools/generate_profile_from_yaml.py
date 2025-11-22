#!/usr/bin/env python3
"""
Generate duckyPad Pro Profile from YAML Template

Converts YAML profile definitions (with templates, inheritance, and layers)
into duckyScript profiles ready for compilation and deployment.

This is the ONLY script that should read YAML template files.

Author: JamesDBartlett3
Date: 2025-11-22
"""

import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from shared.profile_loader import ProfileLoader
from shared.key_layout import TOTAL_KEYS


class YAMLToProfileConverter:
    """Convert YAML profile definitions to duckyScript profiles."""
    
    def __init__(self, yaml_path: Path, output_dir: Optional[Path] = None, verbose: bool = False):
        """
        Initialize converter.
        
        Args:
            yaml_path: Path to YAML template file
            output_dir: Output directory (default: workbench/profiles/<profile-name>)
            verbose: Enable verbose output
        """
        self.yaml_path = yaml_path
        self.output_dir = output_dir
        self.verbose = verbose
        self.loader = ProfileLoader(yaml_path)
        self.current_profile_type = 'main'  # Track if generating 'main' or 'layer'
        self.current_layer_id = None  # Track which layer we're generating
        
    def convert(self) -> List[Path]:
        """
        Convert YAML to duckyScript profile(s).
        
        Returns:
            List of created profile directory paths
        """
        # Load YAML
        if self.verbose:
            print(f"Loading YAML: {self.yaml_path}")
        
        self.loader.load()
        profile_name = self.loader.get_profile_name()
        
        if self.verbose:
            print(f"Profile name: {profile_name}")
        
        # Determine output directory
        if self.output_dir is None:
            # Default: workbench/profiles/<profile-name> (sanitized)
            sanitized_name = self._sanitize_folder_name(profile_name)
            self.output_dir = Path(__file__).parent.parent / "workbench" / "profiles" / sanitized_name
        
        created_profiles = []
        
        # Generate main profile
        self.current_profile_type = 'main'
        self.current_layer_id = None
        main_profile_dir = self._generate_profile(
            profile_name,
            self.loader.get_config(),
            self.loader.get_keys(),
            self.output_dir
        )
        created_profiles.append(main_profile_dir)
        
        # Generate layer profiles
        layers = self.loader.get_layers()
        for layer_id, layer_def in layers.items():
            self.current_profile_type = 'layer'
            self.current_layer_id = layer_id
            
            layer_name = layer_def.get('name', f"{profile_name}-{layer_id}")
            layer_config = layer_def.get('config', {})
            
            # Merge main config with layer config
            merged_config = {**self.loader.get_config(), **layer_config}
            
            layer_keys = self.loader.get_layer_keys(layer_id)
            
            # Sanitize layer name for folder
            sanitized_layer_name = self._sanitize_folder_name(layer_name)
            layer_output_dir = Path(__file__).parent.parent / "workbench" / "profiles" / sanitized_layer_name
            
            layer_profile_dir = self._generate_profile(
                layer_name,
                merged_config,
                layer_keys,
                layer_output_dir
            )
            created_profiles.append(layer_profile_dir)
        
        return created_profiles
    
    def _generate_profile(
        self, 
        profile_name: str, 
        config: Dict[str, Any], 
        keys: Dict[int, Any],
        output_dir: Path
    ) -> Path:
        """
        Generate a single profile (main or layer).
        
        Args:
            profile_name: Profile name
            config: Configuration dict
            keys: Key definitions
            output_dir: Output directory
            
        Returns:
            Path to created profile directory
        """
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if self.verbose:
            print(f"\nGenerating profile: {profile_name}")
            print(f"Output directory: {output_dir}")
        
        # Generate config.txt
        config_path = output_dir / "config.txt"
        self._write_config(config_path, config, keys)
        
        if self.verbose:
            print(f"  Created: {config_path.name}")
        
        # Generate keyN.txt files
        key_count = 0
        for key_num in range(1, TOTAL_KEYS + 1):
            if key_num in keys:
                key_def = keys[key_num]
                
                # If we're on a layer and this key has no action but the parent had a layer_type,
                # we need to preserve the layer switching behavior
                if self.current_profile_type == 'layer':
                    parent_keys = self.loader.get_keys()
                    if key_num in parent_keys:
                        parent_key = parent_keys[key_num]
                        parent_layer_type = parent_key.get('layer_type')
                        
                        # If parent was a layer switcher and current key has no action
                        if parent_layer_type and not any(k in key_def for k in ['key', 'action', 'layer_type']):
                            # Merge parent's layer switching properties
                            key_def = {**parent_key, **key_def}
                
                key_path = output_dir / f"key{key_num}.txt"
                self._write_key_script(key_path, key_num, key_def, is_release=False)
                key_count += 1
                
                # Check if we need a release script
                layer_type = key_def.get('layer_type')
                if layer_type in ['modifier_hold', 'momentary']:
                    release_path = output_dir / f"key{key_num}-release.txt"
                    self._write_key_script(release_path, key_num, key_def, is_release=True)
                    
                    if self.verbose:
                        print(f"  Created: {release_path.name}")
                
                if self.verbose:
                    print(f"  Created: {key_path.name}")
        
        # Generate README.md
        readme_path = output_dir / "README.md"
        self._write_readme(readme_path, profile_name, config, keys)
        
        if self.verbose:
            print(f"  Created: {readme_path.name}")
            print(f"  Total keys: {key_count}")
        
        return output_dir
    
    def _write_config(self, path: Path, config: Dict[str, Any], keys: Dict[int, Any]):
        """
        Write config.txt file.
        
        Args:
            path: Output file path
            config: Configuration dict
            keys: Key definitions (for extracting labels/colors)
        """
        lines = []
        
        # Orientation
        orientation = config.get('orientation', 'portrait')
        if orientation == 'landscape':
            lines.append('IS_LANDSCAPE 1')
        
        # Background color
        bg_color = config.get('background_color', config.get('bg_color'))
        if bg_color:
            lines.append(f'BG_COLOR {bg_color[0]} {bg_color[1]} {bg_color[2]}')
        
        # Dim unused keys
        dim_unused = config.get('dim_unused', config.get('dim_unused_keys'))
        if dim_unused:
            lines.append('DIM_UNUSED_KEYS 1')
        
        # Keydown color
        keydown_color = config.get('keydown_color')
        if keydown_color:
            lines.append(f'KEYDOWN_COLOR {keydown_color[0]} {keydown_color[1]} {keydown_color[2]}')
        
        # Process each key for labels, colors, and flags
        for key_num in range(1, TOTAL_KEYS + 1):
            if key_num not in keys:
                continue
            
            key_def = keys[key_num]
            
            # Key labels (z1/x1 for line 1/2)
            label = key_def.get('label', [])
            if isinstance(label, str):
                label = [label]
            
            if len(label) >= 1 and label[0]:
                lines.append(f'z{key_num} {label[0][:5]}')  # Max 5 chars
            if len(label) >= 2 and label[1]:
                lines.append(f'x{key_num} {label[1][:5]}')  # Max 5 chars
            
            # Key color (SWCOLOR_N)
            color = key_def.get('color')
            if color:
                lines.append(f'SWCOLOR_{key_num} {color[0]} {color[1]} {color[2]}')
            
            # Don't repeat flag (dr)
            no_repeat = key_def.get('no_repeat', False)
            if no_repeat:
                lines.append(f'dr {key_num}')
            
            # Allow abort flag (ab)
            allow_abort = key_def.get('allow_abort', False)
            if allow_abort:
                lines.append(f'ab {key_num}')
        
        # Write file
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
            if lines:
                f.write('\n')
    
    def _write_key_script(self, path: Path, key_num: int, key_def: Dict[str, Any], is_release: bool = False):
        """
        Write keyN.txt or keyN-release.txt duckyScript file.
        
        Args:
            path: Output file path
            key_num: Key number
            key_def: Key definition dict
            is_release: True if writing release script
        """
        lines = []
        
        # Add header comment
        label = key_def.get('label', [])
        if label:
            label_text = ' - '.join(str(l) for l in label if l)
            lines.append(f'REM Key {key_num}: {label_text}')
        else:
            lines.append(f'REM Key {key_num}')
        
        # Determine action type
        action = key_def.get('action')
        layer_type = key_def.get('layer_type')
        
        if layer_type:
            # Layer switcher key
            self._generate_layer_switcher(lines, key_def, is_release)
        elif action == 'media':
            # Media command
            command = key_def.get('command', 'MUTE')
            lines.append(command)
        elif action == 'custom':
            # Custom script
            script = key_def.get('script', '')
            lines.append(script)
        else:
            # Regular key press
            self._generate_key_press(lines, key_def)
        
        # Write file
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
            if lines:
                f.write('\n')
    
    def _generate_layer_switcher(self, lines: List[str], key_def: Dict[str, Any], is_release: bool = False):
        """
        Generate duckyScript for layer switching key.
        
        Args:
            lines: List to append script lines to
            key_def: Key definition dict
            is_release: True if generating release script
        """
        layer_type = key_def.get('layer_type')
        layer_id = key_def.get('layer', 'unknown')
        modifier = key_def.get('modifier')
        
        # Get the actual layer profile name
        layer_name = self._get_layer_profile_name(layer_id)
        parent_name = self._get_parent_profile_name()
        
        # Determine if we're on the main profile or the layer profile
        on_layer = (self.current_profile_type == 'layer')
        
        if layer_type == 'modifier_hold':
            # Modifier hold: press modifier, switch layer, release modifier on return
            lines.append('DEFAULTDELAY 0')
            
            if on_layer:
                # On layer profile
                if is_release:
                    # Release: release modifier and return to main
                    if modifier:
                        lines.append(f'KEYUP {modifier.upper()}')
                    lines.append(f'GOTO_PROFILE {parent_name}')
                else:
                    # Press: just hold the modifier (already switched)
                    if modifier:
                        lines.append(f'KEYDOWN {modifier.upper()}')
            else:
                # On main profile
                if not is_release:
                    # Press: press modifier and switch to layer
                    if modifier:
                        lines.append(f'KEYDOWN {modifier.upper()}')
                    lines.append(f'GOTO_PROFILE {layer_name}')
        
        elif layer_type == 'toggle':
            # Toggle: press to switch, press again to return
            lines.append('DEFAULTDELAY 0')
            
            if not is_release:
                if on_layer:
                    # On layer: return to main
                    lines.append(f'GOTO_PROFILE {parent_name}')
                else:
                    # On main: go to layer
                    lines.append(f'GOTO_PROFILE {layer_name}')
        
        elif layer_type == 'oneshot':
            # Oneshot: switch for one key press, auto-return
            # Note: True oneshot requires state tracking - this is a simplified version
            lines.append('DEFAULTDELAY 0')
            
            if not is_release:
                if on_layer:
                    # On layer: return to main after any key press
                    lines.append(f'GOTO_PROFILE {parent_name}')
                else:
                    # On main: go to layer
                    lines.append(f'REM Oneshot layer')
                    lines.append(f'GOTO_PROFILE {layer_name}')
        
        elif layer_type == 'momentary':
            # Momentary: hold to activate, release to return
            lines.append('DEFAULTDELAY 0')
            
            if on_layer:
                # On layer profile
                if is_release:
                    # Release: return to main
                    lines.append(f'GOTO_PROFILE {parent_name}')
                # Press: do nothing (stay on layer)
            else:
                # On main profile
                if not is_release:
                    # Press: switch to layer
                    lines.append(f'GOTO_PROFILE {layer_name}')
        
        else:
            lines.append(f'REM Unknown layer type: {layer_type}')
    
    def _get_layer_profile_name(self, layer_id: str) -> str:
        """
        Get the full profile name for a layer ID.
        
        Args:
            layer_id: Layer identifier from YAML
            
        Returns:
            Full profile name
        """
        # Check if this layer exists in the loaded profile
        layers = self.loader.get_layers()
        if layer_id in layers:
            layer = layers[layer_id]
            return layer.get('name', f"{self.loader.get_profile_name()}-{layer_id}")
        return layer_id
    
    def _get_parent_profile_name(self) -> str:
        """
        Get the parent (main) profile name.
        
        Returns:
            Parent profile name
        """
        return self.loader.get_profile_name()
    
    def _generate_key_press(self, lines: List[str], key_def: Dict[str, Any]):
        """
        Generate duckyScript for regular key press.
        
        Args:
            lines: List to append script lines to
            key_def: Key definition dict
        """
        key = key_def.get('key')
        if not key:
            # Empty action (label-only key)
            lines.append('REM Empty action - display only')
            return
        
        hold = key_def.get('hold', False)
        
        if hold:
            # Hold key - use HOLD/RELEASE
            lines.append(f'REM Hold key: {key}')
            lines.append(f'HOLD {key.upper()}')
        else:
            # Regular key press
            # Handle modifiers
            modifier = key_def.get('modifier')
            if modifier:
                lines.append(f'{modifier.upper()} {key.upper()}')
            else:
                # Check if key is a single character or special key
                if len(key) == 1 and key.isalnum():
                    # Single character - use STRING
                    lines.append(f'STRING {key}')
                else:
                    # Special key name
                    lines.append(key.upper())
    
    def _write_readme(self, path: Path, profile_name: str, config: Dict[str, Any], keys: Dict[int, Any]):
        """
        Write README.md for profile.
        
        Args:
            path: Output file path
            profile_name: Profile name
            config: Configuration dict
            keys: Key definitions
        """
        lines = [
            f'# {profile_name}',
            '',
            f'Generated from YAML template: `{self.yaml_path.name}`',
            '',
            '## Configuration',
            '',
            f'- **Orientation**: {config.get("orientation", "portrait")}',
        ]
        
        bg_color = config.get('background_color', config.get('bg_color'))
        if bg_color:
            lines.append(f'- **Background Color**: RGB({bg_color[0]}, {bg_color[1]}, {bg_color[2]})')
        
        dim_unused = config.get('dim_unused', config.get('dim_unused_keys'))
        if dim_unused:
            lines.append(f'- **Dim Unused Keys**: Yes')
        
        lines.extend([
            '',
            '## Keys',
            '',
            '| Key | Label | Action |',
            '|-----|-------|--------|',
        ])
        
        # List keys
        for key_num in range(1, TOTAL_KEYS + 1):
            if key_num not in keys:
                continue
            
            key_def = keys[key_num]
            
            # Format label
            label = key_def.get('label', [])
            if isinstance(label, str):
                label = [label]
            label_text = '<br>'.join(str(l) for l in label if l) if label else '-'
            
            # Format action
            action = self._format_action_description(key_def)
            
            lines.append(f'| {key_num} | {label_text} | {action} |')
        
        lines.extend([
            '',
            '## Usage',
            '',
            '1. Compile the profile: `python tools/compile.py -p workbench/profiles/<profile-folder>`',
            '2. Deploy to SD card: `python tools/deploy.py`',
            '',
            '## Notes',
            '',
            f'This profile was automatically generated from the YAML template `{self.yaml_path.name}`.',
            'To modify this profile, edit the YAML file and regenerate.',
            '',
        ])
        
        # Write file
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    
    def _format_action_description(self, key_def: Dict[str, Any]) -> str:
        """
        Format human-readable action description.
        
        Args:
            key_def: Key definition dict
            
        Returns:
            Action description string
        """
        layer_type = key_def.get('layer_type')
        action = key_def.get('action')
        
        if layer_type:
            layer = key_def.get('layer', 'unknown')
            modifier = key_def.get('modifier')
            
            if layer_type == 'modifier_hold':
                if modifier:
                    return f'Hold {modifier}, switch to `{layer}`'
                return f'Switch to `{layer}`'
            elif layer_type == 'toggle':
                return f'Toggle `{layer}` layer'
            elif layer_type == 'oneshot':
                return f'Oneshot to `{layer}`'
            elif layer_type == 'momentary':
                return f'Momentary `{layer}`'
        
        if action == 'media':
            command = key_def.get('command', 'MUTE')
            return f'Media: {command}'
        
        if action == 'custom':
            return 'Custom script'
        
        key = key_def.get('key')
        if not key:
            return 'Display only'
        
        hold = key_def.get('hold', False)
        modifier = key_def.get('modifier')
        
        if hold:
            return f'Hold `{key}`'
        elif modifier:
            return f'`{modifier}+{key}`'
        else:
            return f'`{key}`'
    
    def _sanitize_folder_name(self, name: str) -> str:
        """
        Sanitize profile name for use as folder name.
        
        Args:
            name: Profile name
            
        Returns:
            Sanitized folder name
        """
        # Replace spaces with hyphens, convert to lowercase
        sanitized = name.lower().replace(' ', '-')
        
        # Remove invalid characters
        sanitized = ''.join(c for c in sanitized if c.isalnum() or c in '-_')
        
        return sanitized


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate duckyPad Pro profile from YAML template',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate profile from YAML
  python generate_profile_from_yaml.py workbench/foxhole.yaml
  
  # Specify output directory
  python generate_profile_from_yaml.py workbench/test_profile.yaml -o workbench/profiles/my-test
  
  # Verbose output
  python generate_profile_from_yaml.py workbench/foxhole.yaml -v
        """
    )
    
    parser.add_argument(
        'yaml_file',
        type=Path,
        help='YAML template file to convert'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output directory (default: workbench/profiles/<profile-name>)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Validate YAML file exists
    if not args.yaml_file.exists():
        print(f"Error: YAML file not found: {args.yaml_file}")
        sys.exit(1)
    
    # Convert YAML to profile
    converter = YAMLToProfileConverter(args.yaml_file, args.output, args.verbose)
    
    try:
        created_profiles = converter.convert()
        
        print(f"\n✓ Successfully generated {len(created_profiles)} profile(s):")
        for profile_dir in created_profiles:
            print(f"  • {profile_dir}")
        
    except Exception as e:
        print(f"\n✗ Error generating profile: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
