import socket
import ssl

class TLSConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.tls_sock = None

    def establish_connection(self):
        try:
            context = ssl.create_default_context()
            context.set_alpn_protocols(['h2'])
            sock = socket.create_connection((self.host, self.port))
            self.tls_sock = context.wrap_socket(sock, server_hostname=self.host)
            return self.tls_sock
        except Exception as e:
            print(f"Erro ao estabelecer a conexão TLS: {e}")
            exit(1)

    def close_connection(self):
        if self.tls_sock:
            self.tls_sock.close()
            print("Conexão TLS encerrada.")

