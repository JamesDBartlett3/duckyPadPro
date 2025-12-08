#!/usr/bin/env python3
"""
Generate duckyPad Pro Profile from YAML Template

Converts YAML profile definitions (with templates, inheritance, and layers)
into duckyScript profiles ready for compilation and deployment.

This is the ONLY script that should read YAML template files.

Author: JamesDBartlett3
Date: 2025-11-22
"""

import argparse
import sys
import traceback
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from shared.yaml_loader import ProfileLoader
from shared.key_layout import TOTAL_KEYS
from shared.console import print_color, print_verbose
from shared.colors import parse_color, format_rgb
from shared.validators import (
    ValidationError,
    validate_profile_name,
    validate_key_label,
    require_valid_profile_name,
    require_valid_key_label,
)


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
            # Default: workbench/profiles/<profile-name> (validated)
            validated_name = self._validate_folder_name(profile_name)
            self.output_dir = Path(__file__).parent.parent / "workbench" / "profiles" / validated_name
        
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
            
            # Validate layer name for folder
            validated_layer_name = self._validate_folder_name(layer_name)
            layer_output_dir = Path(__file__).parent.parent / "workbench" / "profiles" / validated_layer_name
            
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
                # Release scripts needed for: layer switchers, single characters (alone), modifier keys (alone)
                # NOT needed for: modifier+key combos, special keys (ESC, F1, etc.), type: string
                layer_type = key_def.get('layer_type')
                key_val = key_def.get('key')
                key = str(key_val) if key_val is not None else ''  # Convert to string (YAML may parse numbers as int)
                key_type = key_def.get('type', '').lower()
                has_modifier_combo = key_def.get('modifier')  # Key combo like CTRL+A
                modifier_keys = {'SHIFT', 'CTRL', 'ALT', 'COMMAND', 'WINDOWS', 'OPTION',
                                 'RSHIFT', 'RCTRL', 'RALT', 'RCOMMAND', 'RWINDOWS', 'ROPTION'}
                is_single_char = len(key) == 1
                is_modifier_only = key.upper() in modifier_keys
                is_string_type = key_type == 'string'
                
                needs_release = (
                    layer_type in ['modifier_hold', 'momentary'] or
                    (not has_modifier_combo and not is_string_type and (is_single_char or is_modifier_only))
                )
                if needs_release:
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
        
        # Process each key for labels, colors, and flags FIRST
        # (This must come before IS_LANDSCAPE for proper firmware parsing)
        for key_num in range(1, TOTAL_KEYS + 1):
            if key_num not in keys:
                continue
            
            key_def = keys[key_num]
            
            # Key labels (z1/x1 for line 1/2)
            label = key_def.get('label', [])
            if isinstance(label, str):
                label = [label]
            
            # Convert label elements to strings (YAML may parse numbers as int)
            if len(label) >= 1 and label[0]:
                z_line = str(label[0])
            else:
                z_line = ""
            
            if len(label) >= 2 and label[1]:
                x_line = str(label[1])
            else:
                x_line = ""
            
            # Validate label against orientation limits
            if z_line or x_line:
                orientation = config.get('orientation', 'portrait')
                try:
                    require_valid_key_label(z_line, x_line, orientation, key_num)
                except ValidationError as e:
                    raise ValidationError(
                        f"{e}\n"
                        f"Label: ['{z_line}', '{x_line}']\n"
                        f"Please shorten the label in your YAML file."
                    )
            
            if z_line:
                lines.append(f'z{key_num} {z_line}')
            if x_line:
                lines.append(f'x{key_num} {x_line}')
            
            # Don't repeat flag (dr) - must come after label
            no_repeat = key_def.get('no_repeat', False)
            if no_repeat:
                lines.append(f'dr {key_num}')
        
        # Background color - supports color names (e.g., "red") or RGB arrays [255, 0, 0]
        bg_color_raw = config.get('background_color', config.get('bg_color'))
        if bg_color_raw:
            bg_color = parse_color(bg_color_raw)
            if bg_color:
                lines.append(f'BG_COLOR {format_rgb(bg_color)}')
        
        # Orientation - MUST come after key labels
        orientation = config.get('orientation', 'portrait')
        if orientation == 'landscape':
            lines.append('IS_LANDSCAPE 1')
        
        # Key colors (SWCOLOR_N) - supports color names or RGB arrays
        for key_num in range(1, TOTAL_KEYS + 1):
            if key_num not in keys:
                continue
            
            key_def = keys[key_num]
            color_raw = key_def.get('color')
            if color_raw:
                color = parse_color(color_raw)
                if color:
                    lines.append(f'SWCOLOR_{key_num} {format_rgb(color)}')
        
        # Dim unused keys
        dim_unused = config.get('dim_unused', config.get('dim_unused_keys'))
        if dim_unused:
            lines.append('DIM_UNUSED_KEYS 1')
        
        # Keydown color - supports color names or RGB arrays
        keydown_color_raw = config.get('keydown_color')
        if keydown_color_raw:
            keydown_color = parse_color(keydown_color_raw)
            if keydown_color:
                lines.append(f'KEYDOWN_COLOR {format_rgb(keydown_color)}')
        
        # Allow abort flags (ab)
        for key_num in range(1, TOTAL_KEYS + 1):
            if key_num not in keys:
                continue
            
            key_def = keys[key_num]
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
        
        # Check if we're on a oneshot layer (need to determine parent layer type)
        is_oneshot_layer = False
        if self.current_profile_type == 'layer' and self.current_layer_id:
            # Check parent keys to see if this layer is accessed via oneshot
            parent_keys = self.loader.get_keys()
            for parent_key_def in parent_keys.values():
                parent_layer = parent_key_def.get('layer')
                parent_layer_type = parent_key_def.get('layer_type')
                if parent_layer == self.current_layer_id and parent_layer_type == 'oneshot':
                    is_oneshot_layer = True
                    break
        
        if layer_type:
            # Layer switcher key
            self._generate_layer_switcher(lines, key_def, is_release)
        elif action == 'media':
            # Media command
            command = key_def.get('command', 'MUTE')
            lines.append(command)
            # If on oneshot layer, return to parent after media action
            if is_oneshot_layer and not is_release:
                lines.append(f'GOTO_PROFILE {self._get_parent_profile_name()}')
        elif action == 'custom' or key_def.get('script'):
            # Custom script - either explicit action: custom or just script: property
            script = key_def.get('script', '')
            if script and not is_release:
                # Support array of lines or single string
                if isinstance(script, list):
                    lines.extend(script)
                else:
                    lines.append(script)
                # If on oneshot layer, return to parent after custom script
                if is_oneshot_layer:
                    lines.append(f'GOTO_PROFILE {self._get_parent_profile_name()}')
            elif not script and not is_release:
                lines.append('REM Empty script')
        else:
            # Regular key press
            self._generate_key_press(lines, key_def, is_release)
            # If on oneshot layer, return to parent after key press
            if is_oneshot_layer and not is_release:
                lines.append(f'GOTO_PROFILE {self._get_parent_profile_name()}')
        
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
        
        # Check if this key switches to the CURRENT layer we're generating
        # If so, it should return to parent. If not, it should go to its target layer.
        is_current_layer = (on_layer and layer_id == self.current_layer_id)
        
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
                else:
                    # Release on main profile: just release the modifier
                    # (don't switch profiles, we're already on main)
                    if modifier:
                        lines.append(f'KEYUP {modifier.upper()}')
        
        elif layer_type == 'toggle':
            # Toggle: press to switch, press again to return
            lines.append('DEFAULTDELAY 0')
            
            if not is_release:
                if is_current_layer:
                    # On this key's layer: return to main
                    lines.append(f'GOTO_PROFILE {parent_name}')
                else:
                    # On main or different layer: go to this key's layer
                    lines.append(f'GOTO_PROFILE {layer_name}')
        
        elif layer_type == 'oneshot':
            # Oneshot: switch for one key press, auto-return
            # Note: True oneshot requires state tracking - this is a simplified version
            lines.append('DEFAULTDELAY 0')
            
            if not is_release:
                if is_current_layer:
                    # On this key's layer: return to main
                    lines.append(f'GOTO_PROFILE {parent_name}')
                else:
                    # On main or different layer: go to this key's layer
                    lines.append(f'REM Oneshot layer')
                    lines.append(f'GOTO_PROFILE {layer_name}')
        
        elif layer_type == 'momentary':
            # Momentary: hold to activate, release to return
            lines.append('DEFAULTDELAY 0')
            
            if is_current_layer:
                # On this key's layer
                if is_release:
                    # Release: return to main
                    lines.append(f'GOTO_PROFILE {parent_name}')
                # Press: do nothing (stay on layer)
            else:
                # On main or different layer
                if not is_release:
                    # Press: switch to this key's layer
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
    
    def _generate_key_press(self, lines: List[str], key_def: Dict[str, Any], is_release: bool = False):
        """
        Generate duckyScript for regular key press.
        
        Args:
            lines: List to append script lines to
            key_def: Key definition dict
            is_release: True if generating release script
        """
        # Check for string: property - types the value as text
        string_val = key_def.get('string')
        if string_val is not None:
            if not is_release:
                lines.append(f'STRING {string_val}')
            # No release script needed for STRING
            return
        
        key = key_def.get('key')
        if not key:
            # Empty action (label-only key)
            lines.append('REM Empty action - display only')
            return
        
        # Convert to string (YAML may parse numbers as int)
        key = str(key)
        
        # Handle key combinations (e.g., CTRL a for Ctrl+A)
        modifier = key_def.get('modifier')
        if modifier:
            lines.append(f'{modifier.upper()} {key.lower()}')
            return
        
        # Modifier keys that need KEYDOWN/KEYUP
        modifier_keys = {'SHIFT', 'CTRL', 'ALT', 'COMMAND', 'WINDOWS', 'OPTION',
                         'RSHIFT', 'RCTRL', 'RALT', 'RCOMMAND', 'RWINDOWS', 'ROPTION'}
        
        # Special keys that are valid duckyScript commands (single press, no release needed)
        special_keys = {
            'ESC', 'ESCAPE', 'ENTER', 'RETURN', 'TAB', 'SPACE', 'BACKSPACE', 'DELETE',
            'INSERT', 'HOME', 'END', 'PAGEUP', 'PAGEDOWN', 'PAUSE', 'BREAK',
            'UP', 'DOWN', 'LEFT', 'RIGHT', 'UPARROW', 'DOWNARROW', 'LEFTARROW', 'RIGHTARROW',
            'CAPSLOCK', 'NUMLOCK', 'SCROLLLOCK', 'PRINTSCREEN', 'MENU', 'APP', 'POWER',
            'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
            'F13', 'F14', 'F15', 'F16', 'F17', 'F18', 'F19', 'F20', 'F21', 'F22', 'F23', 'F24',
            # Numpad keys
            'KP_SLASH', 'KP_ASTERISK', 'KP_MINUS', 'KP_PLUS', 'KP_ENTER', 'KP_DOT', 'KP_EQUAL',
            'KP_0', 'KP_1', 'KP_2', 'KP_3', 'KP_4', 'KP_5', 'KP_6', 'KP_7', 'KP_8', 'KP_9',
        }
        
        is_single_char = len(key) == 1
        is_modifier = key.upper() in modifier_keys
        is_special = key.upper() in special_keys
        
        if is_single_char or is_modifier:
            # Single characters (letters, digits, symbols) and modifiers need KEYDOWN/KEYUP
            if is_release:
                lines.append(f'KEYUP {key.upper() if is_modifier else key}')
            else:
                lines.append(f'KEYDOWN {key.upper() if is_modifier else key}')
        elif is_special:
            # Special keys are valid duckyScript commands - single press
            if not is_release:
                lines.append(key.upper())
            # No release script needed for special keys
        else:
            # Multi-character strings - type as string
            if not is_release:
                lines.append(f'STRING {key}')
            # No release script needed for STRING
    
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
    
    def _validate_folder_name(self, name: str) -> str:
        """
        Validate profile name for use as folder name.
        Profile names must:
        1. Not exceed 14 characters (duckyPad Pro limit)
        2. Not contain invalid filesystem characters
        
        Args:
            name: Profile name
            
        Returns:
            Profile name unchanged if valid
            
        Raises:
            ValidationError: If profile name exceeds duckyPad Pro limit
            ValueError: If profile name contains invalid filesystem characters
        """
        # First check duckyPad Pro limit (14 chars)
        try:
            require_valid_profile_name(name, context=f"profile '{name}'")
        except ValidationError as e:
            raise ValidationError(
                f"{e}\n"
                f"Please shorten the profile name in your YAML file."
            )
        
        # Then check filesystem characters
        # Windows/Linux/macOS invalid chars: < > : " / \ | ? *
        invalid_chars = '<>:"/\\|?*'
        found_invalid = [c for c in name if c in invalid_chars]
        
        if found_invalid:
            raise ValueError(
                f"Profile name '{name}' contains invalid filesystem characters: {', '.join(repr(c) for c in found_invalid)}\n"
                f"Please rename the profile in your YAML file to remove these characters."
            )
        
        return name


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate duckyPad Pro profile from YAML template',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate profile from YAML
  python generate.py workbench/foxhole.yaml
  
  # Specify output directory
  python generate.py workbench/test_profile.yaml -o workbench/profiles/my-test
  
  # Verbose output
  python generate.py workbench/foxhole.yaml -v
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
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()


