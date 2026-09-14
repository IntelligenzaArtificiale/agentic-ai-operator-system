"""Per-user Windows mutexes for state transactions and a single activation UI."""

from contextlib import contextmanager
import ctypes
from ctypes import wintypes
from functools import wraps
import hashlib
import os


@contextmanager
def mutex(scope, path, timeout_ms=0):
    identity = hashlib.sha256(os.path.normcase(os.path.abspath(path)).encode()).hexdigest()
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
    kernel.CreateMutexW.restype = wintypes.HANDLE
    kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel.WaitForSingleObject.restype = wintypes.DWORD
    kernel.ReleaseMutex.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = kernel.CreateMutexW(None, False, f"Local\\AIOS-{scope}-{identity}")
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    acquired = False
    try:
        result = kernel.WaitForSingleObject(handle, timeout_ms)
        if result == 0xFFFFFFFF:
            raise ctypes.WinError(ctypes.get_last_error())
        acquired = result in (0, 0x80)  # Owned, or abandoned by a terminated process.
        yield acquired
    finally:
        if acquired:
            kernel.ReleaseMutex(handle)
        kernel.CloseHandle(handle)


def serialized(method):
    @wraps(method)
    def locked(self, *args, **kwargs):
        with mutex("state", self.state_dir, 15000) as acquired:
            if not acquired:
                raise OSError("Verifica licenza già in corso. Attendi e riprova.")
            return method(self, *args, **kwargs)
    return locked
