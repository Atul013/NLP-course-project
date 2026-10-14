"""Local same-origin frontend and API server: python web/dev.py."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from api.analyze import handler as ApiHandler

ROOT = Path(__file__).resolve().parent


class DevHandler(ApiHandler, SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / "public"), **kwargs)

    def do_GET(self):
        if self.path.split("?")[0] == "/api/analyze":
            return ApiHandler.do_GET(self)
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == "/api/analyze":
            return ApiHandler.do_POST(self)
        self.respond(404, {"error": "Not found"})


if __name__ == "__main__":
    print("Phish Lens: http://127.0.0.1:4180", flush=True)
    ThreadingHTTPServer(("127.0.0.1", 4180), DevHandler).serve_forever()
