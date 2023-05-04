import json
import random
import time
import socket
import threading
import os
import sys
import argparse
import kivy
import kivymd
import configparser
import dpitunnel
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

class IconListItem(OneLineIconListItem):
    icon = StringProperty()

class MainApp(MDApp):
    def __init__(self, **kwargs):
        self.condition_of_tunnel = False
        self.server = None
        super().__init__(**kwargs)
        self.screen = Builder.load_string(KV)
        menu_items = [
           {"text": "Load Balance", "on_release": lambda x="Load Balance": self.set_item(x), "viewclass": "IconListItem", "height": dp(56), "icon": "tunnel"},
           {"text": "Manual", "on_release": lambda x="Manual": self.set_item(x), "viewclass": "IconListItem", "height": dp(56), "icon": "pencil-outline"}
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
        return ', '.join(random_ips)
    
    def parse_args(self):
        parser = argparse.ArgumentParser(description='Python Proxy')
        parser.add_argument('--config', type=str, default='config.ini', help='Path to the configuration file')
        return parser.parse_args()
    
    def write_config(self, config_path, user_operator, listen_PORT, Cloudflare_IPs, Cloudflare_port, my_socket_timeout, first_time_sleep, accept_time_sleep, condition_of_tunnel):
        config = configparser.ConfigParser()
        config.read(config_path)
        
        config.set('settings' , 'user_operator' , str(user_operator))
        config.set('settings', 'listen_PORT', str(listen_PORT))
        config.set('settings', 'Cloudflare_IP', str(Cloudflare_IPs))
        config.set('settings', 'Cloudflare_port', str(Cloudflare_port))
        config.set('settings', 'my_socket_timeout', str(my_socket_timeout))
        config.set('settings', 'first_time_sleep', str(first_time_sleep))
        config.set('settings', 'accept_time_sleep', str(accept_time_sleep))
        config.set('settings', 'condition_of_tunnel' , str(condition_of_tunnel))

        with open(config_path, 'w') as config_file:
            config.write(config_file)

    def start_tunnel(self):
        if self.condition_of_tunnel == False :
            self.condition_of_tunnel = True
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
                self.Cloudflare_IPs = self.choose_random_ips()
            else :
                self.Cloudflare_IPs = str(self.screen.ids.manual_ip_input.text)
            self.Cloudflare_port = int(self.screen.ids.config_port_input.text)
            args = self.parse_args()
            self.write_config(args.config, self.user_operator, self.listen_PORT, self.Cloudflare_IPs, self.Cloudflare_port, self.my_socket_timeout, self.first_time_sleep, self.accept_time_sleep, self.condition_of_tunnel)
            self.screen.ids.start_button.text = 'Tunnel Started!'
            print(f'Tunnel Started!')
            t = threading.Thread(target=dpitunnel.main)
            t.daemon = True
            t.start()
        else :
            self.condition_of_tunnel = False
            args = self.parse_args()
            self.write_config(args.config, '', '', '', '', self.my_socket_timeout, self.first_time_sleep, self.accept_time_sleep, self.condition_of_tunnel)
            self.screen.ids.start_button.text = 'Close app to Terminate Tunnel!'
            time.sleep(2)
            print(f'Tunnel Stopped!')

if __name__ == '__main__':
    MainApp().run()
