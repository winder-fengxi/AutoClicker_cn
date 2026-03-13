import ctypes
import os
from typing import Optional


class ClickerService:
    """C++ DLL 封装。"""

    def __init__(self, base_dir: str):
        self._base_dir = base_dir
        self._lib: Optional[ctypes.CDLL] = None
        self._load_dll()

    def _load_dll(self) -> None:
        dll_path = os.path.join(self._base_dir, "clicker_core.dll")
        try:
            self._lib = ctypes.CDLL(dll_path)
            self._lib.StartClicker.argtypes = [
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
            ]
            self._lib.StartClicker.restype = None

            self._lib.StopClicker.argtypes = []
            self._lib.StopClicker.restype = None

            self._lib.IsRunning.argtypes = []
            self._lib.IsRunning.restype = ctypes.c_bool
        except Exception:
            self._lib = None

    @property
    def available(self) -> bool:
        return self._lib is not None

    def start(
        self,
        interval: int,
        button: int,
        loop_mode: int,
        loop_count: int,
        location_mode: int,
        fixed_x: int,
        fixed_y: int,
        click_type: int,
    ) -> None:
        if not self._lib:
            raise RuntimeError("DLL not available")
        self._lib.StartClicker(interval, button, loop_mode, loop_count, location_mode, fixed_x, fixed_y, click_type)

    def stop(self) -> None:
        if self._lib:
            self._lib.StopClicker()

    def is_running(self) -> bool:
        if not self._lib:
            return False
        return bool(self._lib.IsRunning())
