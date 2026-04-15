from __future__ import annotations

import http.server
import socketserver
from pathlib import Path


class SPAStaticHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, spa_root: Path, **kwargs):
        self._spa_root = spa_root.resolve()
        super().__init__(*args, directory=str(self._spa_root), **kwargs)

    def do_GET(self) -> None:
        clean = self.path.split("?", 1)[0]
        rel = clean.lstrip("/")
        if rel:
            candidate = (self._spa_root / rel).resolve()
            try:
                candidate.relative_to(self._spa_root)
            except ValueError:
                self.send_error(403)
                return
            if candidate.is_file():
                return super().do_GET()
        self.path = "/index.html"
        return super().do_GET()


def _handler_class(spa_root: Path):
    root = spa_root.resolve()

    class Bound(SPAStaticHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, spa_root=root, **kwargs)

    return Bound


def run_spa_server(host: str, port: int, dist: Path) -> None:
    root = dist.expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"UI dist not found: {root}")
    handler_cls = _handler_class(root)
    with socketserver.ThreadingTCPServer((host, port), handler_cls) as httpd:
        httpd.allow_reuse_address = True
        httpd.serve_forever()
