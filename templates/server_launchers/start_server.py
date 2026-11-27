#!/usr/bin/env python3
"""
qgis2web - Local HTTP Server for PBF Vector Tiles

Starts a local HTTP server in the current directory and opens the
specified HTML file (default: index.html) in the default browser.

This is necessary because browsers block CORS requests when opening
HTML files via file:// protocol, which prevents loading PBF tiles.

Works on Windows, macOS and Linux with Python 3.7+ (no other dependency).

Usage:
    python start_server.py [index_file]

Press Ctrl+C to stop the server or close the terminal window.
"""

import functools
import http.server
import os
import socket
import sys
import threading
import time
import webbrowser

# Vector tiles are rewritten by every export: they must never be answered from
# the browser cache, otherwise a reload keeps showing the previous tiles.
NO_CACHE_SUFFIXES = ('.pbf', '.mvt', '.json', '.js')


class TileRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Static handler tuned for projects with thousands of vector tiles."""

    # Keep-alive avoids a TCP handshake for every one of the (many) tiles.
    protocol_version = 'HTTP/1.1'

    extensions_map = dict(http.server.SimpleHTTPRequestHandler.extensions_map)
    extensions_map.update({
        '.pbf': 'application/x-protobuf',
        '.mvt': 'application/x-protobuf',
        '.json': 'application/json',
        '.woff2': 'font/woff2',
    })

    def end_headers(self):
        path = self.path.split('?', 1)[0].lower()
        if path.endswith(NO_CACHE_SUFFIXES):
            self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

    def log_message(self, format, *args):
        pass


class ThreadedHTTPServer(http.server.ThreadingHTTPServer):
    """Threaded server: the browser opens several connections at once."""

    daemon_threads = True
    allow_reuse_address = True
    request_queue_size = 128


def wait_for_server(port, timeout=15.0):
    """Wait until the port accepts connections."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.1)
    return False


def open_browser_when_ready(port, url):
    """Open the browser only once the server is really serving."""
    if wait_for_server(port):
        webbrowser.open(url)
    else:
        print("Server not reachable, open {} manually.".format(url))


def main():
    # Determine the directory where this script is located
    server_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(server_dir)

    # Determine which HTML file to open
    index_file = sys.argv[1] if len(sys.argv) > 1 else "index.html"
    index_path = os.path.join(server_dir, index_file)
    if not os.path.exists(index_path):
        print("Warning: {} not found in this directory.".format(index_file))

    # Let the OS pick a free port: binding port 0 avoids a race between the
    # port search and the server start.
    handler = functools.partial(TileRequestHandler, directory=server_dir)
    try:
        httpd = ThreadedHTTPServer(("", 0), handler)
    except OSError as e:
        print("Error starting server: {}".format(e))
        return 1

    port = httpd.server_address[1]
    url = "http://localhost:{}/{}".format(port, index_file)

    print("=" * 60)
    print("qgis2web - Local HTTP Server")
    print("=" * 60)
    print("Serving directory: {}".format(server_dir))
    print("Server URL:       http://localhost:{}".format(port))
    print("Map URL:          {}".format(url))
    print("Press Ctrl+C to stop the server or close the terminal window.")
    print("=" * 60)

    threading.Thread(
        target=open_browser_when_ready,
        args=(port, url),
        daemon=True,
    ).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        httpd.server_close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
