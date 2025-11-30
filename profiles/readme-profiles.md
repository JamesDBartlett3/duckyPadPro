# duckyPad Pro Profiles

Complete profile packages for duckyPad Pro, organized by use case and application.

## Table of Contents

- [Overview](#overview)
- [YAML Profile System](#yaml-profile-system)
  - [Basic Structure](#basic-structure)
  - [Inheritance with `extends`](#inheritance-with-extends)
  - [Templates](#templates)
  - [Layers](#layers)
  - [Key Definitions](#key-definitions)
  - [Configuration Options](#configuration-options)
- [Creating Profiles](#creating-profiles)
- [Deployment](#deployment)
- [Examples](#examples)

## Overview

This directory contains complete profiles for duckyPad Pro. Each profile is a self-contained package that includes:

- **Key Scripts** (`key1.txt` through `key26.txt`) - duckyScript code for each key press
- **Release Scripts** (`key1-release.txt` through `key26-release.txt`) - Optional scripts for key release events
- **Configuration** (`config.txt`) - Profile settings (labels, colors, directives)
- **Documentation** (`README.md`) - Usage instructions and key mappings

## YAML Profile System

The YAML profile system provides a powerful, declarative way to define duckyPad Pro profiles with support for inheritance, templates, and layers.

### Basic Structure

A YAML profile consists of a main profile definition with optional templates and layers:

```yaml
profile:
  name: MyProfile

  config:
    orientation: landscape
    background_color: [100, 150, 200]
    dim_unused: true

  keys:
    1: { key: CTRL, label: [Ctrl] }
    2: { key: SHIFT, label: [Shft] }
    # ... more keys

  layers:
    modifier:
      name: MyProf-Mod
      keys:
        # ... layer-specific keys
```

### Inheritance with `extends`

The `extends` directive allows layers to inherit keys from other sources, eliminating duplication.

#### Layer-Level Extends

Use `extends: parent` to inherit ALL keys from the main profile, then override specific ones:

```yaml
profile:
  name: Foxhole

  keys:
    1: { modifier: CTRL, layer: ctrl, label: [Ctrl] }
    2: { key: SHIFT, hold: true, label: [Run] }
    3: { key: TAB, label: [Inv] }
    # ... 23 more keys

  layers:
    ctrl:
      extends: parent # Inherit all 26 keys from main profile
      name: Foxhole-Ctrl

      keys:
        # Only define keys that differ from parent
        1: { label: [Ctrl], color: [128, 0, 255] } # Override appearance
        6: { label: [A] } # Override with empty action
        8: { label: ["1"] } # Override with empty action
```

**How it works:**

1. All 26 keys from `parent` (main profile) are copied to the `ctrl` layer
2. Keys 1, 6, and 8 are overridden with new definitions
3. Keys 2-5, 7, 9-26 retain their parent definitions

#### Extending Other Layers

Layers can extend other layers, creating inheritance chains:

```yaml
layers:
  shift:
    extends: parent
    keys:
      6: { key: A, hold: true }

  shift_ctrl:
    extends: shift # Inherit from shift layer instead of parent
    keys:
      1: { modifier: CTRL, layer: shift_ctrl }
```

#### What Gets Inherited

When a layer extends another source:

- ✅ **Keys**: All key definitions (key, label, color, hold, no_repeat, allow_abort)
- ✅ **Actions**: Media controls, custom actions
- ❌ **NOT inherited**: Layer switchers (layer_type, modifier, layer directives)
- ❌ **NOT inherited**: Config (background_color, orientation) - must be explicitly set

### Templates

Templates are reusable key sets that can be applied across multiple profiles.

#### Template Files

Create template files in `profiles/templates/`:

```yaml
# profiles/templates/fps_wasd.yaml
template:
  name: fps_wasd
  description: Standard FPS WASD movement controls
  keys:
    11: { key: W, label: [Fwd, "(W)"], hold: true }
    10: { key: S, label: [Back, "(S)"], hold: true }
    6: { key: A, label: [Left, "(A)"], hold: true }
    14: { key: D, label: [Rght, "(D)"], hold: true }
    17: { key: SPACE, label: [Jump], hold: true }
    9: { key: C, label: [Crnch] }
```

```yaml
# profiles/templates/media_controls.yaml
template:
  name: media_controls
  description: Standard media playback controls
  keys:
    21: { script: MK_VOLUP }
    22: { script: MK_VOLDOWN }
    23: { script: MK_MUTE }
    24: { script: MK_NEXT }
    25: { script: MK_PREV }
    26: { script: MK_PP }
```

#### Using Templates in Profiles

Reference templates by name in the `templates` list:

```yaml
profile:
  name: Valorant

  templates:
    - fps_wasd # Load FPS controls template
    - media_controls # Load media controls template

  keys:
    # Templates applied first, then these override
    5: { key: E, label: [Abil] }
    7: { key: Q, label: [Util] }
    8: { key: "1", label: [Prim] }
    # Keys 6, 9, 10, 11, 14, 17 from fps_wasd template
    # Keys 21-26 from media_controls template
```

#### Templates in Layers

Layers can also use templates:

```yaml
layers:
  numpad:
    templates:
      - numpad_layout # Layer-specific template
    keys:
      1: { label: [Rtrn] }
```

#### Template Application Order

```
1. Profile templates applied (in order listed)
2. Profile keys applied (override templates)
3. Layer extends processed (copy from parent/other layer)
4. Layer templates applied (in order listed)
5. Layer keys applied (override templates and extends)
```

Example:

```yaml
profile:
  name: Example
  templates: [template_a, template_b]
  keys:
    1: { key: A } # Overrides template_a or template_b key 1

  layers:
    layer1:
      extends: parent # Start with all parent keys (including templates)
      templates: [template_c] # Add more keys from template_c
      keys:
        2: { key: B } # Override key 2
```

**Final result for layer1:**

- Key 1: `A` (from profile keys)
- Key 2: `B` (from layer keys)
- Other keys: From `template_a`, `template_b`, `template_c`, or parent profile

### Layers

Layers are separate profiles that can be switched to using layer switcher keys. duckyPad Pro natively supports multiple profiles - layers are just profiles that are designed to work together.

#### Layer Types

Different layer types control how the switcher behaves:

```yaml
keys:
  1:
    layer_type: modifier_hold # Default: hold key, switch layer, release key
    modifier: CTRL
    layer: ctrl
    label: [Ctrl]
```

**Available layer types:**

- `modifier_hold` - Hold modifier while layer is active (default)
- `toggle` - Press to switch, press again to return
- `oneshot` - Switch layer for one key press, then return
- `momentary` - Hold to activate, release to return (no modifier key sent)

#### Layer Switcher Keys

**Press behavior:**

```
KEYDOWN <modifier>
GOTO_PROFILE <layer-name>
```

**Release behavior (in main profile):**

```
KEYUP <modifier>
```

**Release behavior (in layer profile):**

```
KEYUP <modifier>
GOTO_PROFILE <parent-name>
```

#### Layer Configuration

Layers can have their own configuration:

```yaml
layers:
  ctrl:
    extends: parent
    name: MyProfile-Ctrl

    config:
      orientation: landscape
      background_color: [192, 192, 192] # Different from main profile
      dim_unused: false

    keys:
      # ...
```

### Key Definitions

#### Simple Keys

```yaml
keys:
  6: A # Ultra-compact: just the key
  7: SHIFT # Modifier key
  8: ESCAPE # Special key
```

#### Keys with Labels

```yaml
keys:
  6: [A, Move] # [key, label1, label2]
  7: [TAB, Inv, "(Tab)"]
```

#### Full Object Syntax

```yaml
keys:
  6:
    key: A
    hold: true # Generate KEYDOWN/KEYUP instead of simple press
    label: [A, "(Key)"]
    color: [255, 0, 0]
    no_repeat: true # Add 'dr N' directive (don't repeat when held)
    allow_abort: true # Add 'ab N' directive (allow early exit)
```

#### Hold Keys

For keys that should be held down (movement, modifiers):

```yaml
keys:
  2: { key: SHIFT, hold: true, label: [Run] }
  6: { key: a, hold: true, label: [Left] }
```

**Generates:**

- `key2.txt`: `DEFAULTDELAY 0\nKEYDOWN SHIFT\n`
- `key2-release.txt`: `DEFAULTDELAY 0\nKEYUP SHIFT\n`

#### Label-Only Keys (Empty Actions)

For layer keys that should do nothing (used with modifier layers):

```yaml
layers:
  ctrl:
    extends: parent
    keys:
      6: { label: [A] } # No 'key' field = empty action
      8: { label: ["1"] }
```

**Generates:**

- `key6.txt`: (empty file)
- Config entry: `z6 A`

**Use case:** In a Ctrl modifier layer, key 6 does nothing, but shows label "A" to indicate pressing it will send Ctrl+A (because Ctrl from switcher is still held).

#### Media Keys

```yaml
keys:
  21:
    script: MK_VOLUP
  22:
    script: MK_VOLDOWN
```

**Available media key commands (duckyScript):**

- `MK_VOLUP`, `MK_VOLDOWN`, `MK_MUTE`
- `MK_NEXT`, `MK_PREV`, `MK_PP` (play/pause)
- `MK_STOP`

#### Layer Switchers

```yaml
keys:
  1:
    layer_type: modifier_hold
    modifier: CTRL
    layer: ctrl
    label: [Ctrl]
    color: [128, 0, 255]
    no_repeat: true
```

### Configuration Options

#### Profile-Level Config

```yaml
profile:
  config:
    orientation: landscape # or portrait (default)
    background_color: [84, 22, 180]
    dim_unused: true # Dim keys without scripts
```

#### Layer-Level Config

```yaml
layers:
  ctrl:
    config:
      orientation: landscape
      background_color: [192, 192, 192]
```

#### Key-Level Directives

```yaml
keys:
  1:
    key: CTRL
    no_repeat: true # Don't auto-repeat when held (adds 'dr 1')
    allow_abort: true # Allow early exit from macro (adds 'ab 1')
    color: [255, 0, 0]
    label: [Ctrl]
```

## Creating Profiles

### Using YAML

1. **Create a YAML file:**

   ```yaml
   # profiles/my-game.yaml
   profile:
     name: MyGame

     config:
       orientation: landscape
       background_color: [100, 150, 200]

     keys:
       1: { key: CTRL, label: [Ctrl] }
       # ... more keys

     layers:
       ctrl:
         extends: parent
         keys:
           # ... overrides
   ```

2. **Generate, compile, and deploy:**

   ```bash
   python execute.py yaml workbench/my-game.yaml
   ```

   Or step by step:

   ```bash
   # Generate only
   python execute.py yaml workbench/my-game.yaml --generate-only

   # Compile generated profiles
   python execute.py compile workbench/profiles/my-game

   # Deploy to SD card
   python execute.py deploy workbench/profiles/my-game
   ```

### Manual Creation

1. Create profile directory
2. Create `key1.txt` through `keyN.txt` with duckyScript
3. Create `config.txt` with settings
4. Create `README.md` with documentation

## Deployment

### Deployment Steps

1. **Generate, compile, and deploy from YAML:**

   ```bash
   python execute.py yaml workbench/foxhole.yaml
   ```

   This automatically:

   - Generates profiles in `workbench/profiles/`
   - Compiles duckyScript to bytecode
   - Deploys to SD card with proper naming
   - Updates `profile_info.txt`

2. **Or deploy manually:**

   ```bash
   # Generate only
   python execute.py yaml workbench/foxhole.yaml --generate-only

   # Compile
   python execute.py compile workbench/profiles/profile_Foxhole

   # Deploy
   python execute.py deploy workbench/profiles/profile_Foxhole
   ```

3. **Test on duckyPad Pro:**
   - Device auto-reboots after deployment
   - Use +/- buttons to switch between profiles

## Examples

### Example 1: Simple Profile

```yaml
profile:
  name: SimpleExample

  keys:
    1: CTRL
    2: SHIFT
    3: TAB
```

### Example 2: Profile with Templates

```yaml
profile:
  name: FPSGame

  templates:
    - fps_wasd
    - media_controls

  keys:
    5: { key: E, label: [Use] }
    7: { key: Q, label: [Abil] }
```

### Example 3: Profile with Modifier Layer

```yaml
profile:
  name: Productivity

  config:
    orientation: landscape
    background_color: [100, 150, 200]

  keys:
    1: { modifier: CTRL, layer: ctrl, label: [Ctrl], no_repeat: true }
    2: { key: SHIFT, hold: true, label: [Shft] }
    3: { key: TAB, label: [Tab] }
    6-9: [A, S, D, F]

  layers:
    ctrl:
      extends: parent
      name: Prod-Ctrl

      config:
        background_color: [192, 192, 192]

      keys:
        1: { label: [Ctrl], color: [128, 0, 255] }
        6: { label: [SelA] } # Empty action - shows Ctrl+A label
        7: { label: [Save] } # Empty action - shows Ctrl+S label
```

### Example 4: Multi-Layer with Templates

```yaml
profile:
  name: Advanced

  templates:
    - media_controls

  keys:
    1: { modifier: CTRL, layer: ctrl, label: [Ctrl] }
    2: { modifier: ALT, layer: alt, label: [Alt] }
    3-10: [A, S, D, F, G, H, J, K]

  layers:
    ctrl:
      extends: parent
      keys:
        1: { label: [Ctrl], color: [255, 0, 0] }
        3: { label: [SelA] }

    alt:
      extends: parent
      templates:
        - window_management
      keys:
        2: { label: [Alt], color: [0, 255, 0] }
        3: { key: F4, label: [Close] }
```

---

## See Also

- [Getting Started Guide](../docs/getting-started.md)
- [Profile Guide](../docs/profile-guide.md)
- [duckyScript Documentation](https://dekunukem.github.io/duckyPad-Pro/doc/duckyscript_info.html)
- [Tools & Utilities](../tools/readme-tools.md)
