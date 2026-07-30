from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys

apartments_db = []

class ApartmentRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/api/apartments":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                if isinstance(data, list):
                    apartments_db.extend(data)
                    saved_count = len(data)
                else:
                    apartments_db.append(data)
                    saved_count = 1

                print(f"[Backend Mock] Received {saved_count} records. Total in DB: {len(apartments_db)}")

                response_data = {
                    "status": "SUCCESS",
                    "savedCount": saved_count,
                    "totalCountInDb": len(apartments_db)
                }
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(f"Error: {e}".encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == "/api/apartments":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(apartments_db, ensure_ascii=False).encode('utf-8'))
        elif self.path == "/api/apartments/count":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"totalCount": len(apartments_db)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run_mock_backend(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, ApartmentRequestHandler)
    print(f"[Backend Mock] Server running on http://localhost:{port}/api/apartments ...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("[Backend Mock] Stopping server.")
        httpd.server_close()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_mock_backend(port)
