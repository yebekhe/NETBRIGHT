#!/usr/bin/env python3

import socket
import threading
from concurrent.futures import ThreadPoolExecutor
import time
import os
import sys
import argparse
import logging
import configparser
import random

Tunnel_State = 0
# Function to send data in fragments
def send_data_in_fragment(data, sock):
    global random_fragment
    if random_fragment == "down":
        data_len = len(data)
        L_fragment = random.randint(5, data_len // 2)
        fragment_sleep = 0.0025974025974026 * L_fragment
    else:
        L_fragment = 25
        fragment_sleep = 0.065
    for i in range(0, len(data), L_fragment):
        fragment_data = data[i:i+L_fragment]
        logging.debug(f'[SEND] {i} bytes of {str(data_len)}')
        sock.sendall(fragment_data)
        time.sleep(fragment_sleep)
    logging.debug('[SEND] ----------finish------------')

# Function to handle upstream traffic from the client to the backend server
def my_upstream(client_sock):
    first_flag = True
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as backend_sock:
        backend_sock.settimeout(my_socket_timeout)
        while True:
            try:
                if first_flag:
                    first_flag = False
                    time.sleep(first_time_sleep)
                    data = client_sock.recv(16384)
                    if data:
                        backend_ip = get_next_backend_ip()
                        print(f'Using backend IP: {backend_ip}')  # Print the selected backend IP
                        backend_sock.connect((backend_ip, Cloudflare_port))
                        thread_down = threading.Thread(target=my_downstream, args=(backend_sock, client_sock))
                        thread_down.daemon = True
                        thread_down.start()
                        send_data_in_fragment(data, backend_sock)
                    else:
                        raise Exception('cli syn close')
                else:
                    data = client_sock.recv(4096)
                    if data:
                        backend_sock.sendall(data)
                    else:
                        raise Exception('cli pipe close')
            except Exception as e:
                logging.debug(f'[UPSTREAM] {repr(e)}')
                time.sleep(2)
                client_sock.close()
                return False


# Function to handle downstream traffic from the backend server to the client
def my_downstream(backend_sock, client_sock):
    first_flag = True
    while True:
        try:
            if first_flag:
                first_flag = False
                data = backend_sock.recv(16384)
                if data:
                    client_sock.sendall(data)
                else:
                    raise Exception('backend pipe close at first')
            else:
                data = backend_sock.recv(4096)
                if data:
                    client_sock.sendall(data)
                else:
                    raise Exception('backend pipe close')
        except Exception as e:
            logging.debug(f'[DOWNSTREAM] {repr(e)}')
            time.sleep(2)
            client_sock.close()
            return False

# Function to parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Python Proxy')
    parser.add_argument('--config', type=str, default='config.ini', help='Path to the configuration file')
    return parser.parse_args()

# Function to load configuration from a file
def load_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)

    global listen_PORT, Cloudflare_IPs, Cloudflare_port, my_socket_timeout, first_time_sleep, accept_time_sleep , random_fragment, condition_of_tunnel, socket_listen
    listen_PORT = int(config.get('settings', 'listen_PORT'))
    Cloudflare_IPs = [ip.strip() for ip in config.get('settings', 'Cloudflare_IP').split(',')]
    Cloudflare_port = int(config.get('settings', 'Cloudflare_port'))
    my_socket_timeout = int(config.get('settings', 'my_socket_timeout'))
    first_time_sleep = float(config.get('settings', 'first_time_sleep'))
    accept_time_sleep = float(config.get('settings', 'accept_time_sleep'))
    random_fragment = str(config.get('settings', 'random_fragment'))
    socket_listen = int(config.get('settings', 'socket_listen'))

def log_write(log_data):
    file = open("log_data.txt", "w")
    file.write(log_data)
    file.close()

# Function to get the next backend IP using round-robin load balancing
def get_next_backend_ip():
    global Cloudflare_IPs
    selected_ip = random.choice(Cloudflare_IPs)
    Cloudflare_IPs = Cloudflare_IPs[1:] + [selected_ip]
    return selected_ip

# Main function to start the proxy server
def main():
    print("Uh shit here we going again!")
    args = parse_args()
    load_config(args.config)

    print(f'Proxy server listening on 127.0.0.1:{listen_PORT}')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(('', listen_PORT))
        server_sock.listen(socket_listen)
        
        with ThreadPoolExecutor(max_workers=128) as executor:
            while Tunnel_State == 1:
                client_sock, client_addr = server_sock.accept()
                client_sock.settimeout(my_socket_timeout)
                time.sleep(accept_time_sleep)
                executor.submit(my_upstream, client_sock)
                print("Yuho, I'm Still Alive!")
        

if __name__ == "__main__":
    main()
