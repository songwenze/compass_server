from http.server import BaseHTTPRequestHandler, HTTPServer

from main import get_mysql_connect, query_email, main, query_task, new_task

hostName = "localhost"
serverPort = 8080

my_conn = get_mysql_connect()


class MyServer(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path.startswith('/channel_id'):
            self.send_response(200)
            self.send_header('Content-type', 'text/json')
            self.end_headers()
            channel_id = self.path.removeprefix('/channel_id/').removesuffix('/')
            email = query_email(channel_id, my_conn)
            if email:
                self.wfile.write(email.encode("utf-8"))
            else:
                if query_task(channel_id, my_conn):
                    pass
                else:
                    new_task(channel_id, my_conn)
                self.wfile.write("OK".encode("utf-8"))
        else:
            self.send_response(404)





if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        main()
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    print("Server stopped.")