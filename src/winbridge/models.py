from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class WindowRef:
    hwnd: int
    pid: int
    title: str
    class_name: str
    backend: str = "win32"

    def dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ElementRef:
    hwnd: int
    runtime_id: str
    backend: str
    name: str
    control_type: str
    automation_id: str
    left: int
    top: int
    right: int
    bottom: int

    def dict(self) -> dict[str, Any]:
        return asdict(self)

