import io
import sys
import uuid
from pathlib import Path
import http.server
import socketserver
from http import HTTPStatus

PORT = 62346


def send_file_request_handler_factory(file_path):
    guid = uuid.uuid4()

    class LimitedRequestHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            print(f'Got request for {self.path}')

            if self.path.lower().strip('/') == str(guid):
                self.path = str(file_path)
                return super().do_GET()
            else:
                self.send_error(HTTPStatus.NOT_FOUND, 'File not found')
                return None

    return guid, LimitedRequestHandler


def receive_file_request_handler_factory():
    guid = uuid.uuid4()

    class LimitedRequestHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def do_GET(self):
            print(f'Got request for {self.path}')
            return super().do_GET()

        def do_POST(self):
            # Receive and store file
            pass

        def send_head(self):
            f = io.BytesIO()
            form_html = b"""
            <html>
                <body>
                    <form enctype="multipart/form-data" action="#" method="post">
                        <label for="fileselector">Select a file:</label>
                        <input type="file" id="fileselector" name="fileselector" />
                        <input type="submit" id="submit" name="submit" value="Submit" />
                    </form>
                </body>
            </html>
            """
            f.write(form_html)
            f.seek(0)

            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", 'text/html')
            self.send_header("Content-Length", str(len(form_html)))
            # self.send_header("Last-Modified",
                # self.date_time_string(fs.st_mtime))
            self.end_headers()

            return f

    return guid, LimitedRequestHandler


def main():
    if len(sys.argv) != 2:
        raise Exception('Incorrect number of arguments')
    filename = sys.argv[1]
    file_path = Path(filename)

    if not file_path.exists():
        guid, LimitedRequestHandler = receive_file_request_handler_factory()
    else:
        guid, LimitedRequestHandler = send_file_request_handler_factory(
            file_path)

    try:
        with socketserver.TCPServer(("", PORT), LimitedRequestHandler) as httpd:
            print(f'Http Server Serving at port 0.0.0.0:{PORT}')
            print(f'{file_path} is being served at /{guid}')
            httpd.serve_forever()
    except KeyboardInterrupt:
        print('Shutting down')
