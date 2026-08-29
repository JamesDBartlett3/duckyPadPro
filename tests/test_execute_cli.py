#!/usr/bin/env python3
"""Tests for concise execute.py command routing."""

import io
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

import execute


class ExecuteCliTests(unittest.TestCase):
    def run_yaml_command(self, argv):
        with patch.object(execute, "cmd_yaml", return_value=0) as command:
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(execute.main(argv), 0)
        return command.call_args.args[0]

    def test_bare_yaml_runs_full_workflow(self):
        args = self.run_yaml_command(["profile.yaml"])

        self.assertEqual(args.command, "yaml")
        self.assertFalse(args.generate_only)
        self.assertFalse(args.compile_only)
        self.assertFalse(args.skip_deploy)

    def test_bare_yml_is_inferred_case_insensitively(self):
        args = self.run_yaml_command(["profile.YML"])

        self.assertEqual(args.yaml_file, Path("profile.YML"))

    def test_generate_runs_generation_only(self):
        args = self.run_yaml_command(["generate", "profile.yaml"])

        self.assertTrue(args.generate_only)
        self.assertFalse(args.compile_only)

    def test_compile_yaml_generates_and_compiles(self):
        args = self.run_yaml_command(["compile", "profile.yaml"])

        self.assertFalse(args.generate_only)
        self.assertTrue(args.compile_only)

    def test_compile_directory_keeps_existing_behavior(self):
        with patch.object(execute, "compile_profiles", return_value=0) as compile_profiles:
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(execute.main(["compile", "profiles/example"]), 0)

        compile_profiles.assert_called_once_with(
            profile_path=Path("profiles/example"),
            verbose=False,
            resolve_profiles=True,
        )

    def test_legacy_generate_only_syntax_remains_supported(self):
        args = self.run_yaml_command(["yaml", "profile.yaml", "--generate-only"])

        self.assertTrue(args.generate_only)


if __name__ == "__main__":
    unittest.main()