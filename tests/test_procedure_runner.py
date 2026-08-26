import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

RUNNER = Path(__file__).parents[1] / "atpa-v1" / "runtime" / "procedure-runner"
sys.path.insert(0, str(RUNNER))
from engine import PlanError, ProcedureRunner, load_plan, validate_plan  # noqa: E402


class FakeDesktop:
    def __init__(self, width=1920, height=1080, window="Stable App"):
        self.calls = []
        self.size = SimpleNamespace(width=width, height=height)
        self.state = SimpleNamespace(
            active_window=SimpleNamespace(name=window),
            tree_state=SimpleNamespace(interactive_nodes=[], dom_informative_nodes=[]),
        )

    def get_screen_size(self): return self.size
    def get_state(self, **kwargs): self.calls.append(("state", kwargs)); return self.state
    def click(self, *args): self.calls.append(("click", args))
    def type(self, *args): self.calls.append(("type", args))
    def shortcut(self, *args): self.calls.append(("shortcut", args))
    def multi_edit(self, *args): self.calls.append(("multi_edit", args))
    def app(self, *args): self.calls.append(("app", args))


def plan(status="compiled", executor="deterministic", side_effect="none", guards=None):
    return {
        "schema_version": 1,
        "procedure_slug": "processo-test",
        "status": status,
        "variables": [{"name": "value"}],
        "environment": {"fingerprints": ["stable-test-environment"]},
        "blocks": [{
            "id": "work", "executor": executor, "side_effect": side_effect,
            "preconditions": guards if guards is not None else [
                {"kind": "screen_size", "equals": [1920, 1080]},
                {"kind": "active_window", "contains": "Stable App"},
            ], "postconditions": [],
            "actions": [] if executor == "ai" else [{"op": "type", "loc": [10, 20], "text": "{{value}}"}],
        }],
    }


class RunnerTests(unittest.TestCase):
    def test_fast_path_uses_only_guard_observation_then_local_action(self):
        desktop = FakeDesktop()
        result = ProcedureRunner(desktop).execute_block(plan(), "work", {"value": "dynamic"})
        self.assertEqual(result["outcome"], "succeeded")
        self.assertEqual([call[0] for call in desktop.calls], ["state", "type"])
        self.assertEqual(desktop.calls[1][1][1], "dynamic")

    def test_ai_and_unauthorized_external_blocks_halt(self):
        desktop = FakeDesktop()
        self.assertEqual(ProcedureRunner(desktop).execute_block(plan(executor="ai"), "work", {})["reason"], "cognitive_step")
        self.assertEqual(ProcedureRunner(desktop).execute_block(plan(side_effect="external"), "work", {"value": "x"})["reason"], "external_effect_not_authorized")
        self.assertFalse(desktop.calls)

    def test_guard_failure_prevents_action(self):
        desktop = FakeDesktop(width=1280)
        result = ProcedureRunner(desktop).execute_block(plan(guards=[{"kind": "screen_size", "equals": [1920, 1080]}]), "work", {"value": "x"})
        self.assertEqual(result["outcome"], "halted")
        self.assertFalse(any(call[0] == "type" for call in desktop.calls))

    def test_noncompiled_plan_halts(self):
        result = ProcedureRunner(FakeDesktop()).execute_block(plan(status="stabilizing"), "work", {"value": "x"})
        self.assertEqual(result["reason"], "plan_not_compiled")

    def test_unknown_slots_and_path_escape_are_rejected(self):
        invalid = plan()
        invalid["blocks"][0]["actions"][0]["text"] = "{{unknown}}"
        with self.assertRaises(PlanError): validate_plan(invalid)
        with tempfile.TemporaryDirectory() as parent:
            root = Path(parent) / "root"; root.mkdir()
            outside = Path(parent) / "execution-plan.json"
            outside.write_text(json.dumps(plan()), encoding="utf-8")
            with self.assertRaises(PlanError): load_plan(outside, root)

    def test_coordinate_actions_require_fingerprint_and_guards(self):
        invalid = plan()
        invalid["environment"]["fingerprints"] = []
        with self.assertRaisesRegex(PlanError, "fingerprints"):
            validate_plan(invalid)
        invalid = plan(guards=[])
        with self.assertRaisesRegex(PlanError, "screen_size"):
            validate_plan(invalid)


if __name__ == "__main__":
    unittest.main()
