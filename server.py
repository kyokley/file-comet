import cgi
import io
import sys
import uuid
import multipart
from pathlib import Path
import http.server
import socketserver
from http import HTTPStatus

PORT = 62346

FORM_HTML = b"""
<html>
    <body>
        <form enctype="multipart/form-data" action="" method="post">
            <label for="fileselector">Select a file:</label>
            <input type="file" id="fileselector" name="fileselector" />
            <input type="submit" id="submit" name="submit" value="Submit" />
        </form>
    </body>
</html>
"""

SUCCESS_FORM_HTML = b"""
<html>
    <head>
        File received successfully
    </head>
    <body>
        <form enctype="multipart/form-data" action="" method="post">
            <label for="fileselector">Select a file:</label>
            <input type="file" id="fileselector" name="fileselector" />
            <input type="submit" id="submit" name="submit" value="Submit" />
        </form>
    </body>
</html>
"""

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


def receive_file_request_handler_factory(file_path):
    guid = uuid.uuid4()

    class LimitedRequestHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def do_GET(self):
            print(f'Got request for {self.path}')
            if self.path.lower().strip('/') == str(guid):
                return super().do_GET()
            else:
                self.send_error(HTTPStatus.NOT_FOUND, 'File not found')
                return None

        def do_POST(self):
            if self.path.lower().strip('/') == str(guid):
                self.send_error(HTTPStatus.NOT_FOUND, 'File not found')
                return None

            # Receive and store file
            content_length = int(self.headers['Content-Length'])
            _, options = cgi.parse_header(self.headers['Content-Type'])
            boundary = options['boundary']
            data = io.BytesIO(self.rfile.read(content_length))

            parser = multipart.MultipartParser(data, boundary)

            selector_data = None
            for part in parser.parts():
                if part.name == 'fileselector':
                    selector_data = part.raw
                    filename = part.filename
                    break
            else:
                print('Error: Data not found')
                self.send_error(HTTPStatus.BAD_REQUEST,
                                'Improperly formed request')

            if file_path.is_dir():
                with open(file_path / filename, 'wb') as f:
                    f.write(selector_data)
            else:
                with open(file_path, 'wb') as f:
                    f.write(selector_data)

            print(f'Received {filename}')
            self.send_response(HTTPStatus.CREATED)
            self.end_headers()
            self.wfile.write(SUCCESS_FORM_HTML)
            self.wfile.flush()

        def send_head(self):
            f = io.BytesIO()
            f.write(FORM_HTML)
            f.seek(0)

            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", 'text/html')
            self.send_header("Content-Length", str(len(FORM_HTML)))
            self.end_headers()

            return f

    return guid, LimitedRequestHandler


def main():
    if len(sys.argv) > 2:
        raise Exception('Incorrect number of arguments')

    if len(sys.argv) == 2:
        filename = sys.argv[1]
        file_path = Path(filename)
    else:
        file_path = Path('.')

    if not file_path.exists() or file_path.is_dir():
        print(f'Open {file_path} for receiving')
        guid, LimitedRequestHandler = receive_file_request_handler_factory(
            file_path)
    else:
        print(f'Open {file_path} for sending')
        guid, LimitedRequestHandler = send_file_request_handler_factory(
            file_path)

    try:
        with socketserver.TCPServer(("", PORT), LimitedRequestHandler) as httpd:
            print(f'Http Server Serving at port 0.0.0.0:{PORT}')
            print(f'{file_path} is being served at /{guid}')
            httpd.serve_forever()
    except KeyboardInterrupt:
        print('Shutting down')
