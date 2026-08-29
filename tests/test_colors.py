#!/usr/bin/env python3
"""Tests for shared color utilities."""

import unittest
import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

from tools.shared.colors import get_available_colors


class ColorTests(unittest.TestCase):
    def test_available_colors_uses_supported_webcolors_api(self):
        colors = get_available_colors()

        self.assertEqual(colors, sorted(colors))
        self.assertIn("red", colors)


if __name__ == "__main__":
    unittest.main()