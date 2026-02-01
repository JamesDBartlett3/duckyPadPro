#!/usr/bin/env python3
"""
Tests for template inheritance in YAML profile loader.

Tests the critical "last wins" behavior where:
- Later templates override earlier templates for the same key
- Explicit profile keys always override template keys
- Similar behavior applies to layer inheritance
"""
import sys
import tempfile
import unittest
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from shared.yaml_loader import ProfileLoader


class TestTemplateInheritance(unittest.TestCase):
    """Test template inheritance and override behavior."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create templates directory
        self.templates_dir = self.temp_path / 'templates'
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test templates
        self.setup_test_templates()
    
    def setup_test_templates(self):
        """Create test template files."""
        # Template 1: Basic keys
        template1 = self.templates_dir / 'template1.yaml'
        template1.write_text("""template:
  name: template1
  keys:
    1: { key: A }
    2: { key: B }
    3: { key: C }
""")
        
        # Template 2: Overrides key 2
        template2 = self.templates_dir / 'template2.yaml'
        template2.write_text("""template:
  name: template2
  keys:
    2: { key: X }
    4: { key: D }
""")
        
        # Template 3: Media controls
        media_template = self.templates_dir / 'media_controls.yaml'
        media_template.write_text("""template:
  name: media_controls
  keys:
    21: { action: media, command: VOLUME_UP }
    22: { action: media, command: VOLUME_DOWN }
""")
        
        # Empty template
        empty_template = self.templates_dir / 'empty_template.yaml'
        empty_template.write_text("""template:
  name: empty_template
""")
    
    def test_single_template(self):
        """Test applying a single template."""
        yaml_file = self.temp_path / 'test.yaml'
        yaml_file.write_text("""profile:
  name: Test
  templates: [template1]
""")
        
        loader = ProfileLoader(yaml_file)
        loader.load()
        keys = loader.get_keys()
        
        self.assertEqual(keys[1]['key'], 'A')
        self.assertEqual(keys[2]['key'], 'B')
        self.assertEqual(keys[3]['key'], 'C')
    
    def test_last_wins_template_override(self):
        """Test that later templates override earlier templates (critical bug fix)."""
        yaml_file = self.temp_path / 'test.yaml'
        yaml_file.write_text("""profile:
  name: Test
  templates: [template1, template2]
""")
        
        loader = ProfileLoader(yaml_file)
        loader.load()
        keys = loader.get_keys()
        
        # Key 1 from template1
        self.assertEqual(keys[1]['key'], 'A')
        # Key 2 should be from template2 (X), not template1 (B) - THIS IS THE BUG FIX
        self.assertEqual(keys[2]['key'], 'X', 
                        "Later template should override earlier template (last wins)")
        # Key 3 from template1
        self.assertEqual(keys[3]['key'], 'C')
        # Key 4 from template2
        self.assertEqual(keys[4]['key'], 'D')
    
    def test_explicit_keys_override_templates(self):
        """Test that explicit profile keys override all templates."""
        yaml_file = self.temp_path / 'test.yaml'
        yaml_file.write_text("""profile:
  name: Test
  templates: [template1, template2]
  keys:
    2: { key: Z }
""")
        
        loader = ProfileLoader(yaml_file)
        loader.load()
        keys = loader.get_keys()
        
        # Key 2 should be Z from explicit profile, not X from template2 or B from template1
        self.assertEqual(keys[2]['key'], 'Z',
                        "Explicit profile keys should override all templates")
        # Other keys still from templates
        self.assertEqual(keys[1]['key'], 'A')
        self.assertEqual(keys[4]['key'], 'D')
    
    def test_three_template_override_chain(self):
        """Test override behavior with three templates."""
        # Create template3
        template3 = self.templates_dir / 'template3.yaml'
        template3.write_text("""template:
  name: template3
  keys:
    2: { key: Y }
    5: { key: E }
""")
        
        yaml_file = self.temp_path / 'test.yaml'
        yaml_file.write_text("""profile:
  name: Test
  templates: [template1, template2, template3]
""")
        
        loader = ProfileLoader(yaml_file)
        loader.load()
        keys = loader.get_keys()
        
        # Key 2 should be from template3 (Y), the last one
        self.assertEqual(keys[2]['key'], 'Y',
                        "Last template in chain should win")
        self.assertEqual(keys[1]['key'], 'A')
        self.assertEqual(keys[4]['key'], 'D')
        self.assertEqual(keys[5]['key'], 'E')
    
    def test_missing_template_warning(self):
        """Test warning is issued for missing templates."""
        yaml_file = self.temp_path / 'test.yaml'
        yaml_file.write_text("""profile:
  name: Test
  templates: [nonexistent_template]
""")
        
        # Should not raise exception, just print warning
        loader = ProfileLoader(yaml_file)
        loader.load()
        keys = loader.get_keys()
        
        # No keys should be present
        self.assertEqual(len(keys), 0)
    
    def test_empty_template(self):
        """Test that empty templates don't cause errors."""
        yaml_file = self.temp_path / 'test.yaml'
        yaml_file.write_text("""profile:
  name: Test
  templates: [empty_template]
  keys:
    1: { key: A }
""")
        
        loader = ProfileLoader(yaml_file)
        loader.load()
        keys = loader.get_keys()
        
        # Should still have the explicit key
        self.assertEqual(keys[1]['key'], 'A')
    
    def test_layer_extends_with_template_override(self):
        """Test layer inheritance with template override logic."""
        yaml_file = self.temp_path / 'test.yaml'
        yaml_file.write_text("""profile:
  name: Test
  keys:
    1: { key: A }
  layers:
    layer1:
      name: Layer 1
      templates: [template1, template2]
""")
        
        loader = ProfileLoader(yaml_file)
        loader.load()
        layer_keys = loader.get_layer_keys('layer1')
        
        # Layer should have template2's key 2 (X), not template1's (B)
        self.assertEqual(layer_keys[2]['key'], 'X',
                        "Layer templates should use last-wins logic")
    
    def test_layer_explicit_keys_override_templates(self):
        """Test that explicit layer keys override layer templates."""
        yaml_file = self.temp_path / 'test.yaml'
        yaml_file.write_text("""profile:
  name: Test
  layers:
    layer1:
      name: Layer 1
      templates: [template1, template2]
      keys:
        2: { key: Z }
""")
        
        loader = ProfileLoader(yaml_file)
        loader.load()
        layer_keys = loader.get_layer_keys('layer1')
        
        # Explicit layer key should win
        self.assertEqual(layer_keys[2]['key'], 'Z',
                        "Explicit layer keys should override templates")
        # Other keys from templates
        self.assertEqual(layer_keys[1]['key'], 'A')
    
    def test_layer_extends_parent_then_template(self):
        """Test layer extends parent, then applies templates with last-wins."""
        yaml_file = self.temp_path / 'test.yaml'
        yaml_file.write_text("""profile:
  name: Test
  keys:
    1: { key: P }
    2: { key: Q }
  layers:
    layer1:
      name: Layer 1
      extends: parent
      templates: [template2]
""")
        
        loader = ProfileLoader(yaml_file)
        loader.load()
        layer_keys = loader.get_layer_keys('layer1')
        
        # Key 1 from parent
        self.assertEqual(layer_keys[1]['key'], 'P')
        # Key 2 should be from template2 (X), overriding parent (Q)
        self.assertEqual(layer_keys[2]['key'], 'X',
                        "Layer templates should override parent keys")
        # Key 4 from template2
        self.assertEqual(layer_keys[4]['key'], 'D')
    
    def test_media_controls_template(self):
        """Test media controls template can be loaded."""
        yaml_file = self.temp_path / 'test.yaml'
        yaml_file.write_text("""profile:
  name: Test
  templates: [media_controls]
""")
        
        loader = ProfileLoader(yaml_file)
        loader.load()
        keys = loader.get_keys()
        
        # Check media keys
        self.assertEqual(keys[21]['action'], 'media')
        self.assertEqual(keys[21]['command'], 'VOLUME_UP')
        self.assertEqual(keys[22]['command'], 'VOLUME_DOWN')


if __name__ == '__main__':
    unittest.main()
