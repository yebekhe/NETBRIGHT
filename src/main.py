import subprocess
import json
import random
import time
import socket
import threading
from concurrent.futures import ThreadPoolExecutor
import os
import sys
import argparse
import logging
from time import sleep
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
from kivy.uix.screenmanager import ScreenManager, Screen

if os.name == 'posix':
    import resource
    soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_NOFILE)
    resource.setrlimit(resource.RLIMIT_NOFILE, (soft_limit, hard_limit))

KV = '''
ScrollView:
    MDFloatLayout:
        id: float_layout

        MDLabel:
            halign: 'center'
            markup: True
            text: "[color=#ff9800][size=60][b]DPI Tunnel[/b][/size][/color]"
            pos_hint: {'center_y': .8, "center_x": .5}

        MDTextField:
            id: local_port_input
            hint_text: "Enter your desired local port"
            helper_text: "Listening from localhost or 127.0.0.1 to this port"
            helper_text_mode: "on_focus"
            pos_hint: {'center_y': .65, "center_x": .5}
            size_hint_x: .8

        MDDropDownItem:
            id: operator_dropdown
            text: "Choose IP selection type"
            on_release: app.menu.open()
            pos_hint: {'center_y': .55, "center_x": .5}
            size_hint_x: .8

        MDTextField:
            id: manual_ip_input
            hint_text: "Enter your desired Cloudfalre IP"
            helper_text: "I will use this ip for connection to clouflare"
            helper_text_mode: "on_focus"
            pos_hint: {'center_y': .45, "center_x": .5}
            size_hint_x: .8
            opacity: 0

        MDTextField:
            id: config_port_input
            hint_text: "Enter your config port"
            helper_text: "Set 443 if you're using GetAfreeNode"
            helper_text_mode: "on_focus"
            pos_hint: {'center_y': .35, "center_x": .5}
            size_hint_x: .8

        MDRaisedButton:
            id: start_button
            text: "Start Tunnel"
            md_bg_color: "#ff9800"
            elevation_normal: 8
            on_press: app.start_tunnel()
            pos_hint: {'center_y': .2, "center_x": .5}
            size_hint_x: .8

<IconListItem>:
    IconLeftWidget:
        icon: root.icon
        width: dp(50)

'''

class IconListItem(OneLineIconListItem):
    icon = StringProperty()

class MainApp(MDApp):
    def __init__(self, **kwargs):
        self.condition_of_tunnel = False
        self.server = None
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

    def my_upstream(self, client_sock):
        first_flag = True
        backend_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backend_sock.settimeout(self.my_socket_timeout)
        backend_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        while True:
            try:
                if( first_flag == True ):
                    first_flag = False

                    time.sleep(self.first_time_sleep)   # speed control + waiting for packet to fully recieve
                    data = client_sock.recv(16384)

                    if data:
                        backend_ip = self.get_next_backend_ip()
                        print(f'Using backend IP: {backend_ip}')  # Print the selected backend IP
                        backend_sock.connect((backend_ip,self.Cloudflare_port))
                        thread_down = threading.Thread(target = self.my_downstream , args = (backend_sock , client_sock) )
                        thread_down.daemon = True
                        thread_down.start()
                        # backend_sock.sendall(data)
                        send_data_in_fragment(data,backend_sock)

                    else:
                        raise Exception('cli syn close')

                else:
                    data = client_sock.recv(16384)
                    if data:
                        backend_sock.sendall(data)
                    else:
                        raise Exception('cli pipe close')

            except Exception as e:
                #print('upstream : '+ repr(e) )
                time.sleep(2) # wait two second for another thread to flush
                client_sock.close()
                backend_sock.close()
                return False

    def my_downstream(self, backend_sock, client_sock):
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
                #print('downstream '+backend_name +' : '+ repr(e))
                time.sleep(2) # wait two second for another thread to flush
                backend_sock.close()
                client_sock.close()
                return False

    def set_item(self, text_item):
        self.screen.ids.operator_dropdown.set_item(text_item)
        self.menu.dismiss()
        if self.screen.ids.operator_dropdown.current_item == "Manual" :
            self.screen.ids.manual_ip_input.opacity = 1
        else :
            self.screen.ids.manual_ip_input.opacity = 0

    def get_next_backend_ip(self):
        if self.user_operator == "auto":
            selected_ip = random.choice(self.automatic_ip)
        else :
            selected_ip = self.manual_selected_ip
        return selected_ip

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
             t = threading.Thread(target=self._start_tunnel)
             t.daemon = True
             t.start()
        else :
             self.condition_of_tunnel = False
             self.screen.ids.start_button.text = 'Start Tunnel!'
             print(f'Tunnel Stopped!')
             self.restart()

    def _start_tunnel(self):
        self.my_socket_timeout = 21
        self.first_time_sleep = 0.1
        self.accept_time_sleep = 0.01
        self.listen_PORT = int(self.screen.ids.local_port_input.text)
        user_operator_full = self.screen.ids.operator_dropdown.current_item
        operators = {
            "Load Balance" : "auto",
            "Manual": "manual"
        }
        self.user_operator = operators.get(user_operator_full)
        if self.user_operator == "auto":
            self.automatic_ip = self.choose_random_ips()
        else :
            self.manual_selected_ip = str(self.screen.ids.manual_ip_input.text)
        self.Cloudflare_port = int(self.screen.ids.config_port_input.text)

        print(f'Proxy server listening on 127.0.0.1:{self.listen_PORT}')

        while self.condition_of_tunnel == True :
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
                server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_sock.bind(('', self.listen_PORT))
                server_sock.listen(128)

                with ThreadPoolExecutor(max_workers=128) as executor:
                    while True:
                        client_sock, client_addr = server_sock.accept()
                        client_sock.settimeout(self.my_socket_timeout)
                        time.sleep(self.accept_time_sleep)
                        executor.submit(self.my_upstream, client_sock)

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
