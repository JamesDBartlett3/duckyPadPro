#!/usr/bin/env python3
"""
Profile Loader for YAML-based duckyPad Pro Profile Definitions

Loads profile definitions from YAML files and converts them to
duckyScript files and config.txt for deployment.

Author: duckyPad Pro Community
Date: 2025-11-16
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Union


class ProfileLoader:
    """Load and parse YAML profile definitions."""
    
    def __init__(self, yaml_path: Union[str, Path]):
        """
        Initialize loader with YAML file path.
        
        Args:
            yaml_path: Path to YAML profile definition file
        """
        self.yaml_path = Path(yaml_path)
        self.data = None
        self.profile = None
        self.templates = {}
        self.template_cache = {}  # Cache loaded template files
        
    def load(self) -> Dict[str, Any]:
        """
        Load YAML file and parse profile definition.
        
        Returns:
            Parsed profile data
        """
        with open(self.yaml_path, 'r', encoding='utf-8') as f:
            self.data = yaml.safe_load(f)
        
        # Extract templates if present
        if 'templates' in self.data:
            self.templates = self.data['templates']
        
        # Extract profile definition
        if 'profile' in self.data:
            self.profile = self.data['profile']
        else:
            raise ValueError("YAML file must contain 'profile' key")
        
        # Load external templates
        self._load_external_templates()
        
        # Apply templates to profile
        self._apply_templates()
        
        # Process layer inheritance
        self._process_layer_inheritance()
        
        return self.profile
    
    def get_profile_name(self) -> str:
        """Get the profile name."""
        return self.profile.get('name', 'Unnamed')
    
    def get_config(self) -> Dict[str, Any]:
        """Get profile configuration (orientation, colors, etc.)."""
        return self.profile.get('config', {})
    
    def get_keys(self) -> Dict[int, Any]:
        """
        Get all key definitions, expanding ranges and applying templates.
        
        Returns:
            Dictionary mapping key number to key definition
        """
        keys_raw = self.profile.get('keys', {})
        keys_expanded = {}
        
        # Apply extends (template inheritance)
        extends = self.profile.get('extends', [])
        for template_name in extends:
            if template_name in self.templates:
                template_keys = self.templates[template_name]
                keys_expanded.update(template_keys)
        
        # Process each key definition
        for key_spec, definition in keys_raw.items():
            expanded = self._expand_key_spec(key_spec, definition)
            keys_expanded.update(expanded)
        
        return keys_expanded
    
    def get_layers(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all layer definitions.
        
        Returns:
            Dictionary mapping layer ID to layer definition
        """
        return self.profile.get('layers', {})
    
    def get_layer(self, layer_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific layer definition."""
        layers = self.get_layers()
        return layers.get(layer_id)
    
    def get_layer_keys(self, layer_id: str) -> Dict[int, Any]:
        """
        Get key definitions for a specific layer.
        
        Args:
            layer_id: Layer identifier
            
        Returns:
            Dictionary mapping key number to key definition
        """
        layer = self.get_layer(layer_id)
        if not layer:
            return {}
        
        keys_expanded = {}
        
        # Apply layer extends
        extends = layer.get('extends', [])
        for template_name in extends:
            if template_name in self.templates:
                template_keys = self.templates[template_name]
                keys_expanded.update(template_keys)
        
        # Process layer-specific keys
        keys_raw = layer.get('keys', {})
        for key_spec, definition in keys_raw.items():
            expanded = self._expand_key_spec(key_spec, definition)
            keys_expanded.update(expanded)
        
        return keys_expanded
    
    def _expand_key_spec(self, key_spec: Union[str, int], definition: Any) -> Dict[int, Any]:
        """
        Expand key specification into individual key definitions.
        
        Handles:
        - Single keys: 1, "1"
        - Ranges: "6-10"
        - Multiple keys: [6, 8, 10] (if needed later)
        
        Args:
            key_spec: Key specification (number or range)
            definition: Key definition (string, list, or dict)
            
        Returns:
            Dictionary mapping key numbers to definitions
        """
        result = {}
        
        # Parse key spec
        if isinstance(key_spec, int):
            keys = [key_spec]
        elif isinstance(key_spec, str):
            if '-' in key_spec:
                # Range: "6-10"
                start, end = map(int, key_spec.split('-'))
                keys = list(range(start, end + 1))
            else:
                # Single key as string
                keys = [int(key_spec)]
        else:
            raise ValueError(f"Invalid key spec: {key_spec}")
        
        # Expand definition for each key
        if isinstance(definition, list) and '-' in str(key_spec):
            # Array of values for range: "6-10": [A, E, "1", "2", "3"]
            if len(keys) != len(definition):
                raise ValueError(
                    f"Range {key_spec} has {len(keys)} keys but {len(definition)} definitions"
                )
            for key_num, key_def in zip(keys, definition):
                result[key_num] = self._normalize_key_definition(key_def)
        else:
            # Same definition for all keys (including single key with list label)
            for key_num in keys:
                result[key_num] = self._normalize_key_definition(definition)
        
        return result
    
    def _normalize_key_definition(self, definition: Any) -> Dict[str, Any]:
        """
        Normalize key definition to standard dict format.
        
        Handles:
        - String: "A" → {key: "A"}
        - List: ["A", "Label"] → {key: "A", label: ["Label"]}
        - Dict: Already normalized
        
        Args:
            definition: Key definition in any format
            
        Returns:
            Normalized dictionary
        """
        if isinstance(definition, str):
            # Simple key: "A"
            return {'key': definition}
        
        elif isinstance(definition, list):
            # [key, label1, label2] or just [label1, label2]
            if len(definition) == 0:
                return {}
            elif len(definition) == 1:
                return {'key': definition[0]}
            elif len(definition) == 2:
                return {'key': definition[0], 'label': [definition[1]]}
            elif len(definition) == 3:
                return {'key': definition[0], 'label': [definition[1], definition[2]]}
            else:
                raise ValueError(f"Invalid list definition: {definition}")
        
        elif isinstance(definition, dict):
            # Already in dict format
            return definition
        
        else:
            raise ValueError(f"Invalid key definition type: {type(definition)}")
    
    def _load_external_templates(self):
        """Load template files from profiles/templates/ directory."""
        # Get list of template names to load
        template_names = self.profile.get('templates', [])
        if not template_names:
            return
        
        # Determine templates directory
        # Look for profiles/templates/ relative to the YAML file
        templates_dir = self.yaml_path.parent.parent / 'templates'
        if not templates_dir.exists():
            # Try relative to current working directory
            templates_dir = Path('profiles/templates')
        
        if not templates_dir.exists():
            return  # No templates directory, skip
        
        # Load each template
        for template_name in template_names:
            if template_name in self.template_cache:
                continue  # Already loaded
            
            template_file = templates_dir / f"{template_name}.yaml"
            if not template_file.exists():
                print(f"Warning: Template '{template_name}' not found at {template_file}")
                continue
            
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = yaml.safe_load(f)
            
            if 'template' in template_data:
                self.template_cache[template_name] = template_data['template']
            else:
                print(f"Warning: Template file '{template_file}' missing 'template' key")
    
    def _apply_templates(self):
        """Apply templates to profile keys."""
        template_names = self.profile.get('templates', [])
        if not template_names:
            return
        
        # Ensure keys dict exists
        if 'keys' not in self.profile:
            self.profile['keys'] = {}
        
        # Apply templates in order
        for template_name in template_names:
            if template_name not in self.template_cache:
                continue
            
            template = self.template_cache[template_name]
            template_keys = template.get('keys', {})
            
            # Apply template keys (don't override existing keys)
            for key_num, key_def in template_keys.items():
                if key_num not in self.profile['keys']:
                    self.profile['keys'][key_num] = key_def
    
    def _process_layer_inheritance(self):
        """Process extends directives in layers."""
        layers = self.profile.get('layers', {})
        if not layers:
            return
        
        for layer_id, layer in layers.items():
            extends = layer.get('extends')
            if not extends:
                continue
            
            # Determine source keys
            if extends == 'parent':
                source_keys = self.profile.get('keys', {})
            elif extends in layers:
                # Extending another layer
                source_layer = layers[extends]
                source_keys = source_layer.get('keys', {})
            else:
                print(f"Warning: Layer '{layer_id}' extends unknown source '{extends}'")
                continue
            
            # Ensure layer has keys dict
            if 'keys' not in layer:
                layer['keys'] = {}
            
            # Check for label-only overrides and warn
            import copy
            for key_num in list(layer['keys'].keys()):
                override = layer['keys'][key_num]
                if isinstance(override, dict):
                    # Check if this is a label-only override (has label/color but no action)
                    has_visual_only = ('label' in override or 'color' in override)
                    has_action = any(k in override for k in ['key', 'action', 'layer', 'layer_type', 'modifier'])
                    
                    if has_visual_only and not has_action:
                        print(f"Warning: Layer '{layer_id}' key {key_num} has label/color only - ignoring incomplete override, using inherited definition")
                        # Remove the incomplete override
                        del layer['keys'][key_num]
            
            # Copy source keys (don't override existing layer keys)
            for key_num, key_def in source_keys.items():
                if key_num not in layer['keys']:
                    # Deep copy the key definition
                    layer['keys'][key_num] = copy.deepcopy(key_def)
            
            # Apply templates to layer if specified
            layer_templates = layer.get('templates', [])
            for template_name in layer_templates:
                if template_name not in self.template_cache:
                    continue
                
                template = self.template_cache[template_name]
                template_keys = template.get('keys', {})
                
                for key_num, key_def in template_keys.items():
                    if key_num not in layer['keys']:
                        import copy
                        layer['keys'][key_num] = copy.deepcopy(key_def)


def load_profile(yaml_path: Union[str, Path]) -> ProfileLoader:
    """
    Load a profile from a YAML file.
    
    Args:
        yaml_path: Path to YAML file
        
    Returns:
        ProfileLoader instance with loaded data
    """
    loader = ProfileLoader(yaml_path)
    loader.load()
    return loader


if __name__ == '__main__':
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python profile_loader.py <profile.yaml>")
        sys.exit(1)
    
    loader = load_profile(sys.argv[1])
    
    print(f"Profile: {loader.get_profile_name()}")
    print(f"Config: {loader.get_config()}")
    print(f"\nKeys:")
    for key_num, key_def in sorted(loader.get_keys().items()):
        print(f"  {key_num}: {key_def}")
    
    print(f"\nLayers:")
    for layer_id, layer_def in loader.get_layers().items():
        print(f"  {layer_id}:")
        print(f"    Name: {layer_def.get('name')}")
        print(f"    Keys: {len(loader.get_layer_keys(layer_id))}")
