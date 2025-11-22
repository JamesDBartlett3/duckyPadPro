# Profile Info Ordinal Number Mapping Tasks

## Background

The official duckyPad Configurator handles `GOTO_PROFILE {ProfileName}` commands by:

1. Reading `profile_info.txt` from the SD card root
2. Building a profile name → ordinal number mapping
3. Temporarily replacing profile names with numbers during compilation
4. Leaving the original source code unchanged (still contains profile names)

## Implementation Tasks

### 1. Locate the SD Card

Auto-detect duckyPad SD card across operating systems:

**Windows:**

- Check `D:\`, `E:\`, `F:\`, etc. for removable drives
- Look for `profile_info.txt` in root

**macOS:**

- Check `/Volumes/*` directories
- Look for `profile_info.txt` in root

**Linux:**

- Check `/media/*` and `/mnt/*` directories
- Look for `profile_info.txt` in root

**Fallback:**

- Prompt user to provide filesystem path if auto-detection fails
- Store user-provided path for future sessions

### 2. Parse profile_info.txt

Format example:

```
1 Welcome
2 Firefox
3 Chrome
4 OBS
5 WASD
6 Numpad
7 Autohotkey
8 MS Teams
9 duckyScript
10 Foxhole
11 Foxhole-Ctrl
12 EliteDangerous
```

Build mapping dictionary:

```python
{
    'Welcome': 0,        # profile1 = index 0
    'Firefox': 1,        # profile2 = index 1
    'Chrome': 2,         # profile3 = index 2
    'OBS': 3,
    'WASD': 4,
    'Numpad': 5,
    'Autohotkey': 6,
    'MS Teams': 7,
    'duckyScript': 8,
    'Foxhole': 9,
    'Foxhole-Ctrl': 10,  # profile11 = index 10
    'EliteDangerous': 11
}
```

**Note:** Profile number N maps to index N-1 (profile1 → index 0)

### 3. Hot-Swap During Compilation

**Process:**

1. Read original `.txt` file content
2. Find all `GOTO_PROFILE {ProfileName}` commands using regex
3. Look up profile name in mapping dictionary
4. Replace with `GOTO_PROFILE {number}` in memory
5. Pass modified content to `make_bytecode.py` (via stdin or temp file)
6. Keep original `.txt` file unchanged
7. Write compiled `.dsb` output

**Example transformation:**

```
Original:    GOTO_PROFILE Foxhole-Ctrl
In-memory:   GOTO_PROFILE 10
Compiled:    [bytecode with index 10]
File stays:  GOTO_PROFILE Foxhole-Ctrl
```

### 4. Error Handling

**Profile not found:**

- Warn user that profile name doesn't exist in `profile_info.txt`
- List available profile names from mapping
- Skip compilation of that file

**SD card not found:**

- Provide clear error message
- Show where auto-detection looked
- Prompt for manual path or offer to compile without name resolution

**profile_info.txt missing:**

- Warn that name-based GOTO_PROFILE won't work
- Suggest using numeric indices instead
- Offer to continue with numeric-only mode

### 5. Caching Strategy

**Session cache:**

- Load `profile_info.txt` once per compilation session
- Cache mapping dictionary in memory
- Reload only if file timestamp changes

**Persistent cache:**

- Remember SD card path across sessions (optional)
- Store in user config file (e.g., `~/.duckypad/config.json`)

### 6. Integration Points

**Compiler script updates needed:**

- Add SD card detection logic
- Add profile_info.txt parser
- Add regex-based name replacement
- Update compilation flow to use in-memory content
- Add verbose logging for debugging

**Generator script considerations:**

- `yaml_to_profile.py` can continue using profile names
- No need for `-i` flag when SD card is available
- Keep `-i` flag as fallback for offline compilation

### 7. User Experience

**Success flow:**

1. User runs compiler
2. Script auto-detects SD card
3. Loads profile mapping
4. Compiles with profile names → works seamlessly

**Manual flow:**

1. Script can't find SD card
2. Prompts: "Enter duckyPad SD card path (or press Enter to skip):"
3. User provides path or skips
4. Continues with appropriate mode

### 8. Testing Scenarios

- [ ] Windows with SD card on E:\
- [ ] macOS with SD card in /Volumes/
- [ ] Linux with SD card in /media/
- [ ] SD card not connected (fallback to numeric mode)
- [ ] profile_info.txt missing from SD card
- [ ] Profile name not in mapping
- [ ] Profile name with spaces (e.g., "MS Teams")
- [ ] Profile name with hyphens (e.g., "Foxhole-Ctrl")
- [ ] Multiple GOTO_PROFILE commands in one file
- [ ] Mixed numeric and name-based GOTO_PROFILE commands

## Implementation Order

1. **First:** Refactor PowerShell scripts to Python (separate task)
2. **Then:** Implement SD card detection
3. **Then:** Implement profile_info.txt parser
4. **Then:** Implement hot-swap compilation
5. **Then:** Add error handling and user prompts
6. **Finally:** Add caching and session management

## Notes

- This feature makes duckyScript source files more readable (names vs numbers)
- Maintains compatibility with official duckyPad Configurator
- No changes needed to `make_bytecode.py` itself
- All transformations happen before bytecode compilation
- Original source files remain human-readable
