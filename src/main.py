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
import re
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
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

KV = '''
ScrollView:
    md_bg_color: app.theme_cls.bg_light
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
                    text: "[b]NETBRIGHT[/b]"
                    theme_text_color: "Custom"
                    text_color: app.theme_cls.primary_color
                    pos_hint: {'center_y': .9, "center_x": .5}
                    font_size: self.height * 0.08
                    size_hint_x: .9

                MDRoundFlatButton:
                    id: start_button
                    text: "[b]Start Tunnel[/b]"
                    font_size: self.height * 0.25
                    text_color: app.theme_cls.bg_light
                    md_bg_color: app.theme_cls.primary_color
                    elevation_normal: 8
                    on_press: app.start_tunnel()
                    pos_hint: {'center_y': .5, "center_x": .5}
                    size_hint: (.8, .2)
                    

        MDBottomNavigationItem:
            name: 'how_to_use'
            text: 'HOW TO USE?'
            icon: 'help'

            MDFloatLayout:
                id: float_layout

                MDLabel:
                    halign: 'center'
                    markup: True
                    text: "[b]HOW TO USE?[/b]"
                    theme_text_color: "Custom"
                    text_color: app.theme_cls.primary_color
                    font_size: self.height * 0.08
                    pos_hint: {'center_y': .9, "center_x": .5}
                    size_hint_x: .9

                MDTextField:
                    id: how_to_use_textfield
                    multiline: True
                    readonly: True
                    text: "1.Enter your desired port in the Local Port field.\\n2.Select your Connection Type from the Drop-Down menu.\\n3.Enter your Cloudflare IP address (only if you selected Manual in previous step).\\n4.Enter your Config Port in last field.\\n5.Click the Start Tunnel! button to start the tunnel.\\n6.To stop the tunnel, Close app completely.\\n\\nNOTE: Don't Forget to bypass NETBRIGHT from any v2ray client you want to use!"
                    text_color_normal:app.theme_cls.opposite_bg_light
                    text_color_focus:app.theme_cls.primary_color
                    hint_text_color_normal: app.theme_cls.opposite_bg_light
                    hint_text_color_focus: app.theme_cls.primary_color
                    helper_text_color_normal: app.theme_cls.opposite_bg_light
                    helper_text_color_focus: app.theme_cls.primary_color
                    background_color: app.theme_cls.bg_light
                    line_color_normal: app.theme_cls.opposite_bg_light
                    line_color_focus: app.theme_cls.primary_color
                    pos_hint: {'center_y': 0.5, "center_x": .5}
                    size_hint: (0.9, None)
                    height: dp(200)
        
        MDBottomNavigationItem:
            name: 'setting'
            text: 'SETTING'
            icon: 'account-settings'

            MDFloatLayout:
                id: float_layout

                MDLabel:
                    halign: 'center'
                    markup: True
                    text: "[b]SETTING[/b]"
                    theme_text_color: "Custom"
                    text_color: app.theme_cls.primary_color
                    font_size: self.height * 0.08
                    pos_hint: {'center_y': .9, "center_x": .5}
                    size_hint_x: .9

                MDLabel:
                    halign: 'center'
                    markup: True
                    text: "Light/Dark"
                    theme_text_color: "Custom"
                    text_color: app.theme_cls.primary_color
                    font_size: self.height * 0.035
                    pos_hint: {'center_y': .75, "center_x": .25}
                    size_hint_x: .9

                MDIconButton:
                    icon: "theme-light-dark"
                    pos_hint: {"center_y": .75, "center_x": .75}
                    theme_icon_color: "Custom"
                    icon_color: app.theme_cls.primary_color
                    icon_size: "45sp"
                    on_press: app.light_dark()

                MDTextField:
                    id: local_port_input
                    hint_text: "Local Port"
                    helper_text: "Listening from 127.0.0.1 to this port"
                    helper_text_mode: "on_focus"
                    text_color_normal:app.theme_cls.opposite_bg_light
                    text_color_focus:app.theme_cls.primary_color
                    hint_text_color_normal: app.theme_cls.opposite_bg_light
                    hint_text_color_focus: app.theme_cls.primary_color
                    helper_text_color_normal: app.theme_cls.opposite_bg_light
                    helper_text_color_focus: app.theme_cls.primary_color
                    background_color: app.theme_cls.bg_light
                    line_color_normal: app.theme_cls.opposite_bg_light
                    line_color_focus: app.theme_cls.primary_color
                    pos_hint: {'center_y': .65, "center_x": .5}
                    size_hint_x: .8

                MDDropDownItem:
                    id: operator_dropdown
                    text: "Connection Type"
                    on_release: app.menu.open()
                    text_color: app.theme_cls.opposite_bg_light
                    md_bg_color: app.theme_cls.bg_light
                    pos_hint: {'center_y': .55, "center_x": .5}
                    size_hint_x: .8

                MDTextField:
                    id: manual_ip_input
                    hint_text: "Cloudflare IP"
                    helper_text: "I will use this IP for connection to Cloudflare"
                    helper_text_mode: "on_focus"
                    text_color_normal:app.theme_cls.opposite_bg_light
                    text_color_focus:app.theme_cls.primary_color
                    hint_text_color_normal: app.theme_cls.opposite_bg_light
                    hint_text_color_focus: app.theme_cls.primary_color
                    helper_text_color_normal: app.theme_cls.opposite_bg_light
                    helper_text_color_focus: app.theme_cls.primary_color
                    background_color: app.theme_cls.bg_light
                    line_color_normal: app.theme_cls.opposite_bg_light
                    line_color_focus: app.theme_cls.primary_color
                    pos_hint: {'center_y': 0, "center_x": 0}
                    size_hint: (None, None)
                    opacity: 0

                MDTextField:
                    id: config_port_input
                    hint_text: "Config Port"
                    helper_text: "Set 443 if you're using GetAfreeNode"
                    helper_text_mode: "on_focus"
                    text_color_normal:app.theme_cls.opposite_bg_light
                    text_color_focus:app.theme_cls.primary_color
                    hint_text_color_normal: app.theme_cls.opposite_bg_light
                    hint_text_color_focus: app.theme_cls.primary_color
                    helper_text_color_normal: app.theme_cls.opposite_bg_light
                    helper_text_color_focus: app.theme_cls.primary_color
                    background_color: app.theme_cls.bg_light
                    line_color_normal: app.theme_cls.opposite_bg_light
                    line_color_focus: app.theme_cls.primary_color
                    pos_hint: {'center_y': .45, "center_x": .5}
                    size_hint_x: .8

                MDRaisedButton:
                    id: save_button
                    text: "Save Settings"
                    text_color: app.theme_cls.bg_light
                    md_bg_color: app.theme_cls.primary_color
                    elevation_normal: 8
                    on_press: app.save_config()
                    pos_hint: {'center_y': .2, "center_x": .5}
                    size_hint_x: .8

<IconListItem>:
    IconLeftWidgetWithoutTouch:
        icon: root.icon
        width: dp(0)

'''

class IconListItem(OneLineIconListItem):
    icon = StringProperty()

class MainApp(MDApp):
    def __init__(self, **kwargs):
        self.condition_of_tunnel = False
        self.dialog = None
        self.error = None
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
            radius=[24, 0, 24, 0],
            width_mult=10,
            hor_growth="left",
            
        )
        self.menu.bind()
        args = self.parse_args()
        config = configparser.ConfigParser()
        config.read(args.config)

        self.user_operator = str(config.get('settings', 'user_operator'))
        self.listen_PORT = int(config.get('settings', 'listen_PORT'))
        self.Cloudflare_IPs = [ip.strip() for ip in config.get('settings', 'Cloudflare_IP').split(',')]
        self.Cloudflare_port = int(config.get('settings', 'Cloudflare_port'))
        self.my_socket_timeout = int(config.get('settings', 'my_socket_timeout'))
        self.first_time_sleep = float(config.get('settings', 'first_time_sleep'))
        self.accept_time_sleep = float(config.get('settings', 'accept_time_sleep'))
        self.theme_cls.primary_palette = str(config.get('settings', 'primary_palette'))
        self.theme_cls.theme_style = str(config.get('settings', 'theme_style'))


        self.screen.ids.local_port_input.text = str(self.listen_PORT)
        self.screen.ids.config_port_input.text = str(self.Cloudflare_port)
        if self.user_operator == "auto":
           self.screen.ids.operator_dropdown.set_item("Load Balance")
           self.screen.ids.manual_ip_input.pos_hint = {'center_y': 0, "center_x": 0}
           self.screen.ids.manual_ip_input.size_hint = (None , None)
           self.screen.ids.manual_ip_input.opacity = 0
           self.screen.ids.config_port_input.pos_hint = {'center_y': .45, "center_x": .5}
           self.screen.ids.save_button.pos_hint = {'center_y': .3, "center_x": .5}
           

        else:
            self.screen.ids.manual_ip_input.text = str(self.Cloudflare_IPs[0])
            self.screen.ids.operator_dropdown.set_item("Manual")
            self.screen.ids.manual_ip_input.pos_hint = {'center_y': .45, "center_x": .5}
            self.screen.ids.manual_ip_input.size_hint =  self.screen.ids.config_port_input.size_hint
            self.screen.ids.manual_ip_input.opacity = 1
            self.screen.ids.config_port_input.pos_hint = {'center_y': .35, "center_x": .5}
            self.screen.ids.save_button.pos_hint = {'center_y': .2, "center_x": .5}

    def build(self):
        return self.screen

    def light_dark(self):
        self.theme_cls.primary_palette = (
            "Orange" if self.theme_cls.primary_palette == "Red" else "Red"
        )
        self.theme_cls.theme_style = (
            "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        )

    def set_item(self, text_item):
        self.screen.ids.operator_dropdown.set_item(text_item)
        self.menu.dismiss()
        if self.screen.ids.operator_dropdown.current_item == "Manual" :
            self.screen.ids.manual_ip_input.pos_hint = {'center_y': .45, "center_x": .5}
            self.screen.ids.manual_ip_input.size_hint =  self.screen.ids.config_port_input.size_hint
            self.screen.ids.manual_ip_input.opacity = 1
            self.screen.ids.config_port_input.pos_hint = {'center_y': .35, "center_x": .5}
            self.screen.ids.save_button.pos_hint = {'center_y': .1, "center_x": .5}
        else :
            self.screen.ids.manual_ip_input.pos_hint = {'center_y': 0, "center_x": 0}
            self.screen.ids.manual_ip_input.size_hint = (None , None)
            self.screen.ids.manual_ip_input.opacity = 0
            self.screen.ids.config_port_input.pos_hint = {'center_y': .45, "center_x": .5}
            self.screen.ids.save_button.pos_hint = {'center_y': .2, "center_x": .5}

    def choose_random_ips(self):
        try:
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
        except Exception as e:
            return Exception(e)
    
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
        config.set('settings', 'primary_palette', str(self.theme_cls.primary_palette))
        config.set('settings', 'theme_style', str(self.theme_cls.theme_style))

        with open(config_path, 'w') as config_file:
            config.write(config_file)

    def is_valid_ip(self, address):
        pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        match = re.match(pattern, address)
        if not match:
            return False
        octets = address.split('.')
        for octet in octets:
            if int(octet) > 255:
                return False
        return True

    def save_config(self):
        try:
            self.listen_PORT = int(self.screen.ids.local_port_input.text)
            user_operator_full = self.screen.ids.operator_dropdown.current_item
            operators = {
                "Load Balance" : "auto",
                "Manual": "manual"
            }
            self.user_operator = operators.get(user_operator_full)
            if self.user_operator == "auto":
                if self.choose_random_ips() == "the JSON object must be str, bytes or bytearray, not NoneType":
                    raise Exception("I can't get IPs from server , Check Your Internet Connection!")
                else:
                    self.Cloudflare_IPs = self.choose_random_ips()
            else :
                if self.is_valid_ip(str(self.screen.ids.manual_ip_input.text)):
                    self.Cloudflare_IPs = str(self.screen.ids.manual_ip_input.text)
                else:
                    raise Exception("Cloudflare IP is not valid!")
            self.Cloudflare_port = int(self.screen.ids.config_port_input.text)
            args = self.parse_args()
            self.write_config(args.config, self.user_operator, self.listen_PORT, self.Cloudflare_IPs, self.Cloudflare_port, self.my_socket_timeout, self.first_time_sleep, self.accept_time_sleep, self.condition_of_tunnel)
            self.dialog = MDDialog(
                title="Congrates!",
                text="Settings Saved Succesfully!",
                buttons=[
                    MDFlatButton(
                    text="OK",
                    on_release=lambda x: self.dialog.dismiss()
                    )
                ]
            )
            self.dialog.open()
        except Exception as e:
            self.error = MDDialog(
                title="Oops!",
                text=f"Some Went Wrong! {e}",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: self.error.dismiss()
                    )
                ]
            )
            self.error.open()
    def start_tunnel(self):
        try:
            if self.condition_of_tunnel == False :
                self.condition_of_tunnel = True
                self.screen.ids.start_button.text = '[b]Tunnel Started![/b]'
                print(f'Tunnel Started!')
                t = threading.Thread(target=dpitunnel.main)
                t.daemon = True
                t.start()
            else :
                self.error = MDDialog(
                    title="Tunnel is running!",
                    text="Tunnel is running , if you want terminate it , just close application completely!",
                    buttons=[
                        MDFlatButton(
                            text="OK",
                            on_release=lambda x: self.error.dismiss()
                        )
                    ]
                )
                self.error.open()
        except Exception as e:
            self.error = MDDialog(
                title="Tunnel is running!",
                text=f"Some Unexpected Error happend! {e}",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: self.error.dismiss()
                    )
                ]
            )
            self.error.open()

            
if __name__ == '__main__':
    MainApp().run()
