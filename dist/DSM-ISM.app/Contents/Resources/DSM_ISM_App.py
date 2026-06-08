#!/usr/bin/env python3
"""Local desktop launcher for the DSM/ISM interactive UI."""

from __future__ import annotations

import functools
import http.server
import socket
import socketserver
import sys
import threading
import webbrowser
from pathlib import Path


APP_TITLE = "辽宁省大数据管理与优化决策重点实验室"


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


class ReusableThreadingServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def app_dir() -> Path:
    return Path(__file__).resolve().parent


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def start_server(directory: Path) -> tuple[ReusableThreadingServer, str]:
    handler = functools.partial(QuietHandler, directory=str(directory))
    server = ReusableThreadingServer(("127.0.0.1", find_free_port()), handler)
    host, port = server.server_address
    url = f"http://{host}:{port}/index.html"
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, url


def run_tk_window(server: ReusableThreadingServer, url: str) -> None:
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.title(APP_TITLE)
    root.geometry("460x220")
    root.minsize(420, 200)

    frame = ttk.Frame(root, padding=20)
    frame.pack(fill="both", expand=True)

    title = ttk.Label(frame, text=APP_TITLE, font=("TkDefaultFont", 18, "bold"))
    title.pack(anchor="w")

    status = ttk.Label(frame, text="应用已启动，本地界面正在浏览器中运行。")
    status.pack(anchor="w", pady=(12, 4))

    url_label = ttk.Label(frame, text=url, foreground="#0f766e")
    url_label.pack(anchor="w", pady=(0, 16))

    buttons = ttk.Frame(frame)
    buttons.pack(fill="x", pady=(8, 0))

    ttk.Button(buttons, text="打开界面", command=lambda: webbrowser.open(url)).pack(
        side="left"
    )

    def quit_app() -> None:
        server.shutdown()
        server.server_close()
        root.destroy()

    ttk.Button(buttons, text="退出应用", command=quit_app).pack(side="right")
    root.protocol("WM_DELETE_WINDOW", quit_app)
    root.after(300, lambda: webbrowser.open(url))
    root.mainloop()


def run_cli(server: ReusableThreadingServer, url: str) -> int:
    webbrowser.open(url)
    print(f"{APP_TITLE} 已启动：{url}")
    print("按 Ctrl+C 退出。")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()
    return 0


def main() -> int:
    directory = app_dir()
    if not (directory / "index.html").exists():
        print(f"找不到 index.html：{directory / 'index.html'}", file=sys.stderr)
        return 1

    server, url = start_server(directory)
    try:
        run_tk_window(server, url)
    except Exception:
        return run_cli(server, url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
