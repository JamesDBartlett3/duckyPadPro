# Getting Started with duckyPad Pro

This guide will help you get started with using the profiles and scripts in this repository with your duckyPad Pro device.

## Prerequisites

- duckyPad Pro device
- USB cable or SD card for file transfer
- Basic understanding of your operating system (Windows, macOS, or Linux)

## Installing a Profile

1. **Download** the profile you want to use from the `profiles/` directory
2. **Connect** your duckyPad Pro to your computer via USB or remove the SD card
3. **Copy** the profile folder to the appropriate location on your device
4. **Eject** the device safely or insert the SD card back
5. **Select** the profile from your duckyPad Pro menu

## Using Standalone Scripts

Standalone scripts from the `scripts/` directory can be used in several ways:

### Option 1: Add to an Existing Profile

1. Copy the script content
2. Paste it into one of your profile's key files (e.g., `key1.txt`)
3. Save and sync to your device

### Option 2: Create a New Profile

1. Create a new profile directory
2. Add a `config.txt` file
3. Copy scripts to key files
4. Add to your device

### Option 3: Use Helper Tools

Use the profile generator helper to create a new profile structure:

```bash
cd helpers/generators
python profile_generator.py my-custom-profile 8
```

## Customizing Scripts

duckyScript is highly customizable. Here are some tips:

### Adjusting Delays

If commands aren't executing reliably, increase the delay values:

```
DELAY 100   # Short delay
DELAY 500   # Medium delay
DELAY 1000  # Long delay (1 second)
```

### Platform-Specific Keys

Different operating systems use different modifier keys:

**macOS:**
- `COMMAND` for CMD/⌘
- `OPTION` for ALT/⌥
- `CONTROL` for CTRL

**Windows/Linux:**
- `CONTROL` for CTRL
- `ALT` for ALT
- `WINDOWS` or `GUI` for Windows key

### Testing Scripts

1. Start with simple scripts to verify functionality
2. Test each key individually
3. Adjust delays as needed
4. Document any platform-specific requirements

## Helper Utilities

The `helpers/` directory contains useful tools:

### Text to DuckyScript Converter

Convert plain text files to duckyScript:

```bash
cd helpers/converters
python text_to_duckyscript.py input.txt output.txt
```

### Profile Generator

Generate a new profile structure:

```bash
cd helpers/generators
python profile_generator.py profile-name 8
```

## Troubleshooting

### Scripts Not Executing

- **Increase delays**: Add more time between commands
- **Check focus**: Ensure the target application has focus
- **Verify syntax**: Check for typos in duckyScript commands

### Wrong Keys Pressed

- **Platform differences**: Verify modifier keys match your OS
- **Keyboard layout**: Check your system keyboard layout
- **Update scripts**: Adjust key combinations as needed

### Device Not Recognized

- **Check connection**: Ensure USB cable is properly connected
- **Try different port**: Use a different USB port
- **Restart device**: Power cycle your duckyPad Pro

## Next Steps

- Explore the [profiles](../profiles/README.md) directory for ready-to-use profiles
- Browse [scripts](../scripts/README.md) for standalone automations
- Check out [helpers](../helpers/README.md) for useful utilities
- Read the [duckyScript documentation](https://dekunukem.github.io/duckyPad-Pro/doc/duckyscript_info.html)

## Getting Help

- Check the [duckyPad Pro documentation](https://dekunukem.github.io/duckyPad-Pro/)
- Review example profiles and scripts in this repository
- Submit an issue if you find problems
