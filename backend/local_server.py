"""Local Development HTTP Server for AI Waste Segregation Advisor.

Simulates API Gateway proxy integration locally without requiring AWS credentials
or external dependencies, translating HTTP requests directly to lambda_handler().
"""

import os
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging

# Ensure project root is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from backend.lambda_handler import lambda_handler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("local_server")

PORT = int(os.getenv("PORT", "5001"))
HOST = os.getenv("HOST", "0.0.0.0")


class WasteAdvisorRequestHandler(BaseHTTPRequestHandler):
    """Translates incoming HTTP requests to AWS Lambda API Gateway events."""

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Api-Key")

    def do_OPTIONS(self):
        """Respond to CORS preflight requests."""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        """Health check and info endpoint."""
        if self.path in ("/", "/health"):
            self.send_response(200)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response_body = {
                "status": "healthy",
                "service": "AI Waste Segregation Advisor Local API",
                "endpoints": ["POST /analyze", "GET /health"],
                "mock_mode": os.getenv("MOCK_MODE", "true"),
            }
            self.wfile.write(json.dumps(response_body, indent=2).encode("utf-8"))
        else:
            self.send_response(404)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def do_POST(self):
        """Handle POST /analyze."""
        if self.path != "/analyze":
            self.send_response(404)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Endpoint '{self.path}' not found. Use POST /analyze."}).encode("utf-8"))
            return

        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else ""

        # Construct API Gateway proxy event
        event = {
            "httpMethod": "POST",
            "path": "/analyze",
            "headers": dict(self.headers),
            "body": raw_body,
            "requestContext": {
                "http": {
                    "method": "POST",
                    "path": "/analyze",
                }
            }
        }

        # Invoke Lambda handler
        lambda_result = lambda_handler(event, None)

        status_code = lambda_result.get("statusCode", 500)
        headers = lambda_result.get("headers", {})
        body = lambda_result.get("body", "{}")

        self.send_response(status_code)
        for h_key, h_val in headers.items():
            self.send_header(h_key, h_val)
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))


def run():
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, WasteAdvisorRequestHandler)
    print("=" * 60)
    print(f"🌿 AI Waste Segregation Advisor Backend running locally!")
    print(f"📍 URL: http://localhost:{PORT}")
    print(f"📡 API Endpoint: POST http://localhost:{PORT}/analyze")
    print(f"🩺 Health Check: GET http://localhost:{PORT}/health")
    print(f"🧪 Mock Mode: {os.getenv('MOCK_MODE', 'true')}")
    print("=" * 60)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down local server...")
        httpd.server_close()


if __name__ == "__main__":
    run()
