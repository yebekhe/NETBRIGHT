import json
import random
import time
import socket
import threading
import os
import sys
import argparse
import logging
import multiprocessing
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivy.lang.builder import Builder
from kivy.properties import StringProperty
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.bottomnavigation import MDBottomNavigation
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivy.uix.scrollview import ScrollView
from kivymd.uix.floatlayout import MDFloatLayout

if os.name == 'posix':
    import resource
    soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_NOFILE)
    resource.setrlimit(resource.RLIMIT_NOFILE, (soft_limit, hard_limit))

KV = '''
ScrollView:
    MDBottomNavigation:
        MDBottomNavigationItem:
            name: 'home'
            text: 'Home'
            icon: 'home'

            MDFloatLayout:
                id: float_layout

                MDLabel:
                    halign: 'center'
                    markup: True
                    text: "[color=#ff9800][b]DPI Tunnel[/b][/color]"
                    pos_hint: {'center_y': .8, "center_x": .5}
                    font_size: self.height * 0.08
                    size_hint_x: .8

                MDTextField:
                    id: local_port_input
                    hint_text: "Local Port"
                    helper_text: "Listening from 127.0.0.1 to this port"
                    helper_text_mode: "on_focus"
                    pos_hint: {'center_y': .65, "center_x": .5}
                    size_hint_x: .8

                MDDropDownItem:
                    id: operator_dropdown
                    text: "Connection Type"
                    on_release: app.menu.open()
                    pos_hint: {'center_y': .55, "center_x": .5}
                    size_hint_x: .8

                MDTextField:
                    id: manual_ip_input
                    hint_text: "Cloudflare IP"
                    helper_text: "I will use this IP for connection to Cloudflare"
                    helper_text_mode: "on_focus"
                    pos_hint: {'center_y': 0, "center_x": 0}
                    size_hint: (None, None)
                    opacity: 0

                MDTextField:
                    id: config_port_input
                    hint_text: "Config Port"
                    helper_text: "Set 443 if you're using GetAfreeNode"
                    helper_text_mode: "on_focus"
                    pos_hint: {'center_y': .45, "center_x": .5}
                    size_hint_x: .8

                MDRaisedButton:
                    id: start_button
                    text: "Start Tunnel"
                    md_bg_color: "#ff9800"
                    elevation_normal: 8
                    on_press: app.start_tunnel()
                    pos_hint: {'center_y': .3, "center_x": .5}
                    size_hint_x: .8

        MDBottomNavigationItem:
            name: 'how_to_use'
            text: 'How to Use?'
            icon: 'help'

            MDFloatLayout:
                id: float_layout

                MDLabel:
                    halign: 'center'
                    markup: True
                    text: "[color=#ff9800][b]How to Use?[/b][/color]"
                    font_size: self.height * 0.08
                    pos_hint: {'center_y': .8, "center_x": .5}
                    size_hint_x: .8

                MDTextField:
                    id: how_to_use_textfield
                    multiline: True
                    readonly: True
                    text: "1.Enter your desired port in the Local Port field.\\n2.Select your Connection Type the dropdown menu.\\n3.Enter your Cloudflare IP address if selected Manual in previous step.\\n4.Enter your Config Port in last field.\\n5.Click the Start Tunnel! button to start the tunnel.\\n6.To stop the tunnel, Close app completely."
                    pos_hint: {'center_y': 0.5, "center_x": .5}
                    size_hint: (0.9, None)
                    height: dp(200)

<IconListItem>:
    IconLeftWidget:
        icon: root.icon
        width: dp(50)

'''
host = ''
port = None 
listen_port = None
user_operator = None
clouflare_ip = None
cloudflare_port = None
my_socket_timeout = 21
first_time_sleep = 0.1
accept_time_sleep = 0.01

class IconListItem(OneLineIconListItem):
    icon = StringProperty()

class MainApp(MDApp):
    def __init__(self, **kwargs):
        self.condition_of_tunnel = False
        super().__init__(**kwargs)
        self.screen = Builder.load_string(KV)
        menu_items = [
           {"text": "Load Balance", "on_release": lambda x="Load Balance": self.set_item(x), "viewclass": "IconListItem", "height": dp(56)},
           {"text": "Manual", "on_release": lambda x="Manual": self.set_item(x), "viewclass": "IconListItem", "height": dp(56)}
        ]
        self.menu = MDDropdownMenu(
            caller=self.screen.ids.operator_dropdown,
            items=menu_items,
            position="center",
            width_mult=4
        )
        self.menu.bind()

    def build(self):
        return self.screen

    def set_item(self, text_item):
        self.screen.ids.operator_dropdown.set_item(text_item)
        self.menu.dismiss()
        if self.screen.ids.operator_dropdown.current_item == "Manual" :
            self.screen.ids.manual_ip_input.pos_hint = {'center_y': .45, "center_x": .5}
            self.screen.ids.manual_ip_input.size_hint = (0.8 , 0.115)
            self.screen.ids.manual_ip_input.opacity = 1
            self.screen.ids.config_port_input.pos_hint = {'center_y': .35, "center_x": .5}
            self.screen.ids.start_button.pos_hint = {'center_y': .2, "center_x": .5}
        else :
            self.screen.ids.manual_ip_input.pos_hint = {'center_y': 0, "center_x": 0}
            self.screen.ids.manual_ip_input.size_hint = (None , None)
            self.screen.ids.manual_ip_input.opacity = 0
            self.screen.ids.config_port_input.pos_hint = {'center_y': .45, "center_x": .5}
            self.screen.ids.start_button.pos_hint = {'center_y': .3, "center_x": .5}

    def choose_random_ips(self):
        OP = ['MCI', 'MTN', 'RTL', 'MKH', 'HWB' , 'SHT']
        response = UrlRequest("https://raw.githubusercontent.com/yebekhe/cf-clean-ip-resolver/main/list.json")
        while not response.is_finished:
            sleep(1)
            Clock.tick()

        json_data = response.result
        data = json.loads(json_data)
        all_ips = []
        for op in OP:
            matching_ips = [ipv4_address["ip"] for ipv4_address in data["ipv4"] if ipv4_address["operator"] == op]
            all_ips.extend(matching_ips)

        random_indexes = random.sample(range(len(all_ips)), 20)
        random_ips = [all_ips[idx] for idx in random_indexes]
        return random_ips

    def start_tunnel(self):
        if self.condition_of_tunnel == False :
             self.condition_of_tunnel = True
             self.screen.ids.start_button.text = 'Stop Tunnel!'
             print(f'Tunnel Started!')
             t = threading.Thread(target=self._start_tunnel)
             t.daemon = True
             t.start()
        else :
             self.condition_of_tunnel = False
             self.screen.ids.start_button.text = 'Start Tunnel!'
             time.sleep(2)
             print(f'Tunnel Stopped!')
             

    def _start_tunnel(self):
        global my_socket_timeout
        global first_time_sleep
        global accept_time_sleep
        global listen_port
        global user_operator
        global clouflare_ip
        global cloudflare_port

        listen_port = int(self.screen.ids.local_port_input.text)
        user_operator_full = self.screen.ids.operator_dropdown.current_item
        operators = {
            "Load Balance" : "auto",
            "Manual": "manual"
        }
        user_operator = operators.get(user_operator_full)
        if user_operator == "auto":
            clouflare_ip = self.choose_random_ips()
        else :
            clouflare_ip = str(self.screen.ids.manual_ip_input.text)
        cloudflare_port = int(self.screen.ids.config_port_input.text)

        print(f'Proxy server listening on 127.0.0.1:{listen_port}')

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_sock.bind(('', listen_port))
            max_queue_size = socket.SOMAXCONN // 2
            print(f'max_queue_size: {max_queue_size}')
            server_sock.listen(max_queue_size)
            max_workers = multiprocessing.cpu_count() * 50
            print(f'max_workers: {max_workers}')

            while self.condition_of_tunnel == True:
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    client_sock, client_addr = server_sock.accept()
                    client_sock.settimeout(my_socket_timeout)
                    time.sleep(accept_time_sleep)
                    executor.submit(my_upstream(client_sock))

def get_next_backend_ip():
        if user_operator == "auto":
            selected_ip = random.choice(clouflare_ip)
        else :
            selected_ip = clouflare_ip
        return selected_ip

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
                            backend_sock.connect((backend_ip, cloudflare_port))
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

def send_data_in_fragment(data, sock):
    num_fragment = 67
    fragment_sleep = 0.001
    L_data = len(data)
    indices = random.sample(range(1,L_data-1), num_fragment-1)
    indices.sort()
    print('indices=',indices)
    i_pre=0
    for i in indices:
        fragment_data = data[i_pre:i]
        i_pre=i
        sock.sendall(fragment_data)
        time.sleep(fragment_sleep)
    fragment_data = data[i_pre:L_data]
    sock.sendall(fragment_data)
    print('----------finish------------')

MainApp().run()
