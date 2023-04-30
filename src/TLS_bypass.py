import os
import json
import socket
import random
import time
import threading

if os.name == 'posix':
    import resource
    soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_NOFILE)
    resource.setrlimit(resource.RLIMIT_NOFILE, (soft_limit, hard_limit))
    socket_timeout = 60
    sleep_time = 0.01

my_socket_timeout = 60
first_time_sleep = 0.01
accept_time_sleep = 0.01

class ThreadedServer(object):
    def __init__(self, host, port, cf_ip, conf_port):
        self.host = host
        self.port = port
        self.cf_ip = cf_ip
        self.conf_port = conf_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(128)
        print ("Now listening at: 127.0.0.1:"+str(self.port))
        while True:
            client_sock , client_addr = self.sock.accept()
            client_sock.settimeout(my_socket_timeout)
            time.sleep(accept_time_sleep)
            thread_up = threading.Thread(target = self.my_upstream , args =(client_sock,) )
            thread_up.daemon = True
            thread_up.start()


    def stop(self):
        self.sock.close()

    def my_upstream(self, client_sock):
        first_flag = True
        backend_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backend_sock.settimeout(my_socket_timeout)
        while True:
            try:
                if( first_flag == True ):
                    first_flag = False

                    time.sleep(first_time_sleep)
                    data = client_sock.recv(16384)

                    if data:
                        backend_sock.connect((self.cf_ip,self.cf_ip))
                        thread_down = threading.Thread(target = self.my_downstream , args = (backend_sock , client_sock) )
                        thread_down.daemon = True
                        thread_down.start()

                        data_len = len(data)
                        L_fragment = random.randint(25, data_len // 3)
                        fragment_sleep = 0.0025974025974026 * L_fragment
                        send_data_in_fragment(data,backend_sock,L_fragment,fragment_sleep)

                    else:
                        raise Exception('cli syn close')

                else:
                    data = client_sock.recv(4096)
                    if data:
                        backend_sock.sendall(data)
                    else:
                        raise Exception('cli pipe close')

            except Exception as e:
                time.sleep(2)
                client_sock.close()
                backend_sock.close()
                return False

    def my_downstream(self, backend_sock , client_sock):
        first_flag = True
        while True:
            try:
                if( first_flag == True ):
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
                time.sleep(2)
                backend_sock.close()
                client_sock.close()
                return False

def send_data_in_fragment(data , sock , L_fragment , fragment_sleep):
    for i in range(0, len(data), L_fragment):
        fragment_data = data[i:i+L_fragment]
        print('send ',len(fragment_data),' bytes')
        # sock.send(fragment_data)
        sock.sendall(fragment_data)
        time.sleep(fragment_sleep)
        print('----------finish------------')
