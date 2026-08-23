from __future__ import annotations

import argparse
import ctypes
import subprocess
import time
from ctypes import wintypes


class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("PageFaultCount", wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("executable")
    args = parser.parse_args()
    process = subprocess.Popen(
        [args.executable], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    try:
        time.sleep(2)
        counters = PROCESS_MEMORY_COUNTERS(cb=ctypes.sizeof(PROCESS_MEMORY_COUNTERS))
        handle = ctypes.windll.kernel32.OpenProcess(0x0410, False, process.pid)
        if not handle:
            raise ctypes.WinError()
        try:
            if not ctypes.windll.psapi.GetProcessMemoryInfo(
                handle, ctypes.byref(counters), ctypes.sizeof(counters)
            ):
                raise ctypes.WinError()
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
        print(f"working_set_mb={counters.WorkingSetSize / 1024 / 1024:.2f}")
        print(f"peak_working_set_mb={counters.PeakWorkingSetSize / 1024 / 1024:.2f}")
    finally:
        process.terminate()
        process.wait(timeout=5)
