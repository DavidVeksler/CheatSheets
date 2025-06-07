#!/usr/bin/env python3
"""
Simple HTTP server for testing HTML files locally without CORS issues.
Works on both Mac and Windows.
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

PORT = 8000

class PHPHandler(http.server.SimpleHTTPRequestHandler):
    """Handler that serves PHP files as HTML for local testing"""
    
    def end_headers(self):
        # Add CORS headers to prevent issues
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def guess_type(self, path):
        # Serve PHP files as HTML for local testing
        if path.endswith('.php'):
            return 'text/html'
        return super().guess_type(path)

def main():
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print(f"Starting server in: {script_dir}")
    print(f"Server running at: http://localhost:{PORT}")
    print("Press Ctrl+C to stop the server")
    
    try:
        with socketserver.TCPServer(("", PORT), PHPHandler) as httpd:
            # Open browser automatically
            webbrowser.open(f'http://localhost:{PORT}')
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"Port {PORT} is already in use. Try a different port or stop the existing server.")
            sys.exit(1)
        else:
            raise

if __name__ == "__main__":
    main()