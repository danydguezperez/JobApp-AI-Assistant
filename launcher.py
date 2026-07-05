"""
JobApMaker launcher - packaged with PyInstaller.
Starts uvicorn in-process, waits until the server is ready,
and opens the browser automatically.
"""
from __future__ import annotations

import os
import socket
import sys
import threading
import time
import traceback
import webbrowser
from pathlib import Path


if getattr(sys, "frozen", False):
    BASE_DIR = Path(getattr(sys, "_MEIPASS"))
    os.chdir(Path(sys.executable).parent)
else:
    BASE_DIR = Path(__file__).parent


def is_port_open(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=1):
            return True
    except OSError:
        return False


def choose_port() -> int:
    for port in (8080, 8090, 8091, 8000):
        if not is_port_open(port):
            return port
    for port in range(8100, 8201):
        if not is_port_open(port):
            return port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def wait_and_open(port: int = 8080, timeout: int = 30) -> None:
    for _ in range(timeout * 4):
        if is_port_open(port):
            webbrowser.open(f"http://localhost:{port}")
            return
        time.sleep(0.25)


def main() -> None:
    port = choose_port()
    threading.Thread(target=wait_and_open, args=(port,), daemon=True).start()

    import jobapp_ai_assistant  # noqa: F401 - make sure PyInstaller bundles the FastAPI app module
    import uvicorn

    uvicorn.run(
        "jobapp_ai_assistant:app",
        host="127.0.0.1",
        port=port,
        reload=False,
        log_level="warning",
        log_config=None,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log_dir = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
        (log_dir / "JobApMaker_launcher.log").write_text(traceback.format_exc(), encoding="utf-8")
        raise
