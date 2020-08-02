import sys
import uuid
from pathlib import Path
import http.server  # Our http server handler for http requests
import socketserver  # Establish the TCP Socket connections
from http import HTTPStatus

PORT = 9000


def request_handler_factory(file_path):
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


def main(filename):
    file_path = Path(filename)

    if not file_path.exists():
        raise Exception(f'{file_path} does not exist')

    guid, LimitedRequestHandler = request_handler_factory(file_path)

    with socketserver.TCPServer(("", PORT), LimitedRequestHandler) as httpd:
        print("Http Server Serving at port", PORT)
        print(f'{file_path} is being served at {guid}')
        httpd.serve_forever()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise Exception('Incorrect number of arguments')
    filename = sys.argv[1]
    main(filename)
