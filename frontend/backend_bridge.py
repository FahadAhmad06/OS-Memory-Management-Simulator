"""Subprocess JSON bridge communicating with the compiled C++17 backend over stdin/stdout."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import threading
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from config import BACKEND_DIR, BACKEND_EXECUTABLE_CANDIDATES, PROJECT_ROOT


class BackendBridgeError(Exception):
    """Raised when communication with or execution of the C++ backend fails."""


class BackendBridge:
    """Manages locating, invoking, and cleaning up the C++17 OS-MMS executable."""

    DEFAULT_TIMEOUT_SEC = 10.0

    def __init__(self, executable_path: Optional[Path] = None) -> None:
        self._explicit_path = Path(executable_path) if executable_path else None
        self._lock = threading.Lock()
        self._active_processes: set[subprocess.Popen[str]] = set()

    def resolve_executable(self) -> Optional[Path]:
        """Find the compiled C++ backend executable without modifying any backend files."""
        if self._explicit_path and self._explicit_path.is_file() and os.access(self._explicit_path, os.X_OK):
            return self._explicit_path

        env_override = os.environ.get("OS_MMS_BACKEND_BIN", "").strip()
        if env_override:
            env_path = Path(env_override)
            if env_path.is_file() and os.access(env_path, os.X_OK):
                return env_path

        for candidate in BACKEND_EXECUTABLE_CANDIDATES:
            if candidate.is_file() and os.access(candidate, os.X_OK):
                return candidate

        for name in ("OS-MMS", "os_memory_simulator"):
            found = shutil.which(name)
            if found:
                return Path(found)

        # Fallback recursive scan inside backend/build if present
        build_dir = BACKEND_DIR / "build"
        if build_dir.is_dir():
            for name in ("OS-MMS", "os_memory_simulator"):
                for match in build_dir.rglob(name):
                    if match.is_file() and os.access(match, os.X_OK):
                        return match

        return None

    def get_executable_status(self) -> Dict[str, Any]:
        """Return availability metadata for UI status badges."""
        exe = self.resolve_executable()
        if exe is not None:
            return {
                "available": True,
                "path": str(exe),
                "message": f"Connected: {exe.name}",
            }
        return {
            "available": False,
            "path": "",
            "message": "C++ backend binary not found (build backend first)",
        }

    def execute(
        self,
        operation: str,
        data: Dict[str, Any],
        timeout: float = DEFAULT_TIMEOUT_SEC,
    ) -> Dict[str, Any]:
        """
        Send a JSON request to the C++ backend via stdin and return parsed `result`.

        Exact C++ contract (backend/src/common/json_handler.cpp):
          Request:  {"operation": "<op>", "data": { ... }}
          Response: {"success": true, "result": { ... }}
                    or {"success": false, "error": {"message": "..."}}
        """
        exe = self.resolve_executable()
        if exe is None:
            expected_paths = ", ".join(str(p.relative_to(PROJECT_ROOT)) for p in BACKEND_EXECUTABLE_CANDIDATES[:4])
            raise BackendBridgeError(
                "C++ backend executable was not found. "
                f"Checked locations: {expected_paths}. "
                "Compile the backend with CMake before running simulations."
            )

        request_envelope = {
            "operation": operation,
            "data": data,
        }

        try:
            serialized_request = json.dumps(request_envelope)
        except (TypeError, ValueError) as exc:
            raise BackendBridgeError(f"Failed to serialize request payload to JSON: {exc}") from exc

        proc: Optional[subprocess.Popen[str]] = None
        try:
            proc = subprocess.Popen(
                [str(exe)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(exe.parent),
            )
            with self._lock:
                self._active_processes.add(proc)

            stdout_data, stderr_data = proc.communicate(input=serialized_request, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            if proc is not None:
                self._terminate_process(proc)
            raise BackendBridgeError(
                f"Backend timed out after {timeout:.1f}s while executing '{operation}'."
            ) from exc
        except OSError as exc:
            raise BackendBridgeError(f"Failed to launch C++ backend executable: {exc}") from exc
        finally:
            if proc is not None:
                with self._lock:
                    self._active_processes.discard(proc)

        if proc.returncode != 0 and not stdout_data.strip():
            err_detail = stderr_data.strip() or f"Exit code {proc.returncode}"
            raise BackendBridgeError(f"C++ backend terminated abnormally: {err_detail}")

        raw_stdout = stdout_data.strip()
        if not raw_stdout:
            raise BackendBridgeError("C++ backend returned empty output on stdout.")

        try:
            response = json.loads(raw_stdout)
        except json.JSONDecodeError as exc:
            preview = raw_stdout[:240]
            raise BackendBridgeError(
                f"Invalid JSON returned by C++ backend: {exc}. Output preview: {preview}"
            ) from exc

        if not isinstance(response, dict):
            raise BackendBridgeError("Malformed JSON response from backend: root is not an object.")

        success = response.get("success", False)
        if not success:
            error_obj = response.get("error")
            if isinstance(error_obj, dict) and "message" in error_obj:
                msg = str(error_obj["message"])
            else:
                msg = "Backend reported an unspecified error."
            raise BackendBridgeError(msg)

        result = response.get("result")
        if not isinstance(result, dict):
            raise BackendBridgeError("Backend response missing valid 'result' object.")

        return result

    def execute_async(
        self,
        widget: Any,
        operation: str,
        data: Dict[str, Any],
        on_success: Callable[[Dict[str, Any]], None],
        on_error: Callable[[str], None],
        timeout: float = DEFAULT_TIMEOUT_SEC,
    ) -> None:
        """Run a backend request on a worker thread and dispatch callbacks safely on the Tk main loop."""

        def _worker() -> None:
            try:
                result = self.execute(operation=operation, data=data, timeout=timeout)
            except BackendBridgeError as exc:
                err_msg = str(exc)
                self._schedule_ui(widget, lambda: on_error(err_msg))
                return
            except Exception as exc:  # noqa: BLE001
                err_msg = f"Unexpected bridge error: {exc}"
                self._schedule_ui(widget, lambda: on_error(err_msg))
                return

            self._schedule_ui(widget, lambda: on_success(result))

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()

    @staticmethod
    def _schedule_ui(widget: Any, callback: Callable[[], None]) -> None:
        try:
            if widget is not None and widget.winfo_exists():
                widget.after(0, callback)
        except Exception:  # noqa: BLE001
            pass

    @staticmethod
    def _terminate_process(proc: subprocess.Popen[str]) -> None:
        try:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=1.5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=1.0)
        except Exception:  # noqa: BLE001
            pass

    def cleanup(self) -> None:
        """Terminate any active backend child processes cleanly on application exit."""
        with self._lock:
            procs = list(self._active_processes)
            self._active_processes.clear()
        for proc in procs:
            self._terminate_process(proc)
