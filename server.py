import os
import socket
import mimetypes
from urllib.parse import unquote

HOST = "127.0.0.1"
PORT = 8080
WEB_ROOT = "www"
BUFFER_SIZE = 4096

def make_response(status_code, reason, body=b"", content_type="text/plain"):
    response_headers = [
        f"HTTP/1.1 {status_code} {reason}",
        f"Content-Length: {len(body)}",
        f"Content-Type: {content_type}",
        "Connection: close",
        "",
        ""
    ]
    header_data = "\r\n".join(response_headers).encode("utf-8")
    return header_data + body

def parse_request(request_data):
    try:
        text = request_data.decode("utf-8", errors="replace")
        lines = text.split("\r\n")

        if len(lines) == 0 or lines[0] == "":
            return None

        request_line = lines[0].split()

        if len(request_line) != 3:
            return None

        method = request_line[0]
        path = request_line[1]
        version = request_line[2]

        headers = {}

        for line in lines[1:]:
            if line == "":
                break
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip().lower()] = value.strip()

        return {
            "method": method,
            "path": path,
            "version": version,
            "headers": headers
        }

    except Exception:
        return None

def get_safe_file_path(path):
    path = unquote(path)

    if "?" in path:
        path = path.split("?", 1)[0]

    if path == "/":
        path = "/index.html"

    clean_path = os.path.normpath(path.lstrip("/"))

    if clean_path.startswith(".."):
        return None

    return os.path.join(WEB_ROOT, clean_path)

def handle_client(client_socket, client_address):
    try:
        request_data = client_socket.recv(BUFFER_SIZE)

        if not request_data:
            client_socket.close()
            return

        request = parse_request(request_data)

        if request is None:
            response = make_response(400, "Bad Request", b"400 Bad Request")
            client_socket.sendall(response)
            client_socket.close()
            return

        method = request["method"]
        path = request["path"]
        version = request["version"]

        print(f"{client_address} {method} {path} {version}")

        if version not in ["HTTP/1.0", "HTTP/1.1"]:
            response = make_response(400, "Bad Request", b"400 Bad Request")
            client_socket.sendall(response)
            client_socket.close()
            return

        if method != "GET":
            response = make_response(405, "Method Not Allowed", b"405 Method Not Allowed")
            client_socket.sendall(response)
            client_socket.close()
            return

        file_path = get_safe_file_path(path)

        if file_path is None or not os.path.isfile(file_path):
            response = make_response(404, "Not Found", b"404 Not Found")
            client_socket.sendall(response)
            client_socket.close()
            return

        with open(file_path, "rb") as file:
            body = file.read()

        content_type, _ = mimetypes.guess_type(file_path)

        if content_type is None:
            content_type = "application/octet-stream"

        response = make_response(200, "OK", body, content_type)
        client_socket.sendall(response)

    except Exception as e:
        print("Server error:", e)
        try:
            response = make_response(500, "Internal Server Error", b"500 Internal Server Error")
            client_socket.sendall(response)
        except Exception:
            pass

    finally:
        client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    print(f"Server running at http://{HOST}:{PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        handle_client(client_socket, client_address)

if __name__ == "__main__":
    start_server()