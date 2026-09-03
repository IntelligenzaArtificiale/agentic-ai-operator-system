import json
import sys
import tempfile
import unittest
from pathlib import Path


RUNNER = Path(__file__).parents[1] / "atpa-v1" / "runtime" / "procedure-runner"
sys.path.insert(0, str(RUNNER))
from experience import ExperienceError, prepare_run, validate_run_coverage  # noqa: E402


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


class ExperienceRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.system_root = Path(self.temp.name)
        self.procedure_root = self.system_root / "procedure"
        self.procedure = self.procedure_root / "send-item"
        write_json(self.procedure / "procedure.json", {
            "slug": "send-item",
            "version": "1.0.0",
            "status": "validated",
            "department": "operations",
            "category": "communication",
            "experience_context": {
                "applications": ["Mail App"],
                "departments": [],
                "categories": [],
                "patterns": ["rich-text-editor"],
                "refs": [],
            },
            "flow": {"nodes": [
                {"id": "start", "type": "start"},
                {"id": "compose", "type": "action", "label": "Compose", "required": True},
                {"id": "verify", "type": "verification", "label": "Verify", "required": True},
            ]},
        })
        write_json(self.procedure / "execution-plan.json", {
            "status": "compiled",
            "blocks": [{"id": "compose", "executor": "deterministic", "side_effect": "external"}],
        })
        write_json(self.procedure / "experience" / "lessons.json", {
            "lessons": [{"lesson_id": "local", "step_ids": ["compose"]}],
        })
        errors = self.procedure / "experience" / "errors.jsonl"
        errors.write_text(
            json.dumps({"incident_id": "i1", "step_id": "compose"}) + "\n"
            + json.dumps({"incident_id": "invalid"}) + "\n",
            encoding="utf-8",
        )
        write_json(self.system_root / "experience" / "patterns" / "rich-text.json", {
            "id": "patterns/rich-text",
            "match": {"patterns": ["rich-text-editor"]},
            "lessons": [{"lesson_id": "shared", "status": "candidate"}],
        })

    def tearDown(self):
        self.temp.cleanup()

    def test_prepare_run_groups_memory_and_matches_shared_context(self):
        manifest = prepare_run(self.procedure, self.procedure_root)

        self.assertEqual([step["step_id"] for step in manifest["required_steps"]], ["compose", "verify"])
        self.assertEqual(manifest["step_memory"]["compose"]["incidents"][0]["incident_id"], "i1")
        self.assertEqual(manifest["step_memory"]["compose"]["lessons"][0]["lesson_id"], "local")
        self.assertEqual(manifest["shared_lessons"][0]["lesson_id"], "shared")
        self.assertTrue(any("without step_id" in warning for warning in manifest["warnings"]))

    def test_coverage_requires_every_step_or_a_reasoned_skip(self):
        run_path = self.procedure / "runs" / "run.json"
        write_json(run_path, {"steps": [{"step_id": "compose", "outcome": "succeeded"}]})
        missing = validate_run_coverage(self.procedure, run_path, self.procedure_root)
        self.assertFalse(missing["valid"])
        self.assertEqual(missing["missing_step_ids"], ["verify"])

        write_json(run_path, {"steps": [
            {"step_id": "compose", "outcome": "succeeded"},
            {"step_id": "verify", "outcome": "skipped", "skip_reason": "Not applicable in dry run"},
        ]})
        self.assertTrue(validate_run_coverage(self.procedure, run_path, self.procedure_root)["valid"])

    def test_paths_cannot_escape_procedure_root(self):
        with self.assertRaises(ExperienceError):
            prepare_run(self.system_root, self.procedure_root)

    def test_unrelated_malformed_shared_file_warns_without_blocking_run(self):
        invalid = self.system_root / "experience" / "software" / "broken.json"
        invalid.parent.mkdir(parents=True, exist_ok=True)
        invalid.write_text("{", encoding="utf-8")

        manifest = prepare_run(self.procedure, self.procedure_root)

        self.assertEqual(manifest["shared_lessons"][0]["lesson_id"], "shared")
        self.assertTrue(any("invalid shared experience" in warning for warning in manifest["warnings"]))


if __name__ == "__main__":
    unittest.main()
