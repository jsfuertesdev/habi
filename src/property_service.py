import json
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from .database import get_properties, read_json
from utils.Logger import Logger

class PropertyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        Logger.add_to_log("info", f"Received request path: {self.path}")
        if self.path.startswith('/properties'):
            try:
                """
                # Uncomment this section to get parameters from the URL.
                parsed_url = urlparse(self.path)
                filters = parse_qs(parsed_url.query)
                filters = {k: v[0] for k, v in filters.items()}
                """
                filters = read_json('./src/payload.json')
                properties = get_properties(filters)

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(properties).encode())
                Logger.add_to_log("info", "Successfully handled request for properties")
            except Exception as e:
                Logger.add_to_log("error", str(e))
                Logger.add_to_log("error", traceback.format_exc())
                Logger.add_to_log("error", "handling request")
                self.send_error(500, 'Internal Server Error')
        else:
            self.send_error(404, 'Not Found')
            Logger.add_to_log("warn", f"Request path not found: {self.path}")

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, PropertyHandler)
    Logger.add_to_log("info", f'Starting server on port {port}...')
    print(f'Starting server on port {port}...')
    httpd.serve_forever()