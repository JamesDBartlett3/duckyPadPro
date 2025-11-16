#!/usr/bin/env python3
"""
Text to DuckyScript Converter

This helper script converts plain text into duckyScript STRING commands.
Useful for creating scripts that type out predefined text.

Usage:
    python text_to_duckyscript.py input.txt output.txt
    
Example:
    Input: "Hello World"
    Output: STRING Hello World
"""

import sys


def convert_text_to_duckyscript(input_text, add_delays=False):
    """
    Convert text to duckyScript format.
    
    Args:
        input_text: The text to convert
        add_delays: Whether to add DELAY commands between lines
        
    Returns:
        duckyScript formatted string
    """
    lines = input_text.strip().split('\n')
    output = []
    
    for i, line in enumerate(lines):
        if line.strip():  # Skip empty lines
            output.append(f"STRING {line}")
            if i < len(lines) - 1:  # Not the last line
                output.append("ENTER")
                if add_delays:
                    output.append("DELAY 100")
    
    return '\n'.join(output)


def main():
    if len(sys.argv) < 3:
        print("Usage: python text_to_duckyscript.py input.txt output.txt")
        print("Options: Add --delays to include delay commands")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    add_delays = '--delays' in sys.argv
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            input_text = f.read()
        
        output_text = convert_text_to_duckyscript(input_text, add_delays)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_text)
        
        print(f"Successfully converted {input_file} to {output_file}")
        
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
