"""Validate and execute safe, declarative desktop action blocks."""

from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any, Callable


TERMINAL_PLAN_STATES = {"compiled", "degraded"}
ALLOWED_PLAN_STATES = {
    "exploratory",
    "stabilizing",
    "compiled_candidate",
    *TERMINAL_PLAN_STATES,
}
ALLOWED_OPERATIONS = {
    "app",
    "click",
    "multi_edit",
    "shortcut",
    "type",
    "wait",
    "wait_for",
}
EXTERNAL_EFFECTS = {"external", "destructive"}
SLOT_PATTERN = re.compile(r"\{\{([a-z][a-z0-9_]*)\}\}")


class PlanError(ValueError):
    """Raised when a compiled plan is invalid or unsafe to execute."""


class GuardFailed(RuntimeError):
    """Raised when the desktop no longer matches a compiled assumption."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PlanError(message)


def _render(value: Any, variables: dict[str, Any]) -> Any:
    if isinstance(value, str):
        def replace(match: re.Match[str]) -> str:
            name = match.group(1)
            if name not in variables:
                raise PlanError(f"Missing variable: {name}")
            return str(variables[name])

        return SLOT_PATTERN.sub(replace, value)
    if isinstance(value, list):
        return [_render(item, variables) for item in value]
    if isinstance(value, dict):
        return {key: _render(item, variables) for key, item in value.items()}
    return value


def load_plan(plan_path: Path, procedure_root: Path) -> dict[str, Any]:
    resolved_plan = plan_path.resolve()
    resolved_root = procedure_root.resolve()
    _require(resolved_plan.is_relative_to(resolved_root), "Plan must stay inside procedure root")
    _require(resolved_plan.name == "execution-plan.json", "Expected execution-plan.json")
    _require(resolved_plan.is_file(), f"Plan does not exist: {resolved_plan}")
    plan = json.loads(resolved_plan.read_text(encoding="utf-8"))
    validate_plan(plan)
    return plan


def validate_plan(plan: dict[str, Any]) -> None:
    _require(plan.get("schema_version") == 1, "Unsupported plan schema")
    _require(bool(plan.get("procedure_slug")), "procedure_slug is required")
    _require(plan.get("status") in ALLOWED_PLAN_STATES, "Invalid plan status")
    _require(isinstance(plan.get("variables"), list), "variables must be a list")
    _require(isinstance(plan.get("blocks"), list), "blocks must be a list")
    variable_names = {item.get("name") for item in plan["variables"]}
    _require(None not in variable_names, "Every variable needs a name")
    block_ids: set[str] = set()
    for block in plan["blocks"]:
        block_id = block.get("id")
        _require(bool(block_id) and block_id not in block_ids, "Block ids must be unique")
        block_ids.add(block_id)
        _require(block.get("executor") in {"deterministic", "ai"}, f"Invalid executor: {block_id}")
        _require(
            block.get("side_effect") in {"none", "reversible", "external", "destructive"},
            f"Invalid side_effect: {block_id}",
        )
        actions = block.get("actions", [])
        _require(isinstance(actions, list), f"actions must be a list: {block_id}")
        if block["executor"] == "ai":
            _require(not actions, f"AI block cannot contain deterministic actions: {block_id}")
        coordinate_ops = {action.get("op") for action in actions} & {"click", "type", "multi_edit"}
        if coordinate_ops:
            fingerprints = plan.get("environment", {}).get("fingerprints", [])
            guard_kinds = {guard.get("kind") for guard in block.get("preconditions", [])}
            _require(bool(fingerprints), f"Coordinate actions require fingerprints: {block_id}")
            _require(
                {"screen_size", "active_window"} <= guard_kinds,
                f"Coordinate actions require screen_size and active_window guards: {block_id}",
            )
        for action in actions:
            _require(action.get("op") in ALLOWED_OPERATIONS, f"Invalid operation in {block_id}")
            rendered_slots = set(SLOT_PATTERN.findall(json.dumps(action)))
            _require(rendered_slots <= variable_names, f"Unknown variables in {block_id}")


class ProcedureRunner:
    """Runs one compiled block and returns structured local telemetry."""

    def __init__(self, desktop: Any, sleep: Callable[[float], None] = time.sleep):
        self.desktop = desktop
        self.sleep = sleep

    def execute_block(
        self,
        plan: dict[str, Any],
        block_id: str,
        variables: dict[str, Any],
        allow_external_effects: bool = False,
    ) -> dict[str, Any]:
        block = next((item for item in plan["blocks"] if item["id"] == block_id), None)
        if block is None:
            raise PlanError(f"Unknown block: {block_id}")
        if plan["status"] != "compiled":
            return self._halt(block_id, "plan_not_compiled", requires_ai=True)
        if block["executor"] == "ai":
            return self._halt(block_id, "cognitive_step", requires_ai=True)
        if block["side_effect"] in EXTERNAL_EFFECTS and not allow_external_effects:
            return self._halt(block_id, "external_effect_not_authorized", requires_ai=True)

        started = time.perf_counter()
        action_results: list[dict[str, Any]] = []
        try:
            self._check_guards(block.get("preconditions", []))
            for index, raw_action in enumerate(block.get("actions", [])):
                action = _render(raw_action, variables)
                action_started = time.perf_counter()
                self._execute_action(action)
                action_results.append(
                    {
                        "index": index,
                        "op": action["op"],
                        "duration_ms": round((time.perf_counter() - action_started) * 1000),
                    }
                )
            self._check_guards(block.get("postconditions", []))
        except (GuardFailed, PlanError, OSError, RuntimeError) as exc:
            return {
                "outcome": "halted",
                "block_id": block_id,
                "reason": str(exc),
                "requires_ai": True,
                "duration_ms": round((time.perf_counter() - started) * 1000),
                "actions": action_results,
            }
        return {
            "outcome": "succeeded",
            "block_id": block_id,
            "requires_ai": False,
            "duration_ms": round((time.perf_counter() - started) * 1000),
            "actions": action_results,
        }

    @staticmethod
    def _halt(block_id: str, reason: str, requires_ai: bool) -> dict[str, Any]:
        return {
            "outcome": "halted",
            "block_id": block_id,
            "reason": reason,
            "requires_ai": requires_ai,
            "duration_ms": 0,
            "actions": [],
        }

    def _check_guards(self, guards: list[dict[str, Any]]) -> None:
        for guard in guards:
            kind = guard.get("kind")
            if kind == "screen_size":
                size = self.desktop.get_screen_size()
                actual = [size.width, size.height]
                if actual != guard.get("equals"):
                    raise GuardFailed(f"screen_size mismatch: {actual}")
                continue
            state = self.desktop.get_state(
                use_vision=False,
                use_dom=bool(guard.get("use_dom", False)),
                use_ui_tree=True,
                use_annotation=False,
            )
            if kind == "active_window":
                actual = getattr(getattr(state, "active_window", None), "name", "")
                if guard.get("contains", "").casefold() not in actual.casefold():
                    raise GuardFailed(f"active_window mismatch: {actual}")
            elif kind in {"text_exists", "element_exists"}:
                expected = guard.get("contains", "").casefold()
                text = self._state_text(state, include_all=kind == "text_exists")
                if expected not in text.casefold():
                    raise GuardFailed(f"{kind} missing: {guard.get('contains', '')}")
            else:
                raise PlanError(f"Unsupported guard: {kind}")

    @staticmethod
    def _state_text(state: Any, include_all: bool) -> str:
        tree = getattr(state, "tree_state", None)
        nodes = [] if tree is None else list(getattr(tree, "interactive_nodes", []))
        if include_all and tree is not None:
            nodes += list(getattr(tree, "dom_informative_nodes", []))
        return "\n".join(
            str(getattr(node, "name", "") or getattr(node, "text", "")) for node in nodes
        )

    def _execute_action(self, action: dict[str, Any]) -> None:
        op = action["op"]
        if op == "click":
            self.desktop.click(action["loc"], action.get("button", "left"), action.get("clicks", 1))
        elif op == "type":
            self.desktop.type(
                tuple(action["loc"]),
                action.get("text", ""),
                action.get("caret_position", "idle"),
                action.get("clear", False),
                action.get("press_enter", False),
            )
        elif op == "shortcut":
            self.desktop.shortcut(action["keys"])
        elif op == "wait":
            self.sleep(float(action["seconds"]))
        elif op == "multi_edit":
            self.desktop.multi_edit([tuple(item) for item in action["items"]])
        elif op == "app":
            self._execute_app(action)
        elif op == "wait_for":
            self._wait_for(action)
        else:
            raise PlanError(f"Unsupported operation: {op}")

    def _execute_app(self, action: dict[str, Any]) -> None:
        mode = action.get("mode", "launch")
        if mode == "launch_executable":
            executable = Path(action["executable"]).expanduser().resolve()
            if not executable.is_file():
                raise PlanError(f"Executable not found: {executable}")
            subprocess.Popen(
                [str(executable), *action.get("args", [])],
                cwd=action.get("cwd"),
                shell=False,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                close_fds=True,
            )
            return
        self.desktop.app(
            mode,
            action.get("name"),
            action.get("window_loc"),
            action.get("window_size"),
        )

    def _wait_for(self, action: dict[str, Any]) -> None:
        deadline = time.perf_counter() + float(action.get("timeout", 10))
        guard = action["guard"]
        while True:
            try:
                self._check_guards([guard])
                return
            except GuardFailed:
                if time.perf_counter() >= deadline:
                    raise GuardFailed(f"wait_for timed out: {guard}")
                self.sleep(float(action.get("interval", 0.25)))
