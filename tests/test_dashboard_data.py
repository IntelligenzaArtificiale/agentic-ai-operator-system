"""Dashboard data is derived from evidence, not filenames or optimistic status."""
import json
from pathlib import Path

from dashboard_data import collect, metrics


def run(outcome="succeeded", duration=1000, at="2026-09-15T12:00:00Z", **extra):
    return {"run_id": "fixture", "outcome": outcome, "verification_status": "verified",
            "duration_ms": duration, "ended_at": at, **extra}


def test_latest_uses_dates_not_input_order():
    result = metrics([run(duration=9000, at="2026-09-16T12:00:00Z"), run(duration=1000)], 0)
    assert result["last_duration_ms"] == 9000
    assert result["last_run"]["at"] == "2026-09-16T12:00:00Z"


def test_undated_and_unverified_never_masquerade_as_latest_success():
    result = metrics([run(duration=20, at=None), run(duration=1, verification_status="unverified")], 2)
    assert result["last_run"]["outcome"] == "unverified"
    assert result["last_duration_ms"] is None
    assert result["average_duration_ms"] == 20
    assert result["unverified_runs"] == 1


def test_invalid_durations_and_running_records_are_not_verified_samples():
    result = metrics([run(duration=-1), run(duration=float('nan')), run(duration=True), run("running")], 0)
    assert result["average_duration_ms"] is None
    assert result["run_count"] == 3


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def test_weighted_average_and_corrupt_plan_do_not_hide_process(tmp_path):
    for slug, durations in (("alpha", [1000,1000,1000]), ("beta", [9000])):
        folder = tmp_path / "procedure" / slug
        write(folder / "procedure.json", {"name":slug, "status":"active"})
        for i, value in enumerate(durations):
            write(folder / "runs" / f"{i}.json", run(duration=value))
    (tmp_path / "procedure/alpha/execution-plan.json").write_text('{broken', encoding="utf-8")
    data = collect(tmp_path)
    assert len(data["procedures"]) == 2
    assert data["counts"]["average_duration_ms"] == 3000
    assert len(data["warnings"]) == 1


def test_empty_and_corrupt_company_are_explicit(tmp_path):
    assert collect(tmp_path)["counts"]["runs"] == 0
    write(tmp_path / "company-profile.json", [])
    data = collect(tmp_path)
    assert data["company"]["status"] == "not_configured"
    assert data["warnings"]


def test_slowest_steps_ignore_invalid_and_failed_samples():
    data = metrics([run(steps=[{"step_id":"read","label":"Read","duration_ms":100},None]),
                    run("failed",steps=[{"step_id":"read","duration_ms":9000}])], 0)
    assert data["slowest_steps"] == [{"step_id":"read","label":"Read","samples":1,"average_duration_ms":100}]
