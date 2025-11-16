# Feature Ideas

This document contains ideas for future features and enhancements to the duckyPadPro repository.

## Important Technical Constraints

### Key Numbering

For complete key layout diagrams and orientation mappings, see [Key Layout Reference](../docs/key-layout.md).

**Quick reference:**

- Physical keys are numbered 1-20, left-to-right, top-to-bottom (in portrait mode)
- Rotary encoder inputs are numbered 21-26 (2 encoders × 3 inputs each)
- Key numbering does not change when rotating orientation
- Portrait mode: 4 columns × 5 rows (physical keys)
- Landscape mode: 5 columns × 4 rows (90° CCW rotation)

### Key Label Limitations

- **Maximum 2 lines** of text per key label
- **Maximum 5 characters** per line (ASCII only)
- Total: 10 characters maximum per key label

All helper tools and generators must respect this constraint when creating key labels or suggesting naming conventions.

## Orientation/Layout Management

### 1. Profile Orientation Converter

Converts existing profiles between portrait (4×5) and landscape (5×4) orientations by remapping key positions.

**Key mapping logic:**

- Key numbers (1-20) remain constant regardless of orientation
- Portrait: keys arranged in 4 columns × 5 rows (key 1 at top-left)
- Landscape: keys arranged in 5 columns × 4 rows (key 1 at bottom-left after 90° CCW rotation)
- Orientation setting changes physical layout interpretation, not key numbering

**Use case:** Users who switch between portrait and landscape modes can convert their existing profiles rather than recreating them manually.

### 2. Orientation Validator

Checks if a profile is optimized for a specific orientation:

- Detects key layout patterns (e.g., logical groupings)
- Warns if the profile seems designed for the opposite orientation
- Suggests which keys might be awkward to reach in current orientation

**Use case:** Helps users identify when a profile they downloaded might not work well with their current orientation setting.

### 3. Dual-Orientation Profile Generator

Creates two versions of the same profile simultaneously:

- Takes a logical key mapping (by function, not position)
- Generates both portrait and landscape layouts
- Maintains the same functional grouping optimized for each orientation

**Use case:** Profile creators can publish both versions, making their profiles more accessible to all users.

### 4. Orientation Preview Tool

Visual ASCII/text representation showing:

- Current key layout in both orientations
- Which key labels/functions are assigned to which physical positions
- Helps visualize before copying to device

**Use case:** Preview how a profile will look on the physical device before transferring it.

### 5. Smart Key Organizer

Suggests optimal key arrangements based on:

- Frequency of use (put common keys in easy-to-reach positions)
- Key relationships (group related functions)
- Orientation-specific ergonomics (accounting for different thumb/finger reach patterns)

**Use case:** Users creating new profiles can get suggestions for the most ergonomic key placement.

### 6. Orientation Migration Helper

For users switching orientations:

- Analyzes muscle memory patterns from current layout
- Suggests gradual transition strategies
- Creates "hybrid" profiles for learning period

**Use case:** Users who want to switch orientations can do so gradually without losing productivity.

### 7. Profile Mirror Tool

Mirrors a profile horizontally (left-right) for handedness conversion:

- Swaps key positions horizontally while preserving functionality
- Portrait mode: Mirrors across vertical center axis (keys 1↔4, 2↔3, 5↔8, etc.)
- Landscape mode: Mirrors across vertical center axis (keys 4↔20, 8↔16, 12 stays center, etc.)
- **Rotary encoder keys (21-26) are excluded** from mirroring (position is fixed on device)
- Preserves key functions/scripts, only changes physical positions
- Option to create mirrored copy or overwrite original
- Useful for converting right-handed profiles to left-handed layouts

**Example (portrait mode - 4 columns × 5 rows):**

- Row 1: Key 1 ↔ Key 4, Key 2 ↔ Key 3
- Row 2: Key 5 ↔ Key 8, Key 6 ↔ Key 7
- Row 3: Key 9 ↔ Key 12, Key 10 ↔ Key 11
- Row 4: Key 13 ↔ Key 16, Key 14 ↔ Key 15
- Row 5: Key 17 ↔ Key 20, Key 18 ↔ Key 19

**Example (landscape mode - 5 columns × 4 rows):**

- Top row: Key 4 ↔ Key 20, Key 8 ↔ Key 16, Key 12 stays center
- Row 2: Key 3 ↔ Key 19, Key 7 ↔ Key 15, Key 11 stays center
- Row 3: Key 2 ↔ Key 18, Key 6 ↔ Key 14, Key 10 stays center
- Bottom row: Key 1 ↔ Key 17, Key 5 ↔ Key 13, Key 9 stays center

**Use case:** Users can share profiles regardless of hand dominance, or switch profiles when changing primary hand position. Useful for accessibility or ergonomic customization.

---

## Profile/Layer Management

### 1. Multi-Layer Profile Generator

Generates a set of interconnected profiles that function like keyboard layers:

- Creates multiple profile directories with consistent structure
- Automatically generates the profile-switching duckyScript commands
- Supports both toggle (press to switch) and hold (momentary) modes
- Visual indicators in key labels show current layer (within 2-line, 5-char limit)
- Option for "home" key to return to default profile
- User specifies which keys are navigation vs. functional (doesn't impose a template)

**Use case:** Power users can access 100+ functions on a 26-input device (20 physical keys + 6 rotary encoder inputs) by treating profiles as layers, similar to QMK keyboard firmware. Creates the infrastructure for multi-profile setups without forcing a specific navigation layout.

### 2. Navigation Layout Templates

Pre-built navigation key configurations optimized for different use cases:

**Portrait Mode (4 columns × 5 rows):**

- **Bottom row navigation**: Keys 17-20 as switchers, remaining keys functional
- **Top row navigation**: Keys 1-4 as switchers, remaining keys functional
- **Left column navigation**: Keys 1, 5, 9, 13, 17 as switchers, remaining keys functional
- **Right column navigation**: Keys 4, 8, 12, 16, 20 as switchers, remaining keys functional

**Landscape Mode (5 columns × 4 rows, 90° CCW rotation):**

- **Bottom row navigation**: Keys 1, 5, 9, 13, 17 as switchers, remaining keys functional (was left column in portrait)
- **Top row navigation**: Keys 4, 8, 12, 16, 20 as switchers, remaining keys functional (was right column in portrait)
- **Left column navigation**: Keys 1-4 as switchers, remaining keys functional (was top row in portrait)
- **Right column navigation**: Keys 17-20 as switchers, remaining keys functional (was bottom row in portrait)

**Use case:** Users can choose a navigation layout that matches their hand size, usage patterns, and orientation preference. Works with the Multi-Layer Profile Generator to create complete layer systems.

### 3. Hold-Toggle Hybrid Generator

Creates profiles with sophisticated layer switching behavior:

- Hold a key for momentary layer access (returns on release)
- Double-tap to toggle and stay on that layer
- Generates the necessary duckyScript logic for this behavior
- Visual feedback in key labels within 2-line, 5-char limit (e.g., "MEDIA" on line 1, "hold" on line 2)

**Use case:** Advanced users can have both quick-access layers and persistent layers without sacrificing keys.

### 4. Layer Inheritance Tool

Manages shared functionality across multiple layers:

- Define "base" keys that appear in all layers
- Specify per-layer overrides
- Automatically propagates base key changes to all layer profiles
- Reduces duplication and maintenance burden

**Use case:** Users with navigation keys or common shortcuts don't need to manually update them across 5+ profiles.

### 5. Visual Layer Map Generator

Creates documentation showing the complete layer structure:

- ASCII/text diagram of all layers and navigation paths
- Shows which keys switch to which profiles
- Indicates toggle vs. hold behavior
- Exports as markdown or HTML for reference

**Use case:** Users with complex multi-layer setups can visualize and share their configuration structure.

### 6. Modifier Layer Generator

Creates momentary layer switchers that simultaneously hold down modifier keys:

- Switcher key holds modifier combo (e.g., Win+Ctrl+Alt) while switching to a layer
- Layer contains simple keys (A-Z, F1-F12, numbers, symbols, etc.)
- Pressing a key on the modifier layer sends the modifier combo + that key
- Releasing the switcher releases modifiers and returns to main layer
- Supports any modifier combination (Ctrl, Alt, Shift, Win/Cmd, or combinations)
- Automatically generates the duckyScript logic for press/release behavior

**Example workflow:**

- Hold switcher key → Win+Ctrl+Alt is pressed, switch to modifier layer
- Press key containing "F5" → System receives Win+Ctrl+Alt+F5
- Release switcher → Win+Ctrl+Alt released, return to main layer

**Use case:** Power users working with applications that have complex modifier-heavy shortcut schemes (DAWs, video editors, IDEs) can access dozens of shortcuts efficiently. Main layer stays reserved for most common shortcuts, while modifier layers provide access to additional shortcuts without memorizing complex multi-key combinations.

---

## Script Generation & Automation

### 1. Macro Recorder

Records keyboard and mouse actions and generates duckyScript code for playback:

- User specifies which key the macro should be assigned to
- Recording captures keyboard presses, modifier combinations, and timing
- Optional mouse movement and click recording
- Generates optimized duckyScript with appropriate DELAY commands
- Allows post-recording editing and adjustment of delays
- Option to simplify/optimize recorded script (remove redundant actions, adjust timing)
- Preview function to test generated script before saving

**Recording modes:**

- **Real-time recording**: Captures exact timing between actions
- **Manual timing**: User adds delays explicitly after recording
- **Smart timing**: Analyzes patterns and suggests optimal delays

**Use case:** Users unfamiliar with duckyScript syntax can create complex macros by demonstration. Also useful for quickly capturing repetitive workflows without manually writing duckyScript code.

---

## How to Contribute

If you'd like to implement any of these features:

1. Check if an issue already exists for the feature
2. Create a new issue to discuss the implementation approach
3. Submit a pull request with your implementation
4. Include documentation and examples
