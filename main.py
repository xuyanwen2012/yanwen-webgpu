import http.server
import socketserver
import sys
import argparse
import logging
from pathlib import Path
from urllib.parse import urlparse, unquote
import mimetypes
import signal

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("server.log")],
)
logger = logging.getLogger(__name__)


class COIRequestHandler(http.server.SimpleHTTPRequestHandler):
    # Serve from a specific directory (set by the server)
    def __init__(self, *args, directory=None, **kwargs):
        super().__init__(*args, directory=directory, **kwargs)

    # Inject COOP/COEP (and a couple of helpful) headers on every response
    def end_headers(self):
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.send_header("X-Content-Type-Options", "nosniff")
        # Dev caching—tweak as you like
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    # Optional: keep your index at "/"
    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if path == "/":
            return self._serve_index()
        return super().do_GET()

    def _serve_index(self):
        try:
            # list only .html by default; adjust if you want to list others
            html_files = sorted(
                [p.name for p in Path(self.directory).glob("*.html") if p.is_file()]
            )
            content = [
                "<!DOCTYPE html><html><head><meta charset='utf-8'>",
                "<title>HTML Files</title></head><body>",
                "<h1>HTML Files</h1><ul>",
            ]
            for f in html_files:
                content.append(f"<li><a href='/{f}'>{f}</a></li>")
            content.append("</ul></body></html>")
            body = "\n".join(content).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            logger.error(f"Error serving index: {e}")
            self.send_error(500, "Internal server error")


def main():
    parser = argparse.ArgumentParser(description="COI static server (SAB-ready)")
    parser.add_argument("-p", "--port", type=int, default=8001)
    parser.add_argument("-d", "--directory", type=str, default=".")
    parser.add_argument("--host", type=str, default="localhost")
    args = parser.parse_args()

    directory = Path(args.directory).resolve()
    if not directory.is_dir():
        logger.error(f"Invalid directory: {directory}")
        sys.exit(1)

    # Threaded server so workers/assets load in parallel
    class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
        daemon_threads = True

    handler = lambda *h_args, **h_kwargs: COIRequestHandler(
        *h_args, directory=str(directory), **h_kwargs
    )
    with ThreadingHTTPServer((args.host, args.port), handler) as httpd:
        logger.info(f"Serving: {directory}")
        logger.info(f"URL:     http://{args.host}:{args.port}")
        logger.info(
            "COOP/COEP enabled (SharedArrayBuffer should work). Ctrl+C to stop."
        )
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logger.info("Server stopped by user")


if __name__ == "__main__":
    main()
