#!/usr/bin/env python3
"""
Serve a copia local do Pathbuilder.

Precisa aceitar POST: o app faz POST para a propria origem na inicializacao, e
`python -m http.server` responde `501 Unsupported method` -- que aparece no
console do navegador e e a suspeita de por que a tela fica no spinner.
"""
import http.server, socketserver, sys

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        self.rfile.read(n)
        corpo = b"{}"
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def log_message(self, *a):
        pass

porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8899
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("127.0.0.1", porta), Handler) as s:
    s.serve_forever()
