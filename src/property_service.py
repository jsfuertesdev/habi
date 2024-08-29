"""
Module for handling HTTP requests related to property data and running the HTTP server.
"""

import json
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from .database import get_properties, read_json
from utils.Logger import Logger


class PropertyHandler(BaseHTTPRequestHandler):
    """
    Handles HTTP GET requests and processes property-related queries.
    """

    def do_GET(self):
        """
        Processes GET requests to handle property queries or return errors.
        """
        Logger.add_to_log("info", f"Received request path: {self.path}")
        if self.path.startswith("/properties"):
            try:
                # Uncomment this section to get parameters from the URL.
                # parsed_url = urlparse(self.path)
                # filters = parse_qs(parsed_url.query)
                # filters = {k: v[0] for k, v in filters.items()}

                # Read filters from a JSON file
                filters = read_json("./src/payload.json")
                properties = get_properties(filters)

                # Send successful response
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(properties).encode())
                Logger.add_to_log("info", "Successfully handled request for properties")
            except FileNotFoundError as e:
                # Handle file not found error specifically
                Logger.add_to_log("error", f"File not found: {e}")
                Logger.add_to_log("error", traceback.format_exc())
                self.send_error(500, "Internal Server Error")
            except json.JSONDecodeError as e:
                # Handle JSON decoding error specifically
                Logger.add_to_log("error", f"Error decoding JSON: {e}")
                Logger.add_to_log("error", traceback.format_exc())
                self.send_error(500, "Internal Server Error")
            except Exception as e:
                # Handle other exceptions
                Logger.add_to_log("error", str(e))
                Logger.add_to_log("error", traceback.format_exc())
                self.send_error(500, "Internal Server Error")
        else:
            # Handle not found error for invalid paths
            self.send_error(404, "Not Found")
            Logger.add_to_log("warn", f"Request path not found: {self.path}")


def run_server(port=8000):
    """
    Starts the HTTP server on the specified port.

    :param port: Port number for the server to listen on (default: 8000).
    """
    server_address = ("", port)
    httpd = HTTPServer(server_address, PropertyHandler)
    Logger.add_to_log("info", f"Starting server on port {port}...")
    print(f"Starting server on port {port}...")
    httpd.serve_forever()
