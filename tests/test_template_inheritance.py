#!/usr/bin/env python3
"""
Unit Tests for Template Inheritance in YAML Profile Loader

Tests the template inheritance feature including:
- "Last wins" behavior for multiple templates
- Explicit keys override templates
- Missing template warnings
- Layer template inheritance
- Edge cases

Author: JamesDBartlett3
Date: 2026-02-01
"""

import sys
import tempfile
from pathlib import Path
from io import StringIO

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


def setup_test_templates(temp_dir: Path):
    """Create test template files and inline templates."""
    # Create media template with correct syntax
    media_template = temp_dir / "media_controls.yaml"
    media_template.write_text("""template:
  name: media_controls
  description: Standard media playback controls
  keys:
    21: { script: MK_VOLUP }
    22: { script: MK_VOLDOWN }
    23: { script: MK_MUTE }
""")
    
    # Create a second template for testing override
    custom_template = temp_dir / "custom_media.yaml"
    custom_template.write_text("""template:
  name: custom_media
  description: Custom media controls
  keys:
    21: { script: "MK_VOLUP\\nMK_VOLUP" }
    22: { script: "MK_VOLDOWN\\nMK_VOLDOWN" }
    24: { script: MK_NEXT }
""")
    
    return media_template, custom_template


def test_last_wins_template_override():
    """Test that later templates override earlier ones for the same key."""
    print("\n--- Test: Last Wins Template Override ---")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        # Structure: temp/workbench/test.yaml and temp/templates/
        workbench_dir = temp_path / "workbench"
        workbench_dir.mkdir()
        templates_dir = temp_path / "templates"
        templates_dir.mkdir()
        
        # Create templates
        template1 = templates_dir / "template1.yaml"
        template1.write_text("""template:
  name: template1
  keys:
    1: { key: A }
    2: { key: B }
    3: { key: C }
""")
        
        template2 = templates_dir / "template2.yaml"
        template2.write_text("""template:
  name: template2
  keys:
    2: { key: X }
    3: { key: Y }
    4: { key: Z }
""")
        
        # Create profile that uses both templates
        profile_path = workbench_dir / "test.yaml"
        profile_path.write_text("""profile:
  name: Test
  templates:
    - template1
    - template2
""")
        
        # Load profile
        loader = ProfileLoader(profile_path)
        loader.load()
        keys = loader.get_keys()
        
        # Verify last wins behavior
        # Key 1 from template1 only
        if keys.get(1, {}).get('key') == 'A':
            results.pass_test("Key 1 from template1 (A)")
        else:
            results.fail_test("Key 1 from template1", f"Expected 'A', got {keys.get(1)}")
        
        # Key 2 should be from template2 (overrides template1)
        if keys.get(2, {}).get('key') == 'X':
            results.pass_test("Key 2 from template2 overrides template1 (X)")
        else:
            results.fail_test("Key 2 override", f"Expected 'X', got {keys.get(2)}")
        
        # Key 3 should be from template2 (overrides template1)
        if keys.get(3, {}).get('key') == 'Y':
            results.pass_test("Key 3 from template2 overrides template1 (Y)")
        else:
            results.fail_test("Key 3 override", f"Expected 'Y', got {keys.get(3)}")
        
        # Key 4 from template2 only
        if keys.get(4, {}).get('key') == 'Z':
            results.pass_test("Key 4 from template2 (Z)")
        else:
            results.fail_test("Key 4 from template2", f"Expected 'Z', got {keys.get(4)}")


def test_explicit_keys_override_templates():
    """Test that explicit profile keys override all templates."""
    print("\n--- Test: Explicit Keys Override Templates ---")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        workbench_dir = temp_path / "workbench"
        workbench_dir.mkdir()
        templates_dir = temp_path / "templates"
        templates_dir.mkdir()
        
        # Create template
        template = templates_dir / "base.yaml"
        template.write_text("""template:
  name: base
  keys:
    1: { key: A }
    2: { key: B }
    3: { key: C }
""")
        
        # Create profile with explicit keys that override template
        profile_path = workbench_dir / "test.yaml"
        profile_path.write_text("""profile:
  name: Test
  templates:
    - base
  keys:
    2: { key: EXPLICIT }
""")
        
        # Load profile
        loader = ProfileLoader(profile_path)
        loader.load()
        keys = loader.get_keys()
        
        # Verify explicit key wins
        if keys.get(1, {}).get('key') == 'A':
            results.pass_test("Key 1 from template (A)")
        else:
            results.fail_test("Key 1 from template", f"Expected 'A', got {keys.get(1)}")
        
        if keys.get(2, {}).get('key') == 'EXPLICIT':
            results.pass_test("Key 2 explicit overrides template (EXPLICIT)")
        else:
            results.fail_test("Key 2 explicit override", f"Expected 'EXPLICIT', got {keys.get(2)}")
        
        if keys.get(3, {}).get('key') == 'C':
            results.pass_test("Key 3 from template (C)")
        else:
            results.fail_test("Key 3 from template", f"Expected 'C', got {keys.get(3)}")


def test_missing_template_warning():
    """Test that missing templates generate warnings."""
    print("\n--- Test: Missing Template Warning ---")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        workbench_dir = temp_path / "workbench"
        workbench_dir.mkdir()
        templates_dir = temp_path / "templates"
        templates_dir.mkdir()
        
        # Create profile with non-existent template
        profile_path = workbench_dir / "test.yaml"
        profile_path.write_text("""profile:
  name: Test
  templates:
    - nonexistent_template
  keys:
    1: { key: A }
""")
        
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured = StringIO()
        
        try:
            # Load profile
            loader = ProfileLoader(profile_path)
            loader.load()
            
            # Restore stdout
            sys.stdout = old_stdout
            output = captured.getvalue()
            
            # Check for warning
            if "Warning: Template 'nonexistent_template' not found" in output:
                results.pass_test("Warning emitted for missing template")
            else:
                results.fail_test("Missing template warning", f"No warning found in output: {output}")
        finally:
            sys.stdout = old_stdout


def test_layer_template_inheritance():
    """Test template inheritance in layers."""
    print("\n--- Test: Layer Template Inheritance ---")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        workbench_dir = temp_path / "workbench"
        workbench_dir.mkdir()
        templates_dir = temp_path / "templates"
        templates_dir.mkdir()
        
        # Create template
        template = templates_dir / "base.yaml"
        template.write_text("""template:
  name: base
  keys:
    1: { key: A }
    2: { key: B }
""")
        
        # Create profile with layer that extends template
        profile_path = workbench_dir / "test.yaml"
        profile_path.write_text("""profile:
  name: Test
  templates:
    - base
  keys:
    1: { key: X }
  layers:
    layer1:
      name: Layer 1
      type: toggle
      trigger: 5
      extends:
        - base
      keys:
        2: { key: LAYER_OVERRIDE }
""")
        
        # Load profile
        loader = ProfileLoader(profile_path)
        loader.load()
        
        # Get layer keys
        layer_keys = loader.get_layer_keys('layer1')
        
        # Verify layer inheritance
        if layer_keys.get(1, {}).get('key') == 'A':
            results.pass_test("Layer inherits key 1 from template (A)")
        else:
            results.fail_test("Layer inherit key 1", f"Expected 'A', got {layer_keys.get(1)}")
        
        if layer_keys.get(2, {}).get('key') == 'LAYER_OVERRIDE':
            results.pass_test("Layer explicit key overrides template (LAYER_OVERRIDE)")
        else:
            results.fail_test("Layer explicit override", f"Expected 'LAYER_OVERRIDE', got {layer_keys.get(2)}")


def test_layer_extends_another_layer():
    """Test layer extending another layer."""
    print("\n--- Test: Layer Extends Another Layer ---")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        workbench_dir = temp_path / "workbench"
        workbench_dir.mkdir()
        
        # Create profile with multiple layers
        profile_path = workbench_dir / "test.yaml"
        profile_path.write_text("""profile:
  name: Test
  layers:
    base_layer:
      name: Base Layer
      type: toggle
      trigger: 5
      keys:
        1: { key: A }
        2: { key: B }
    extended_layer:
      name: Extended Layer
      type: toggle
      trigger: 6
      extends:
        - base_layer
      keys:
        2: { key: OVERRIDE }
        3: { key: C }
""")
        
        # Load profile
        loader = ProfileLoader(profile_path)
        loader.load()
        
        # Get extended layer keys
        layer_keys = loader.get_layer_keys('extended_layer')
        
        # Verify layer-to-layer inheritance
        if layer_keys.get(1, {}).get('key') == 'A':
            results.pass_test("Layer inherits key 1 from base layer (A)")
        else:
            results.fail_test("Layer inherit from layer", f"Expected 'A', got {layer_keys.get(1)}")
        
        if layer_keys.get(2, {}).get('key') == 'OVERRIDE':
            results.pass_test("Layer overrides inherited key 2 (OVERRIDE)")
        else:
            results.fail_test("Layer override inherited", f"Expected 'OVERRIDE', got {layer_keys.get(2)}")
        
        if layer_keys.get(3, {}).get('key') == 'C':
            results.pass_test("Layer has own key 3 (C)")
        else:
            results.fail_test("Layer own key", f"Expected 'C', got {layer_keys.get(3)}")


def test_empty_template():
    """Test empty template edge case."""
    print("\n--- Test: Empty Template Edge Case ---")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        workbench_dir = temp_path / "workbench"
        workbench_dir.mkdir()
        templates_dir = temp_path / "templates"
        templates_dir.mkdir()
        
        # Create empty template
        template = templates_dir / "empty.yaml"
        template.write_text("""template:
  name: empty
  keys: {}
""")
        
        # Create profile that uses empty template
        profile_path = workbench_dir / "test.yaml"
        profile_path.write_text("""profile:
  name: Test
  templates:
    - empty
  keys:
    1: { key: A }
""")
        
        # Load profile - should not crash
        try:
            loader = ProfileLoader(profile_path)
            loader.load()
            keys = loader.get_keys()
            
            if keys.get(1, {}).get('key') == 'A':
                results.pass_test("Empty template handled correctly")
            else:
                results.fail_test("Empty template", f"Expected key 1='A', got {keys.get(1)}")
        except Exception as e:
            results.fail_test("Empty template", f"Exception: {e}")


def test_template_with_no_keys_section():
    """Test template with no keys section edge case."""
    print("\n--- Test: Template With No Keys Section ---")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        workbench_dir = temp_path / "workbench"
        workbench_dir.mkdir()
        templates_dir = temp_path / "templates"
        templates_dir.mkdir()
        
        # Create template without keys section
        template = templates_dir / "no_keys.yaml"
        template.write_text("""template:
  name: no_keys
  description: Template without keys
""")
        
        # Create profile that uses this template
        profile_path = workbench_dir / "test.yaml"
        profile_path.write_text("""profile:
  name: Test
  templates:
    - no_keys
  keys:
    1: { key: A }
""")
        
        # Load profile - should not crash
        try:
            loader = ProfileLoader(profile_path)
            loader.load()
            keys = loader.get_keys()
            
            if keys.get(1, {}).get('key') == 'A':
                results.pass_test("Template without keys section handled correctly")
            else:
                results.fail_test("Template without keys", f"Expected key 1='A', got {keys.get(1)}")
        except Exception as e:
            results.fail_test("Template without keys", f"Exception: {e}")


def test_non_oriented_templates():
    """Test templates with non-oriented key definitions."""
    print("\n--- Test: Non-Oriented Templates ---")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        workbench_dir = temp_path / "workbench"
        workbench_dir.mkdir()
        templates_dir = temp_path / "templates"
        templates_dir.mkdir()
        
        # Create media controls template with correct syntax
        media_template = templates_dir / "media.yaml"
        media_template.write_text("""template:
  name: media
  description: Media controls
  keys:
    21: { script: MK_VOLUP }
    22: { script: MK_VOLDOWN }
    23: { script: MK_MUTE }
""")
        
        # Create profile using template
        profile_path = workbench_dir / "test.yaml"
        profile_path.write_text("""profile:
  name: Test
  templates:
    - media
  keys:
    1: { key: A }
""")
        
        # Load profile
        loader = ProfileLoader(profile_path)
        loader.load()
        keys = loader.get_keys()
        
        # Verify template keys are applied
        if keys.get(21, {}).get('script') == 'MK_VOLUP':
            results.pass_test("Media key 21 (MK_VOLUP)")
        else:
            results.fail_test("Media key 21", f"Expected 'MK_VOLUP', got {keys.get(21)}")
        
        if keys.get(22, {}).get('script') == 'MK_VOLDOWN':
            results.pass_test("Media key 22 (MK_VOLDOWN)")
        else:
            results.fail_test("Media key 22", f"Expected 'MK_VOLDOWN', got {keys.get(22)}")
        
        if keys.get(23, {}).get('script') == 'MK_MUTE':
            results.pass_test("Media key 23 (MK_MUTE)")
        else:
            results.fail_test("Media key 23", f"Expected 'MK_MUTE', got {keys.get(23)}")


def test_multiple_templates_last_wins():
    """Test that with 3+ templates, the last one wins."""
    print("\n--- Test: Multiple Templates (3+) Last Wins ---")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        workbench_dir = temp_path / "workbench"
        workbench_dir.mkdir()
        templates_dir = temp_path / "templates"
        templates_dir.mkdir()
        
        # Create three templates that define the same key
        for i in range(1, 4):
            template = templates_dir / f"template{i}.yaml"
            template.write_text(f"""template:
  name: template{i}
  keys:
    1: {{ key: KEY{i} }}
""")
        
        # Create profile using all three templates
        profile_path = workbench_dir / "test.yaml"
        profile_path.write_text("""profile:
  name: Test
  templates:
    - template1
    - template2
    - template3
""")
        
        # Load profile
        loader = ProfileLoader(profile_path)
        loader.load()
        keys = loader.get_keys()
        
        # Verify last template wins
        if keys.get(1, {}).get('key') == 'KEY3':
            results.pass_test("Last of 3 templates wins (KEY3)")
        else:
            results.fail_test("Last of 3 templates", f"Expected 'KEY3', got {keys.get(1)}")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Template Inheritance Tests")
    print("=" * 60)
    
    test_last_wins_template_override()
    test_explicit_keys_override_templates()
    test_missing_template_warning()
    test_layer_template_inheritance()
    test_layer_extends_another_layer()
    test_empty_template()
    test_template_with_no_keys_section()
    test_non_oriented_templates()
    test_multiple_templates_last_wins()
    
    # Print summary
    success = results.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
