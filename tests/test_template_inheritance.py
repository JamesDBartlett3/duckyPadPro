#!/usr/bin/env python3
"""
Unit Tests for Template Inheritance

Tests that templates can be properly inherited by both main profiles
and layer profiles.

Author: GitHub Copilot
Date: 2025-11-24
"""

import sys
import tempfile
import shutil
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))

from shared.yaml_loader import ProfileLoader  # type: ignore


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


def setup_test_templates(tmp_dir: Path):
    """Create test template files"""
    templates_dir = tmp_dir / 'templates'
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    # Create media_controls template
    media_template = templates_dir / 'media_controls.yaml'
    media_template.write_text("""template:
  name: media_controls
  description: Standard media playback controls
  keys:
    21: { action: media, command: VOLUME_UP }
    22: { action: media, command: VOLUME_DOWN }
    23: { action: media, command: MUTE }
""")
    
    # Create fps_wasd template
    fps_template = templates_dir / 'fps_wasd.yaml'
    fps_template.write_text("""template:
  name: fps_wasd
  description: Standard FPS WASD movement controls
  keys:
    11: { key: W, label: [Fwd, W], hold: true }
    10: { key: S, label: [Back, S], hold: true }
    6: { key: A, label: [Left, A], hold: true }
    14: { key: D, label: [Rght, D], hold: true }
""")
    
    return templates_dir


def test_main_profile_template_inheritance():
    """Test that main profile can inherit from templates"""
    print("\n--- Main Profile Template Inheritance ---")
    
    # Create temporary directory for test
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        templates_dir = setup_test_templates(tmp_path)
        
        # Create test YAML profile
        profile_yaml = tmp_path / 'test_profile.yaml'
        profile_yaml.write_text("""profile:
  name: TestProfile
  
  templates:
    - media_controls
    - fps_wasd
  
  keys:
    1: { key: CTRL, label: [Ctrl] }
    2: { key: SHIFT, label: [Shft] }
""")
        
        # Load profile
        loader = ProfileLoader(profile_yaml)
        loader.load()
        
        # Get keys
        keys = loader.get_keys()
        
        # Check that template keys are present
        if 21 in keys:
            results.pass_test("Main profile has key 21 from media_controls template")
        else:
            results.fail_test("Main profile template key 21", "Key 21 not found")
        
        if 22 in keys:
            results.pass_test("Main profile has key 22 from media_controls template")
        else:
            results.fail_test("Main profile template key 22", "Key 22 not found")
        
        if 6 in keys:
            results.pass_test("Main profile has key 6 from fps_wasd template")
        else:
            results.fail_test("Main profile template key 6", "Key 6 not found")
        
        if 11 in keys:
            results.pass_test("Main profile has key 11 from fps_wasd template")
        else:
            results.fail_test("Main profile template key 11", "Key 11 not found")
        
        # Check that main profile keys override templates
        if 1 in keys and keys[1].get('key') == 'CTRL':
            results.pass_test("Main profile key 1 overrides template")
        else:
            results.fail_test("Main profile key override", "Key 1 not correctly set")


def test_layer_template_inheritance():
    """Test that layers can inherit from templates"""
    print("\n--- Layer Template Inheritance ---")
    
    # Create temporary directory for test
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        templates_dir = setup_test_templates(tmp_path)
        
        # Create test YAML profile with layer templates
        profile_yaml = tmp_path / 'test_layer_profile.yaml'
        profile_yaml.write_text("""profile:
  name: TestLyrProf
  
  templates:
    - media_controls
  
  keys:
    1: { modifier: CTRL, layer: ctrl, label: [Ctrl], no_repeat: true }
    2: { key: SHIFT, label: [Shft] }
  
  layers:
    ctrl:
      extends: parent
      name: TestCtrl
      templates:
        - fps_wasd
      
      keys:
        1: { label: [Ctrl], color: [128, 0, 255] }
""")
        
        # Load profile
        loader = ProfileLoader(profile_yaml)
        loader.load()
        
        # Get layer keys
        layer_keys = loader.get_layer_keys('ctrl')
        
        # Check that layer has keys from parent (including parent's templates)
        if 21 in layer_keys:
            results.pass_test("Layer has key 21 from parent's media_controls template")
        else:
            results.fail_test("Layer parent template key 21", "Key 21 not found in layer")
        
        if 2 in layer_keys:
            results.pass_test("Layer has key 2 from parent")
        else:
            results.fail_test("Layer parent key 2", "Key 2 not found in layer")
        
        # Check that layer has keys from its own templates
        if 6 in layer_keys:
            results.pass_test("Layer has key 6 from fps_wasd template")
        else:
            results.fail_test("Layer template key 6", "Key 6 not found in layer")
        
        if 11 in layer_keys:
            results.pass_test("Layer has key 11 from fps_wasd template")
        else:
            results.fail_test("Layer template key 11", "Key 11 not found in layer")
        
        # Check that layer keys override parent/template keys
        if 1 in layer_keys:
            key1_def = layer_keys[1]
            if 'color' in key1_def and key1_def['color'] == [128, 0, 255]:
                results.pass_test("Layer key 1 overrides parent")
            else:
                results.fail_test("Layer key override", "Key 1 color not correctly overridden")
        else:
            results.fail_test("Layer key 1", "Key 1 not found in layer")


def test_template_application_order():
    """Test that template application follows correct order"""
    print("\n--- Template Application Order ---")
    
    # Create temporary directory for test
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        templates_dir = setup_test_templates(tmp_path)
        
        # Create overlapping template
        overlap_template = templates_dir / 'overlap.yaml'
        overlap_template.write_text("""template:
  name: overlap
  description: Template with overlapping key
  keys:
    6: { key: X, label: [Ovlp] }
""")
        
        # Create test YAML profile with multiple templates
        profile_yaml = tmp_path / 'test_order.yaml'
        profile_yaml.write_text("""profile:
  name: TestOrder
  
  templates:
    - fps_wasd
    - overlap
  
  keys:
    6: { key: Z, label: [Main] }
""")
        
        # Load profile
        loader = ProfileLoader(profile_yaml)
        loader.load()
        
        # Get keys
        keys = loader.get_keys()
        
        # Check that main profile key overrides templates
        if 6 in keys:
            key6_def = keys[6]
            if key6_def.get('key') == 'Z' and key6_def.get('label', [''])[0] == 'Main':
                results.pass_test("Main profile key overrides all templates")
            else:
                results.fail_test("Template order", f"Key 6 not correctly overridden: {key6_def}")
        else:
            results.fail_test("Template order key 6", "Key 6 not found")


def test_template_last_wins():
    """Test that later templates override earlier templates (coats of paint)"""
    print("\n--- Template Last-Wins Behavior ---")
    
    # Create temporary directory for test
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Create test YAML profile with overlapping inline templates
        profile_yaml = tmp_path / 'test_last_wins.yaml'
        profile_yaml.write_text("""templates:
  first:
    keys:
      5: { key: F, label: [Fst] }
  second:
    keys:
      5: { key: S, label: [Snd] }

profile:
  name: TestLastWins
  
  templates:
    - first
    - second  # Should win for key 5 (last wins like "coats of paint")
  
  keys:
    1: { key: CTRL, label: [Ctrl] }
""")
        
        # Load profile
        loader = ProfileLoader(profile_yaml)
        loader.load()
        
        # Get keys
        keys = loader.get_keys()
        
        # Check that second template wins
        if 5 in keys:
            key5_def = keys[5]
            if key5_def.get('key') == 'S' and key5_def.get('label', [''])[0] == 'Snd':
                results.pass_test("Later template overrides earlier template (last wins)")
            else:
                results.fail_test("Template last wins", f"Expected second template to win, got: {key5_def}")
        else:
            results.fail_test("Template last wins key 5", "Key 5 not found")


def test_multiple_layer_templates():
    """Test that layers can use multiple templates"""
    print("\n--- Multiple Layer Templates ---")
    
    # Create temporary directory for test
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        templates_dir = setup_test_templates(tmp_path)
        
        # Create test YAML profile with layer using multiple templates
        profile_yaml = tmp_path / 'test_multi_layer_tpl.yaml'
        profile_yaml.write_text("""profile:
  name: TestMulti
  
  keys:
    1: { modifier: CTRL, layer: ctrl, label: [Ctrl], no_repeat: true }
  
  layers:
    ctrl:
      extends: parent
      name: TestMltCtrl
      templates:
        - fps_wasd
        - media_controls
      
      keys:
        1: { label: [Ctrl] }
""")
        
        # Load profile
        loader = ProfileLoader(profile_yaml)
        loader.load()
        
        # Get layer keys
        layer_keys = loader.get_layer_keys('ctrl')
        
        # Check that layer has keys from both templates
        if 6 in layer_keys:
            results.pass_test("Layer has key 6 from fps_wasd template")
        else:
            results.fail_test("Layer multiple templates key 6", "Key 6 not found")
        
        if 21 in layer_keys:
            results.pass_test("Layer has key 21 from media_controls template")
        else:
            results.fail_test("Layer multiple templates key 21", "Key 21 not found")


def test_inline_templates_main_profile():
    """Test that main profile can use inline templates"""
    print("\n--- Inline Templates (Main Profile) ---")
    
    # Create temporary directory for test
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Create test YAML profile with inline template
        profile_yaml = tmp_path / 'test_inline_main.yaml'
        profile_yaml.write_text("""templates:
  inline_keys:
    keys:
      8: { key: "1", label: [One] }
      9: { key: "2", label: [Two] }

profile:
  name: TestInline
  
  templates:
    - inline_keys
  
  keys:
    1: { key: CTRL, label: [Ctrl] }
""")
        
        # Load profile
        loader = ProfileLoader(profile_yaml)
        loader.load()
        
        # Get keys
        keys = loader.get_keys()
        
        # Check that inline template keys are present
        if 8 in keys:
            results.pass_test("Main profile has key 8 from inline template")
        else:
            results.fail_test("Main inline template key 8", "Key 8 not found")
        
        if 9 in keys:
            results.pass_test("Main profile has key 9 from inline template")
        else:
            results.fail_test("Main inline template key 9", "Key 9 not found")
        
        # Check that main profile keys still work
        if 1 in keys and keys[1].get('key') == 'CTRL':
            results.pass_test("Main profile key 1 works with inline template")
        else:
            results.fail_test("Main profile key with inline template", "Key 1 not correctly set")


def test_inline_templates_layer():
    """Test that layers can use inline templates"""
    print("\n--- Inline Templates (Layer) ---")
    
    # Create temporary directory for test
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Create test YAML profile with layer using inline template
        profile_yaml = tmp_path / 'test_inline_layer.yaml'
        profile_yaml.write_text("""templates:
  inline_layer_keys:
    keys:
      5: { key: E, label: [Use] }
      7: { key: Q, label: [Abil] }

profile:
  name: TestInLayer
  
  keys:
    1: { modifier: CTRL, layer: ctrl, label: [Ctrl], no_repeat: true }
    2: { key: SHIFT, label: [Shft] }
  
  layers:
    ctrl:
      extends: parent
      name: TestLyrInln
      templates:
        - inline_layer_keys
      
      keys:
        1: { label: [Ctrl] }
""")
        
        # Load profile
        loader = ProfileLoader(profile_yaml)
        loader.load()
        
        # Get layer keys
        layer_keys = loader.get_layer_keys('ctrl')
        
        # Check that layer has keys from inline template
        if 5 in layer_keys:
            results.pass_test("Layer has key 5 from inline template")
        else:
            results.fail_test("Layer inline template key 5", "Key 5 not found")
        
        if 7 in layer_keys:
            results.pass_test("Layer has key 7 from inline template")
        else:
            results.fail_test("Layer inline template key 7", "Key 7 not found")
        
        # Check that layer still has parent keys
        if 2 in layer_keys:
            results.pass_test("Layer has key 2 from parent with inline template")
        else:
            results.fail_test("Layer parent key with inline template", "Key 2 not found")


def test_mixed_inline_and_external_templates():
    """Test that profiles can use both inline and external templates"""
    print("\n--- Mixed Inline and External Templates ---")
    
    # Create temporary directory for test
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        templates_dir = setup_test_templates(tmp_path)
        
        # Create test YAML profile mixing inline and external templates
        profile_yaml = tmp_path / 'test_mixed.yaml'
        profile_yaml.write_text("""templates:
  inline_action:
    keys:
      4: { key: R, label: [Reld] }

profile:
  name: TestMixed
  
  templates:
    - inline_action
    - media_controls
  
  keys:
    1: { key: CTRL, label: [Ctrl] }
""")
        
        # Load profile
        loader = ProfileLoader(profile_yaml)
        loader.load()
        
        # Get keys
        keys = loader.get_keys()
        
        # Check inline template key
        if 4 in keys:
            results.pass_test("Profile has key 4 from inline template")
        else:
            results.fail_test("Mixed templates inline key 4", "Key 4 not found")
        
        # Check external template key
        if 21 in keys:
            results.pass_test("Profile has key 21 from external template")
        else:
            results.fail_test("Mixed templates external key 21", "Key 21 not found")
        
        # Check profile key
        if 1 in keys:
            results.pass_test("Profile has key 1 with mixed templates")
        else:
            results.fail_test("Mixed templates profile key 1", "Key 1 not found")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Template Inheritance Unit Tests")
    print("=" * 60)
    
    test_main_profile_template_inheritance()
    test_layer_template_inheritance()
    test_template_application_order()
    test_template_last_wins()
    test_multiple_layer_templates()
    test_inline_templates_main_profile()
    test_inline_templates_layer()
    test_mixed_inline_and_external_templates()
    
    success = results.print_summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
