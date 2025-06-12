import os
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        message = os.environ.get('GLOBAL_MESSAGE', 'No message found')
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(message.encode())

if __name__ == '__main__':
    port = 8000
    server = HTTPServer(('', port), Handler)
    print(f"Serving on port {port}")
    server.serve_forever()

