# duckyPad Pro Key Layout Reference

This document provides a visual reference for the physical layout and numbering of keys on the duckyPad Pro in both portrait and landscape orientations.

> **For Developers**: Python scripts can use the centralized [`helpers/shared/key_layout.py`](../helpers/shared/key_layout.py) module which provides these diagrams, key descriptions, and utility functions for working with key layouts programmatically.

## Key Numbering Fundamentals

- Physical keys are numbered **1-20** in a fixed sequence (4×5 grid)
- Rotary encoder inputs are numbered **21-26** (2 encoders × 3 inputs each)
- Numbering is always **left-to-right, top-to-bottom** in portrait mode (for physical keys)
- Key numbering **does not change** when rotating orientation
- The physical device rotates 90° counterclockwise for landscape mode
- Keys stay in their physical positions; orientation only changes how rows/columns are interpreted

## Portrait Mode (4 columns × 5 rows)

Key 1 is at the **top-left**, key 20 is at the **bottom-right**.

```
┌────┬────┬────┬────┐
│  1 │  2 │  3 │  4 │  ← Top Row
├────┼────┼────┼────┤
│  5 │  6 │  7 │  8 │
├────┼────┼────┼────┤
│  9 │ 10 │ 11 │ 12 │
├────┼────┼────┼────┤
│ 13 │ 14 │ 15 │ 16 │
├────┼────┼────┼────┤
│ 17 │ 18 │ 19 │ 20 │  ← Bottom Row
└────┴────┴────┴────┘
 ↑              ↑
Left          Right
Column        Column
```

### Portrait Mode - Row/Column Reference

**Rows:**
- Row 1 (Top): Keys 1, 2, 3, 4
- Row 2: Keys 5, 6, 7, 8
- Row 3: Keys 9, 10, 11, 12
- Row 4: Keys 13, 14, 15, 16
- Row 5 (Bottom): Keys 17, 18, 19, 20

**Columns:**
- Column 1 (Left): Keys 1, 5, 9, 13, 17
- Column 2: Keys 2, 6, 10, 14, 18
- Column 3: Keys 3, 7, 11, 15, 19
- Column 4 (Right): Keys 4, 8, 12, 16, 20

## Landscape Mode (5 columns × 4 rows)

After 90° CCW rotation, key 1 is at the **bottom-left**, key 20 is at the **top-right**.

```
┌────┬────┬────┬────┬────┐
│  4 │  8 │ 12 │ 16 │ 20 │  ← Top Row
├────┼────┼────┼────┼────┤
│  3 │  7 │ 11 │ 15 │ 19 │
├────┼────┼────┼────┼────┤
│  2 │  6 │ 10 │ 14 │ 18 │
├────┼────┼────┼────┼────┤
│  1 │  5 │  9 │ 13 │ 17 │  ← Bottom Row
└────┴────┴────┴────┴────┘
 ↑                    ↑
Left                Right
Column              Column
```

### Landscape Mode - Row/Column Reference

**Rows:**
- Row 1 (Top): Keys 4, 8, 12, 16, 20
- Row 2: Keys 3, 7, 11, 15, 19
- Row 3: Keys 2, 6, 10, 14, 18
- Row 4 (Bottom): Keys 1, 5, 9, 13, 17

**Columns:**
- Column 1 (Left): Keys 1, 2, 3, 4
- Column 2: Keys 5, 6, 7, 8
- Column 3: Keys 9, 10, 11, 12
- Column 4: Keys 13, 14, 15, 16
- Column 5 (Right): Keys 17, 18, 19, 20

## Orientation Comparison

| Position | Portrait Mode | Landscape Mode |
|----------|---------------|----------------|
| Top-left | Key 1 | Key 4 |
| Top-right | Key 4 | Key 20 |
| Bottom-left | Key 17 | Key 1 |
| Bottom-right | Key 20 | Key 17 |
| Physical top row | Keys 1-4 | Keys 4, 8, 12, 16, 20 |
| Physical bottom row | Keys 17-20 | Keys 1, 5, 9, 13, 17 |
| Physical left column | Keys 1, 5, 9, 13, 17 | Keys 1, 2, 3, 4 |
| Physical right column | Keys 4, 8, 12, 16, 20 | Keys 17, 18, 19, 20 |

## Understanding the Rotation

When you rotate from portrait to landscape (90° CCW):
- What was the **right column** in portrait becomes the **top row** in landscape
- What was the **left column** in portrait becomes the **bottom row** in landscape
- What was the **bottom row** in portrait becomes the **right column** in landscape
- What was the **top row** in portrait becomes the **left column** in landscape

## Rotary Encoders (Keys 21-26)

In addition to the 20 physical keys in the 4×5 grid, the duckyPad Pro includes **two rotary encoders** with three inputs each:

### First Rotary Encoder (Keys 21-23)
- **Key 21**: Clockwise rotation
- **Key 22**: Counter-clockwise rotation
- **Key 23**: Press/click

### Second Rotary Encoder (Keys 24-26)
- **Key 24**: Clockwise rotation
- **Key 25**: Counter-clockwise rotation
- **Key 26**: Press/click

### Physical Position

**Portrait Mode (4×5 grid):**
- Rotary encoders are on the **right side** of the device
- First encoder: Upper position (keys 21-23)
- Second encoder: Lower position (keys 24-26)

**Landscape Mode (5×4 grid after 90° CCW rotation):**
- Rotary encoders are on the **top side** of the device
- First encoder: Left position (keys 21-23)
- Second encoder: Right position (keys 24-26)

### Naming Convention

The encoders are referred to as "first" and "second" rather than "top/bottom" or "left/right" because:
- Their relative position changes with device orientation
- Using ordinal names (first/second) maintains consistency across orientations
- Physical rotation of the device doesn't change which encoder is "first"

### Common Use Cases

**Volume Control:**
```
REM key21.txt - Volume Up
MEDIA_VOLUME_UP

REM key22.txt - Volume Down
MEDIA_VOLUME_DOWN

REM key23.txt - Mute
MEDIA_MUTE
```

**Scrolling:**
```
REM key24.txt - Scroll Down
DOWN
DOWN
DOWN

REM key25.txt - Scroll Up
UP
UP
UP

REM key26.txt - Page Select
ENTER
```

**Profile Switching:**
```
REM key21.txt - Next Profile
FUNCTION_KEY NEXT_PROFILE

REM key22.txt - Previous Profile
FUNCTION_KEY PREV_PROFILE

REM key23.txt - Return to Main
FUNCTION_KEY PROFILE 1
```

## Key Constraints

### Key Label Limitations
- **Maximum 2 lines** of text per key label
- **Maximum 5 characters** per line (ASCII only)
- Total: 10 characters maximum per key label

All helper tools and profile designs must respect this constraint when creating key labels.
