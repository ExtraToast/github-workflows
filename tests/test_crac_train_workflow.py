from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CRAC_WORKFLOW = ROOT / ".github/workflows/crac-train.yml"
COMPOSE_ACTION = ROOT / "actions/compose-system-test-stack/action.yml"
README = ROOT / "README.md"


class CracTrainWorkflowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = CRAC_WORKFLOW.read_text(encoding="utf-8")
        cls.compose_action = COMPOSE_ACTION.read_text(encoding="utf-8")
        cls.readme = README.read_text(encoding="utf-8")
        match = re.search(
            r"python3 - <<'PY' >> \"\$GITHUB_OUTPUT\"\n(?P<body>.*?)\n          PY",
            cls.workflow,
            re.DOTALL,
        )
        if match is None:
            raise AssertionError("Could not find embedded CRaC sidecar resolver.")
        cls.sidecar_resolver = textwrap.dedent(match.group("body"))

    def resolve_sidecars(self, sidecars_json: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory():
            env = os.environ.copy()
            env["SIDECARS_JSON"] = sidecars_json
            result = subprocess.run(
                [sys.executable, "-c", self.sidecar_resolver],
                env=env,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            return result

    def test_missing_sidecars_defaults_to_round_two_topology(self) -> None:
        result = self.resolve_sidecars("null")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("postgres=true\n", result.stdout)
        self.assertIn("valkey=true\n", result.stdout)
        self.assertIn("rabbitmq=true\n", result.stdout)
        self.assertIn("list=postgres,valkey,rabbitmq\n", result.stdout)

    def test_sidecars_accepts_subset_list(self) -> None:
        result = self.resolve_sidecars('["postgres", "valkey"]')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("postgres=true\n", result.stdout)
        self.assertIn("valkey=true\n", result.stdout)
        self.assertIn("rabbitmq=false\n", result.stdout)
        self.assertIn("list=postgres,valkey\n", result.stdout)

    def test_sidecars_support_explicit_none_and_reject_mixed_none(self) -> None:
        result = self.resolve_sidecars('"none"')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("postgres=false\n", result.stdout)
        self.assertIn("valkey=false\n", result.stdout)
        self.assertIn("rabbitmq=false\n", result.stdout)
        self.assertIn("list=none\n", result.stdout)

        empty_result = self.resolve_sidecars("[]")
        self.assertEqual(empty_result.returncode, 0, empty_result.stderr)
        self.assertIn("list=none\n", empty_result.stdout)

        mixed_result = self.resolve_sidecars('["none", "postgres"]')
        self.assertNotEqual(mixed_result.returncode, 0)
        self.assertIn("value 'none' cannot be combined with other sidecars", mixed_result.stderr)

    def test_only_supported_sidecar_names_are_accepted(self) -> None:
        result = self.resolve_sidecars('["postgres", "search"]')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unsupported CRaC sidecar(s): search", result.stderr)

    def test_job_services_are_not_started_unconditionally(self) -> None:
        services_block = re.search(r"\n    services:\n", self.workflow)
        self.assertIsNone(services_block)
        self.assertIn("Start Postgres sidecar", self.workflow)
        self.assertIn("Start Valkey sidecar", self.workflow)
        self.assertIn("Start RabbitMQ sidecar", self.workflow)

    def test_training_env_vars_are_conditional(self) -> None:
        self.assertIn('if [ "$POSTGRES_ENABLED" = "true" ]; then', self.workflow)
        self.assertIn('if [ "$VALKEY_ENABLED" = "true" ]; then', self.workflow)
        self.assertIn('if [ "$RABBITMQ_ENABLED" = "true" ]; then', self.workflow)

    def test_readme_documents_sidecar_matrix_examples(self) -> None:
        self.assertIn('"sidecars": ["postgres", "valkey"]', self.readme)
        self.assertIn('"sidecars": "none"', self.readme)

    def test_compose_action_is_design_first_placeholder(self) -> None:
        expected_inputs = [
            "compose-files",
            "services",
            "wait-strategy",
            "diagnostics-command",
            "migration-check-command",
            "placeholder-ack",
        ]
        for expected_input in expected_inputs:
            self.assertIn(f"  {expected_input}:", self.compose_action)

        self.assertIn("design-first skeleton", self.compose_action)
        self.assertIn('PLACEHOLDER_ACK: ${{ inputs.placeholder-ack }}', self.compose_action)


if __name__ == "__main__":
    unittest.main()
