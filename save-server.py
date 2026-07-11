#!/usr/bin/env python3
"""Server locale: serve i file statici e accetta POST /__save?name=... per salvare le depth-map."""
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

ROOT = os.path.dirname(os.path.abspath(__file__))
DEPTH_DIR = os.path.join(ROOT, "gallery", "depth")
os.makedirs(DEPTH_DIR, exist_ok=True)

class Handler(SimpleHTTPRequestHandler):
    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/__save":
            qs = parse_qs(parsed.query)
            name = (qs.get("name", [""])[0])
            # sanitizza: solo basename, estensione .png
            name = os.path.basename(name)
            if not name.endswith(".png"):
                self.send_response(400); self.end_headers(); self.wfile.write(b"bad name"); return
            length = int(self.headers.get("Content-Length", 0))
            data = self.rfile.read(length)
            with open(os.path.join(DEPTH_DIR, name), "wb") as f:
                f.write(data)
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b"ok:" + str(len(data)).encode())
        else:
            self.send_response(404); self.end_headers()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

if __name__ == "__main__":
    os.chdir(ROOT)
    ThreadingHTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
