"""Build execution preflight manifests and verify that required steps were accounted for."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ExperienceError(ValueError):
    """Raised when procedure or experience data is unsafe or malformed."""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ExperienceError(f"Cannot read JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ExperienceError(f"Expected JSON object: {path}")
    return value


def _resolve_procedure(procedure_path: Path, procedure_root: Path) -> Path:
    root = procedure_root.resolve()
    resolved = procedure_path.resolve()
    if not resolved.is_relative_to(root) or not resolved.is_dir():
        raise ExperienceError("Procedure must be a directory inside procedure root")
    for name in ("procedure.json", "execution-plan.json"):
        if not (resolved / name).is_file():
            raise ExperienceError(f"Procedure is missing {name}")
    return resolved


def _operational_steps(procedure: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = procedure.get("flow", {}).get("nodes", [])
    if not isinstance(nodes, list):
        raise ExperienceError("procedure.flow.nodes must be a list")
    steps: list[dict[str, Any]] = []
    seen: set[str] = set()
    for node in nodes:
        if not isinstance(node, dict) or node.get("type") in {"start", "end"}:
            continue
        step_id = node.get("id")
        if not isinstance(step_id, str) or not step_id or step_id in seen:
            raise ExperienceError("Every operational flow node needs a unique id")
        seen.add(step_id)
        steps.append(
            {
                "step_id": step_id,
                "label": node.get("label", step_id),
                "type": node.get("type", "action"),
                "description": node.get("description", ""),
                "required": node.get("required", True) is not False,
            }
        )
    if not steps:
        raise ExperienceError("Procedure has no operational steps")
    return steps


def _read_incidents(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    incidents: list[dict[str, Any]] = []
    warnings: list[str] = []
    if not path.is_file():
        return incidents, warnings
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not raw_line.strip():
            continue
        try:
            incident = json.loads(raw_line)
        except json.JSONDecodeError:
            warnings.append(f"invalid incident JSON at line {line_number}")
            continue
        if not isinstance(incident, dict) or not incident.get("step_id"):
            warnings.append(f"incident without step_id at line {line_number}")
            continue
        incidents.append(incident)
    return incidents, warnings


def _lesson_list(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    lessons = _read_json(path).get("lessons", [])
    return [item for item in lessons if isinstance(item, dict)] if isinstance(lessons, list) else []


def _context_values(procedure: dict[str, Any]) -> dict[str, set[str]]:
    context = procedure.get("experience_context", {})
    if not isinstance(context, dict):
        context = {}
    values: dict[str, set[str]] = {}
    for key in ("applications", "departments", "categories", "patterns"):
        raw = context.get(key, [])
        values[key] = {str(item).strip().casefold() for item in raw if str(item).strip()} if isinstance(raw, list) else set()
    values["departments"].add(str(procedure.get("department", "")).strip().casefold())
    values["categories"].add(str(procedure.get("category", "")).strip().casefold())
    values = {key: {item for item in items if item} for key, items in values.items()}
    return values


def _shared_lessons(
    procedure: dict[str, Any], shared_root: Path, warnings: list[str]
) -> list[dict[str, Any]]:
    if not shared_root.is_dir():
        return []
    context = _context_values(procedure)
    experience_context = procedure.get("experience_context", {})
    explicit_refs = {
        str(item).replace("\\", "/").removesuffix(".json")
        for item in experience_context.get("refs", [])
    } if isinstance(experience_context, dict) and isinstance(experience_context.get("refs", []), list) else set()
    selected: list[dict[str, Any]] = []
    for path in shared_root.glob("*/*.json"):
        try:
            document = _read_json(path)
        except ExperienceError:
            warnings.append(f"invalid shared experience file: {path.name}")
            continue
        reference = path.relative_to(shared_root).as_posix().removesuffix(".json")
        match = document.get("match", {})
        matched = reference in explicit_refs
        if isinstance(match, dict):
            for key, current in context.items():
                expected = match.get(key, [])
                if isinstance(expected, list) and current & {str(item).strip().casefold() for item in expected}:
                    matched = True
        if not matched:
            continue
        for lesson in document.get("lessons", []):
            if isinstance(lesson, dict):
                selected.append({"reference": reference, **lesson})
    return selected


def prepare_run(procedure_path: Path, procedure_root: Path) -> dict[str, Any]:
    procedure_dir = _resolve_procedure(procedure_path, procedure_root)
    procedure = _read_json(procedure_dir / "procedure.json")
    plan = _read_json(procedure_dir / "execution-plan.json")
    steps = _operational_steps(procedure)
    incidents, warnings = _read_incidents(procedure_dir / "experience" / "errors.jsonl")
    lessons = _lesson_list(procedure_dir / "experience" / "lessons.json")
    step_memory: dict[str, dict[str, list[dict[str, Any]]]] = {
        step["step_id"]: {"incidents": [], "lessons": []} for step in steps
    }
    procedure_lessons: list[dict[str, Any]] = []
    for incident in incidents:
        if incident["step_id"] in step_memory:
            step_memory[incident["step_id"]]["incidents"].append(incident)
        else:
            warnings.append(f"incident references unknown step_id: {incident['step_id']}")
    for lesson in lessons:
        step_ids = lesson.get("step_ids", [])
        if isinstance(step_ids, list) and step_ids:
            for step_id in step_ids:
                if step_id in step_memory:
                    step_memory[step_id]["lessons"].append(lesson)
                else:
                    warnings.append(f"lesson references unknown step_id: {step_id}")
        else:
            procedure_lessons.append(lesson)
    blocks = [
        {
            "block_id": block.get("id"),
            "executor": block.get("executor"),
            "side_effect": block.get("side_effect"),
        }
        for block in plan.get("blocks", [])
        if isinstance(block, dict)
    ]
    shared_root = procedure_root.resolve().parent / "experience"
    return {
        "schema_version": 1,
        "procedure": {
            "slug": procedure.get("slug"),
            "version": procedure.get("version"),
            "status": procedure.get("status"),
            "plan_status": plan.get("status"),
        },
        "required_steps": steps,
        "plan_blocks": blocks,
        "step_memory": step_memory,
        "procedure_lessons": procedure_lessons,
        "shared_lessons": _shared_lessons(procedure, shared_root, warnings),
        "coverage_contract": {
            "required_step_ids": [step["step_id"] for step in steps if step["required"]],
            "allowed_outcomes": ["succeeded", "failed", "skipped"],
            "skip_requires_reason": True,
        },
        "warnings": warnings,
    }


def validate_run_coverage(procedure_path: Path, run_path: Path, procedure_root: Path) -> dict[str, Any]:
    procedure_dir = _resolve_procedure(procedure_path, procedure_root)
    resolved_run = run_path.resolve()
    runs_root = (procedure_dir / "runs").resolve()
    if not resolved_run.is_relative_to(runs_root) or not resolved_run.is_file():
        raise ExperienceError("Run must be a JSON file inside the procedure runs directory")
    manifest = prepare_run(procedure_dir, procedure_root)
    run = _read_json(resolved_run)
    completed: set[str] = set()
    invalid_skips: list[str] = []
    for step in run.get("steps", []):
        if not isinstance(step, dict) or not step.get("step_id"):
            continue
        if step.get("outcome") == "skipped" and not str(step.get("skip_reason", "")).strip():
            invalid_skips.append(step["step_id"])
            continue
        if step.get("outcome") in {"succeeded", "failed", "skipped"}:
            completed.add(step["step_id"])
    required = set(manifest["coverage_contract"]["required_step_ids"])
    missing = sorted(required - completed)
    return {
        "valid": not missing and not invalid_skips,
        "missing_step_ids": missing,
        "invalid_skips": sorted(invalid_skips),
        "accounted_step_ids": sorted(completed),
    }
