"""MCP entrypoint exposing validation and deterministic block execution."""

from __future__ import annotations

import json
import os
from pathlib import Path

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from windows_mcp.desktop.service import Desktop

from engine import ProcedureRunner, load_plan


mcp = FastMCP(
    name="procedure-runner",
    instructions="Executes only validated deterministic blocks from compiled procedure plans.",
)
_desktop: Desktop | None = None


def get_desktop() -> Desktop:
    global _desktop
    if _desktop is None:
        _desktop = Desktop()
    return _desktop


def procedure_root() -> Path:
    configured = os.getenv("AGENTIC_PROCEDURE_ROOT")
    if configured:
        return Path(configured)
    return Path.home() / "Documents" / "Agentic AI Operator System" / "procedure"


@mcp.tool(
    name="ValidatePlan",
    description="Validates one execution-plan.json inside the configured procedure root.",
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True),
)
def validate_plan_tool(plan_path: str) -> str:
    plan = load_plan(Path(plan_path), procedure_root())
    return json.dumps(
        {
            "valid": True,
            "procedure_slug": plan["procedure_slug"],
            "status": plan["status"],
            "blocks": len(plan["blocks"]),
        }
    )


@mcp.tool(
    name="ExecuteBlock",
    description=(
        "Executes one compiled deterministic block without screenshots. Returns control when the "
        "block needs AI reasoning, authorization, or a guard no longer matches."
    ),
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=False),
)
def execute_block_tool(
    plan_path: str,
    block_id: str,
    variables_json: str = "{}",
    allow_external_effects: bool = False,
) -> str:
    plan = load_plan(Path(plan_path), procedure_root())
    variables = json.loads(variables_json)
    if not isinstance(variables, dict):
        raise ValueError("variables_json must contain one JSON object")
    result = ProcedureRunner(get_desktop()).execute_block(
        plan,
        block_id,
        variables,
        allow_external_effects=allow_external_effects,
    )
    return json.dumps(result, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run()
