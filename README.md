# Micro HTTP/1.1 Server

This project is a basic HTTP/1.1 server built from scratch using Python and sockets.

It accepts TCP connections, parses HTTP requests manually, and serves files from a local folder.

Features
- Uses Python socket
- Handles GET requests
- Parses the request line and headers manually
- Serves static files like HTML, CSS, and JS
- Returns 200, 404, 405, and 500 responses
- Sends Content-Type and Content-Length headers

How to run
1. Open terminal in the project folder
2. Run python server.py
3. Open http://127.0.0.1:8080 in your browser

Examples
- / loads index.html
- /style.css loads the CSS file
- /script.js loads the JS file
- /fake.html returns 404

Notes
- Only GET is supported
- The connection closes after each request