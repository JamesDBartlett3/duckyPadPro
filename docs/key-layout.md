# duckyPad Pro Key Layout Reference

This document provides a visual reference for the physical layout and numbering of keys on the duckyPad Pro in both portrait and landscape orientations.

## Key Numbering Fundamentals

- Keys are numbered **1-20** in a fixed sequence
- Numbering is always **left-to-right, top-to-bottom** in portrait mode
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
- What was the **bottom row** in portrait becomes the **left column** in landscape
- What was the **top row** in portrait becomes the **right column** in landscape

## Key Constraints

### Key Label Limitations
- **Maximum 2 lines** of text per key label
- **Maximum 5 characters** per line (ASCII only)
- Total: 10 characters maximum per key label

All helper tools and profile designs must respect this constraint when creating key labels.
