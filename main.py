import kivy
import os
import requests
import json
import socket
import random
import threading
from pathlib import Path
import copy
import time
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout


class Application(App):
    def build(self):
        # Set up the main layout
        self.layout = BoxLayout(orientation='vertical')

        # Add the Listen Port fields
        listen_port_label = Label(text="Listen Port:")
        self.listen_port_entry = TextInput(multiline=False)
        self.layout.add_widget(listen_port_label)
        self.layout.add_widget(self.listen_port_entry)

        # Add the Cloudflare IP fields
        cloudflare_ip_label = Label(text="Cloudflare IP:")
        self.cloudflare_ip_dropdown = DropDown()
        operators = {
            "Automatic": "162.159.36.93",
            "Hamrah aval": "MCI",
            "Irancell": "MTN",
            "Rightel": "RTL",
            "Mokhaberat": "MKH",
            "HiWeb": "HWB",
            "Asiatek": "AST",
            "Shatel": "SHT",
            "ParsOnline": "PRS",
            "MobinNet": "MBT",
            "AndisheSabzKhazar": "ASK",
            "Respina": "RSP",
            "AfraNet": "AFN",
            "ZiTel": "ZTL",
            "Pishgaman": "PSM",
            "Arax": "ARX",
            "SamanTel": "SMT",
            "FanAva": "FNV",
            "DidebanNet": "DBN",
            "UpTel": "APT",
            "FanupTelecom": "FNP",
            "RayNet": "RYN",
            "Manual": "manual"
        }
        for operator in operators:
            btn = Button(text=operator, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.on_cloudflare_ip_select(btn.text))
            self.cloudflare_ip_dropdown.add_widget(btn)
        self.manual_input_layout = BoxLayout(orientation='vertical')
        self.manual_input_textinput = TextInput(multiline=False, hint_text="Enter one IP address")
        self.manual_input_layout.add_widget(self.manual_input_textinput)
        self.manual_input_layout.size_hint_y = None
        self.manual_input_layout.height = 0
        self.root = BoxLayout()
        self.root.add_widget(cloudflare_ip_label)
        self.root.add_widget(self.cloudflare_ip_dropdown)
        self.layout.add_widget(self.root)
        self.layout.add_widget(self.manual_input_layout)

        
        cloudflare_port_label = Label(text="Cloudflare Port:")
        self.cloudflare_port_entry = TextInput(multiline=False)
        self.layout.add_widget(cloudflare_port_label)
        self.layout.add_widget(self.cloudflare_port_entry)

        
        self.submit_button = Button(text='Submit', size_hint=(None, None), width=100, height=44)
        self.submit_button.bind(on_release=self.submit)
        self.layout.add_widget(self.submit_button)

        return self.layout

    def on_cloudflare_ip_select(self, selection):
        if selection == "Manual":
            self.manual_input_layout.size_hint_y = None
            self.manual_input_layout.height = 200
        elif selection == "Automatic":
            self.manual_input_layout.size_hint_y = None
            self.manual_input_layout.height = 0
        else:
            self.manual_input_layout.size_hint_y = None
            self.manual_input_layout.height = 0

    def submit(self, instance):
        
        listen_PORT = int(self.listen_port_entry.text)
        operator = self.cloudflare_ip_dropdown.button.text
        operator_code = operators.get(operator, '')
        if operator_code == "manual":
            Cloudflare_IP = self.manual_input_textinput.text.strip()
        elif operator_code == "162.159.36.93":
            Cloudflare_IP = "162.159.36.93"
        else:
            response = requests.get("https://raw.githubusercontent.com/yebekhe/cf-clean-ip-resolver/main/list.json")
            json_data = response.content
            Cloudflare_IP = self.choose_random_ip_with_operator(json_data, operator_code)
        Cloudflare_port = int(self.cloudflare_port_entry.text)

        if os.name == 'posix':
            print('os is linux')
            import resource   # ( -> pip install python-resources )
            soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_NOFILE)
            resource.setrlimit(resource.RLIMIT_NOFILE, (soft_limit, hard_limit))
            my_socket_timeout = 60
            first_time_sleep = 0.01 
            accept_time_sleep = 0.01 
            
                # Start server
            if not self.server_running:
                # Create instance of ThreadedServer and start listening on listen_PORT
                self.server = ThreadedServer('', listen_PORT, Cloudflare_IP, Cloudflare_port,
                                         timeout=SOCKET_TIMEOUT, sleep_time=SLEEP_TIME)
                self.server.start()
                self.server_running = True

                # Change text of Submit button to indicate that tunnel is active
                self.submit_button.text = 'Tunnel is active...'
                
    def stop_server(self):
        # Stop server
        if self.server_running:
            self.server.stop()
            self.server_running = False

            # Change text of Submit button back to 'Submit'
            self.submit_button.text = 'Submit'
    
    def check_server_status(self, instance):
        if self.server_running:
            self.stop_server()
        else:
            self.submit(instance)
            

    def choose_random_ip_with_operator(self, json_data, operator_code):
        data = json.loads(json_data)

        matching_ips = []
        for ipv4_address in data["ipv4"]:
            if ipv4_address["operator"] == operator_code:
                matching_ips.append(ipv4_address["ip"])

        matching_count = len(matching_ips)

        if matching_count > 0:
            random_index = random.randint(0, matching_count - 1)
            random_ip = matching_ips[random_index]
            return random_ip
        else:
            return None
            
class ThreadedServer(object):                        
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(128) 
        
        while True:
            client_sock , client_addr = self.sock.accept()                   
            client_sock.settimeout(my_socket_timeout)
            time.sleep(accept_time_sleep) 
            thread_up = threading.Thread(target = self.my_upstream , args =(client_sock,) )
            thread_up.daemon = True 
            thread_up.start()
            
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
                        backend_sock.connect((Cloudflare_IP,Cloudflare_port))
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
        sock.sendall(fragment_data)
        time.sleep(fragment_sleep)

    print('----------finish------------')
if name == 'main':
    Application().run()
