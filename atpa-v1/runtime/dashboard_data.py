"""Read-only dashboard projection. No app control, licensing secrets or shell calls."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path

TERMINAL = {"succeeded", "failed", "unverified", "cancelled"}


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0


def timestamp(value):
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed.replace(tzinfo=timezone.utc).timestamp() if parsed.tzinfo is None else parsed.timestamp()
    except (ValueError, TypeError, OverflowError):
        return 0


def read_object(path, warnings):
    try:
        if path.is_symlink() or path.stat().st_size > 8_000_000:
            raise ValueError("unsupported file")
        value = json.loads(path.read_text(encoding="utf-8-sig"))
        if not isinstance(value, dict):
            raise ValueError("expected object")
        return value
    except (OSError, ValueError, RecursionError):
        warnings.append(f"File non leggibile o non valido: {path.name}")
        return None


def run_time(run):
    return timestamp(run.get("finished_at") or run.get("ended_at") or run.get("started_at"))


def verified(run):
    return run.get("outcome") == "succeeded" and run.get("verification_status") == "verified"


def summary(run):
    outcome = run.get("outcome", "unknown")
    if outcome == "succeeded" and not verified(run):
        outcome = "unverified"
    return {"run_id": str(run.get("run_id", "")), "outcome": outcome,
            "at": run.get("finished_at") or run.get("ended_at") or run.get("started_at"),
            "duration_ms": run.get("duration_ms") if number(run.get("duration_ms")) else None}


def metrics(runs, incidents):
    completed = sorted((run for run in runs if run.get("outcome") in TERMINAL), key=run_time)
    clean = [run for run in completed if verified(run) and number(run.get("duration_ms"))]
    values = [run["duration_ms"] for run in clean]
    samples = {}
    for run in clean:
        for step in run.get("steps", []) if isinstance(run.get("steps"), list) else []:
            if not isinstance(step, dict) or not number(step.get("duration_ms")):
                continue
            key = str(step.get("step_id") or step.get("label") or "Step")
            entry = samples.setdefault(key, {"label": str(step.get("label") or key), "values": []})
            entry["values"].append(step["duration_ms"])
    slow = [{"step_id": key, "label": entry["label"], "samples": len(entry["values"]),
             "average_duration_ms": round(sum(entry["values"]) / len(entry["values"]))}
            for key, entry in samples.items()]
    def total(key):
        return sum(run.get("metrics", {}).get(key, 0) for run in completed
                   if isinstance(run.get("metrics"), dict) and number(run["metrics"].get(key)))
    dated = [run for run in completed if run_time(run)]
    dated_clean = [run for run in clean if run_time(run)]
    return {"run_count": len(completed), "successful_runs": sum(verified(r) for r in completed),
            "failed_runs": sum(r.get("outcome") == "failed" for r in completed),
            "unverified_runs": sum(summary(r)["outcome"] == "unverified" for r in completed),
            "cancelled_runs": sum(r.get("outcome") == "cancelled" for r in completed),
            "average_duration_ms": round(sum(values) / len(values)) if values else None,
            "duration_total_ms": sum(values), "duration_samples": len(values),
            "best_duration_ms": min(values) if values else None,
            "last_duration_ms": dated_clean[-1]["duration_ms"] if dated_clean else None,
            "last_run": summary(dated[-1]) if dated else None,
            "incident_count": incidents, "ai_interventions": total("ai_interventions"),
            "deterministic_blocks": total("deterministic_blocks"),
            "slowest_steps": sorted(slow, key=lambda s: s["average_duration_ms"], reverse=True)[:5],
            "recent_runs": [summary(r) for r in reversed(completed[-10:])]}


def collect(root: Path, system=None):
    warnings, procedures = [], []
    root = root.resolve()
    directory = root / "procedure"
    if directory.is_dir():
        for folder in sorted(directory.iterdir()):
            if not folder.is_dir() or folder.is_symlink():
                continue
            meta = read_object(folder / "procedure.json", warnings)
            if meta is None:
                continue
            meta.setdefault("slug", folder.name)
            meta.setdefault("name", folder.name)
            runs = []
            runs_dir = folder / "runs"
            if runs_dir.is_dir() and not runs_dir.is_symlink():
                for path in runs_dir.glob("*.json"):
                    run = read_object(path, warnings)
                    if run and run.get("run_id"):
                        runs.append(run)
            incidents = 0
            errors = folder / "experience" / "errors.jsonl"
            if errors.is_file() and not errors.is_symlink():
                try:
                    with errors.open(encoding="utf-8-sig") as stream:
                        for line in stream:
                            if not line.strip():
                                continue
                            try:
                                if isinstance(json.loads(line), dict):
                                    incidents += 1
                            except ValueError:
                                warnings.append(f"Incidente non leggibile: {folder.name}")
                except OSError:
                    warnings.append(f"Storico non leggibile: {folder.name}")
            plan_path = folder / "execution-plan.json"
            plan = read_object(plan_path, warnings) if plan_path.exists() else None
            blocks = plan.get("blocks", []) if plan else []
            procedures.append({"meta": meta, "path": str(folder),
                               "plan": {"status": plan.get("status", "missing") if plan else "missing",
                                        "blocks": len(blocks) if isinstance(blocks, list) else 0},
                               "metrics": metrics(runs, incidents)})
    company_path = root / "company-profile.json"
    company = read_object(company_path, warnings) if company_path.exists() else None
    experience = {"lessons": 0, "validated": 0, "candidates": 0}
    for path in (root / "experience").glob("*/*.json"):
        doc = read_object(path, warnings)
        lessons = doc.get("lessons", []) if doc else []
        for lesson in lessons if isinstance(lessons, list) else []:
            if not isinstance(lesson, dict):
                continue
            experience["lessons"] += 1
            experience["validated" if lesson.get("status") == "validated" else "candidates"] += 1
    totals = {key: sum(p["metrics"][key] for p in procedures)
              for key in ("run_count", "successful_runs", "failed_runs", "unverified_runs", "incident_count",
                          "ai_interventions", "duration_samples", "duration_total_ms")}
    counts = {**totals, "total": len(procedures), "runs": totals["run_count"],
              "incidents": totals["incident_count"], "shared_lessons": experience["lessons"],
              "average_duration_ms": round(totals["duration_total_ms"] / totals["duration_samples"])
              if totals["duration_samples"] else None}
    for state in ("draft", "validated", "active"):
        counts[state] = sum(p["meta"].get("status") == state for p in procedures)
    counts["compiled"] = sum(p["plan"]["status"] == "compiled" for p in procedures)
    return {"generated_at": datetime.now(timezone.utc).isoformat(), "version": "2.6.0",
            "system": system or {}, "counts": counts, "procedures": procedures,
            "company": company or {"status": "not_configured"}, "experience": experience,
            "warnings": warnings, "root": str(root)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    Path(args.output).write_text(json.dumps(collect(Path(args.root)), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
