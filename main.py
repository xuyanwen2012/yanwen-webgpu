#!/usr/bin/env python3
"""
Robust HTTP Server for HTML Files
A more feature-rich alternative to python3 -m http.server
"""

import http.server
import socketserver
import os
import sys
import argparse
import logging
from pathlib import Path
from urllib.parse import urlparse, unquote
import mimetypes
import signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("server.log")],
)
logger = logging.getLogger(__name__)


class HTMLFileHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP request handler that only serves HTML files and provides better logging."""

    def __init__(self, *args, **kwargs):
        # Set up MIME types
        mimetypes.init()
        super().__init__(*args, **kwargs)

    def log_message(self, format, *args):
        """Override to use our logger instead of stderr."""
        logger.info(f"{self.address_string()} - {format % args}")

    def do_GET(self):
        """Handle GET requests, only serving HTML files."""
        try:
            # Parse the URL
            parsed_url = urlparse(self.path)
            path = unquote(parsed_url.path)

            # Handle root path
            if path == "/":
                self._serve_index()
                return

            # Convert to file system path
            file_path = Path(self.directory) / path.lstrip("/")

            # Security check: prevent directory traversal
            try:
                file_path = file_path.resolve()
                if not str(file_path).startswith(str(Path(self.directory).resolve())):
                    self._send_error(403, "Access denied")
                    return
            except (ValueError, RuntimeError):
                self._send_error(403, "Access denied")
                return

            # Check if file exists and is an HTML file
            if not file_path.exists():
                self._send_error(404, "File not found")
                return

            if not file_path.is_file():
                self._send_error(403, "Not a file")
                return

            # Only serve HTML files
            if not self._is_html_file(file_path):
                self._send_error(403, "Only HTML files are allowed")
                return

            # Serve the HTML file
            self._serve_html_file(file_path)

        except Exception as e:
            logger.error(f"Error handling request: {e}")
            self._send_error(500, "Internal server error")

    def _is_html_file(self, file_path):
        """Check if the file is an HTML file."""
        return file_path.suffix.lower() in [".html", ".htm"]

    def _serve_index(self):
        """Serve an index page listing all HTML files."""
        try:
            html_files = []
            for file_path in Path(self.directory).glob("*.html"):
                if file_path.is_file():
                    html_files.append(file_path.name)

            # Sort files for consistent ordering
            html_files.sort()

            # Create index HTML
            index_html = self._create_index_html(html_files)

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(index_html.encode("utf-8"))))
            self.end_headers()
            self.wfile.write(index_html.encode("utf-8"))

        except Exception as e:
            logger.error(f"Error serving index: {e}")
            self._send_error(500, "Internal server error")

    def _create_index_html(self, html_files):
        """Create a minimal index HTML page listing all HTML files."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>HTML Files</title>
</head>
<body>
    <h1>HTML Files</h1>
    <ul>"""

        for html_file in html_files:
            html += f"""
        <li><a href="/{html_file}">{html_file}</a></li>"""

        html += """
    </ul>
</body>
</html>"""
        return html

    def _serve_html_file(self, file_path):
        """Serve an HTML file with proper headers."""
        try:
            with open(file_path, "rb") as f:
                content = f.read()

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            self.end_headers()
            self.wfile.write(content)

        except Exception as e:
            logger.error(f"Error serving file {file_path}: {e}")
            self._send_error(500, "Error reading file")

    def _send_error(self, code, message):
        """Send a minimal error response."""
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        error_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Error {code}</title>
</head>
<body>
    <h1>Error {code}</h1>
    <p>{message}</p>
    <p><a href="/">Back to index</a></p>
</body>
</html>"""

        self.wfile.write(error_html.encode("utf-8"))


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info("Shutdown signal received. Stopping server...")
    sys.exit(0)


def main():
    """Main function to start the HTTP server."""
    parser = argparse.ArgumentParser(
        description="Robust HTTP server for HTML files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Start server on port 8001
  python main.py -p 8080           # Start server on port 8080
  python main.py -d /path/to/html  # Serve files from specific directory
        """,
    )

    parser.add_argument(
        "-p", "--port", type=int, default=8001, help="Port to serve on (default: 8001)"
    )

    parser.add_argument(
        "-d",
        "--directory",
        type=str,
        default=".",
        help="Directory to serve files from (default: current directory)",
    )

    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host to bind to (default: localhost)",
    )

    args = parser.parse_args()

    # Validate directory
    directory = Path(args.directory).resolve()
    if not directory.exists():
        logger.error(f"Directory does not exist: {directory}")
        sys.exit(1)

    if not directory.is_dir():
        logger.error(f"Path is not a directory: {directory}")
        sys.exit(1)

    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create server
    with socketserver.TCPServer((args.host, args.port), HTMLFileHandler) as httpd:
        # Set the directory for the handler
        httpd.RequestHandlerClass.directory = str(directory)

        logger.info(f"Starting HTTP server...")
        logger.info(f"Serving files from: {directory}")
        logger.info(f"Server URL: http://{args.host}:{args.port}")
        logger.info(f"Index page: http://{args.host}:{args.port}/")
        logger.info(f"Only HTML files will be served")
        logger.info(f"Logs saved to: server.log")
        logger.info(f"Press Ctrl+C to stop the server")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
