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

if os.name == 'posix':
    import resource
    soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_NOFILE)
    resource.setrlimit(resource.RLIMIT_NOFILE, (soft_limit, hard_limit))

KV = '''
ScrollView:
    MDFloatLayout:

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
            text: "Select your operator"
            on_release: app.menu.open()
            pos_hint: {'center_y': .55, "center_x": .5}
            size_hint_x: .8

        MDTextField:
            id: config_port_input
            hint_text: "Enter your config port"
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
           {"text": "Automatic", "on_release": lambda x="Automatic": self.set_item(x), "viewclass": "IconListItem", "height": dp(56)},
           {"text": "Hamrah-Aval", "on_release": lambda x="Hamrah-Aval": self.set_item(x), "viewclass": "IconListItem", "height": dp(56)},
           {"text": "Irancell", "on_release": lambda x="Irancell": self.set_item(x), "viewclass": "IconListItem", "height": dp(56)},
           {"text": "Rightel", "on_release": lambda x="Rightel": self.set_item(x), "viewclass": "IconListItem", "height": dp(56)},
           {"text": "Mokhaberat", "on_release": lambda x="Mokhaberat": self.set_item(x), "viewclass": "IconListItem", "height": dp(56)},
           {"text": "HiWeb", "on_release": lambda x="HiWeb": self.set_item(x), "viewclass": "IconListItem", "height": dp(56)},
           {"text": "AsiaTech", "on_release": lambda x="AsiaTech": self.set_item(x), "viewclass": "IconListItem", "height": dp(56)},
           {"text": "Shatel", "on_release": lambda x="Shatel": self.set_item(x), "viewclass": "IconListItem", "height": dp(56)},
           {"text": "ParsOnline", "on_release": lambda x="ParsOnline": self.set_item(x), "viewclass": "IconListItem", "height": dp(56)},
           {"text": "MobinNet", "on_release": lambda x="MobinNet": self.set_item(x), "viewclass": "IconListItem", "height": dp(56)},
           {"text": "Andishe-Sabz-Khazar", "on_release": lambda x="Andishe-Sabz-Khazar": self.set_item(x), "viewclass": "IconListItem", "height": dp(56)},
           {"text": "Respina", "on_release": lambda x="Respina": self.set_item(x), "viewclass": "IconListItem", "height": dp(56)},
           {"text": "AfraNet", "on_release": lambda x="AfraNet": self.set_item(x), "viewclass": "IconListItem", "height": dp(56)},
           {"text": "Zi-Tel", "on_release": lambda x="Zi-Tel": self.set_item(x), "viewclass": "IconListItem", "height": dp(56)},
           {"text": "Pishgaman", "on_release": lambda x="Pishgaman": self.set_item(x), "viewclass": "IconListItem", "height": dp(56)},
           {"text": "Araax", "on_release": lambda x="Araax": self.set_item(x), "viewclass": "IconListItem", "height": dp(56)},
           {"text": "SamanTel", "on_release": lambda x="SamanTel": self.set_item(x), "viewclass": "IconListItem", "height": dp(56)},
           {"text": "FanAva", "on_release": lambda x="FanAva": self.set_item(x), "viewclass": "IconListItem", "height": dp(56)},
           {"text": "DidebanNet", "on_release": lambda x="DidebanNet": self.set_item(x), "viewclass": "IconListItem", "height": dp(56)},
           {"text": "ApTel", "on_release": lambda x="ApTel": self.set_item(x), "viewclass": "IconListItem", "height": dp(56)},
           {"text": "Fanap-Telecom", "on_release": lambda x="Fanap-Telecom": self.set_item(x), "viewclass": "IconListItem", "height": dp(56)},
           {"text": "RayNet", "on_release": lambda x="RayNet": self.set_item(x), "viewclass": "IconListItem", "height": dp(56)}
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

    def send_data_in_fragment(self, data, sock):
        for i in range(0, len(data), self.L_fragment):
            fragment_data = data[i:i+self.L_fragment]
            logging.debug(f'[SEND] {len(fragment_data)} bytes')
            sock.sendall(fragment_data)
            time.sleep(self.fragment_sleep)
        logging.debug('[SEND] ----------finish------------')

    def my_upstream(self, client_sock):
        first_flag = True
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as backend_sock:
            backend_sock.settimeout(self.my_socket_timeout)
            while True:
                try:
                    if first_flag:
                        first_flag = False
                        time.sleep(self.first_time_sleep)
                        data = client_sock.recv(16384)
                        data_len = len(data)
                        self.L_fragment = random.randint(15, data_len // 3)
                        self.fragment_sleep = 0.0025974025974026 * self.L_fragment
                        if data:
                            backend_ip = self.get_next_backend_ip()

                            print(f'Using backend IP: {backend_ip}')  # Print the selected backend IP
                            backend_sock.connect((backend_ip, self.Cloudflare_port))
                            thread_down = threading.Thread(target=self.my_downstream, args=(backend_sock, client_sock))
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

    def my_downstream(self, backend_sock, client_sock):
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

    def set_item(self, text_item):
        self.screen.ids.operator_dropdown.set_item(text_item)
        self.menu.dismiss()

    def get_next_backend_ip(self):
        if self.user_operator == "AUTO":
            self.OP = ['MCI', 'MTN', 'RTL', 'MKH']
            self.chosen_OP = random.choice(self.OP)
            selected_ip = self.choose_random_ip_with_operator(self.chosen_OP)
        else :
            selected_ip = self.choose_random_ip_with_operator(self.user_operator)
        return selected_ip

    def choose_random_ip_with_operator(self, operator_code):
        response = UrlRequest("https://raw.githubusercontent.com/yebekhe/cf-clean-ip-resolver/main/list.json")
        while not response.is_finished:
            sleep(1)
            Clock.tick()

        json_data = response.result
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

    def _start_tunnel(self):
        while self.condition_of_tunnel == True :
            self.my_socket_timeout = 60
            self.first_time_sleep = 0.01
            self.accept_time_sleep = 0.01
            self.listen_PORT = int(self.screen.ids.local_port_input.text)
            user_operator_full = self.screen.ids.operator_dropdown.current_item
            operators = {
                "Automatic" : "AUTO",
                "Hamrah-Aval": "MCI",
                "Irancell": "MTN",
                "Rightel": "RTL",
                "Mokhaberat": "MKH",
                "HiWeb": "HWB",
                "AsiaTech": "AST",
                "Shatel": "SHT",
                "ParsOnline": "PRS",
                "MobinNet": "MBT",
                "Andishe-Sabz-Khazar": "ASK",
                "Respina": "RSP",
                "AfraNet": "AFN",
                "Zi-Tel": "ZTL",
                "Pishgaman": "PSM",
                "Araax": "ARX",
                "SamanTel": "SMT",
                "FanAva": "FNV",
                "DidebanNet": "DBN",
                "ApTel": "APT",
                "Fanap-Telecom": "FNP",
                "RayNet": "RYN"
            }
            self.user_operator = operators.get(user_operator_full)
            self.Cloudflare_port = int(self.screen.ids.config_port_input.text)
            update_text(f'Proxy server listening on 127.0.0.1:{self.listen_PORT}')
            print(f'Proxy server listening on 127.0.0.1:{self.listen_PORT}')
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

MainApp().run()
