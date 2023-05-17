import json
import random
import time
import socket
import dns.resolver
import threading
import os
import sys
import argparse
import kivy
import kivymd
import configparser
import re
import dpitunnel
import shutil
import webbrowser
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from kivy.clock import Clock
from kivy.clock import mainthread
from kivy.network.urlrequest import UrlRequest
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivy.utils import platform
from kivy.lang.builder import Builder
from kivy.properties import StringProperty
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.bottomnavigation import MDBottomNavigation
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivy.uix.scrollview import ScrollView
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from android import loadingscreen
from plyer import notification
from plyer.platforms.android import activity, SDK_INT
import jnius
from jnius import autoclass, cast

Window.keyboard_anim_args = {'d': .2, 't': 'in_out_expo'}
Window.softinput_mode = "below_target"

KV = """
TheScreen:
    Main:
    Setting:

<Main>
    name: "Main"

    ScrollView:
        scroll_type: ["bars", "content"]
        MDGridLayout:
            cols: 1
            spacing: 0
            size_hint_y: None
            height: dp(700)

            MDTopAppBar:
                id: title_home
                title: "NetBright"
                right_action_items: [["cog", lambda x: app.callback(), "Open Setting"]]
                pos_hint: {"center_y": .96, "center_x": .5}
                md_bg_color: app.theme_cls.primary_color
                row: 1

            AnchorLayout:
                row: 2
                anchor_x: 'center'

                MDBoxLayout:
                    adaptive_size: True

                    MDIconButton:
                        id: start_button
                        icon: "toggle-switch-off-outline"
                        theme_icon_color: "Custom"
                        icon_color: app.theme_cls.primary_color
                        icon_size: "150sp"
                        on_press: app.start_tunnel()
                        pos_hint: { "center_y": .5}

            AnchorLayout:
                row: 3
                anchor_x: 'center'
                padding: [0,0,0,150]

                MDBoxLayout:
                    size_hint_y: None
                    height: root.height // 3
                    size_hint_x: None
                    width: root.width * 0.8

                    MDTextField:
                        id: log_textfield
                        multiline: True
                        readonly: True
                        mode: "rectangle"
                        active_line: False
                        hint_text: "Log"
                        font_name: "log.ttf"
                        text: ""
                        font_size: "12sp"
                        size_hint_y: None
                        height: root.height // 3
                        max_height: root.height // 3
                        text_color_normal:app.theme_cls.opposite_bg_light
                        text_color_focus:app.theme_cls.opposite_bg_light
                        hint_text_color_normal: app.theme_cls.opposite_bg_light
                        hint_text_color_focus: app.theme_cls.primary_color
                        helper_text_color_normal: app.theme_cls.opposite_bg_light
                        helper_text_color_focus: app.theme_cls.primary_color
                        background_color: app.theme_cls.bg_light
                        line_color_normal: app.theme_cls.opposite_bg_light
                        line_color_focus: app.theme_cls.primary_color
                        pos_hint: {'center_y': 0.5}


<Setting>
    name: "Setting"

    ScrollView:
        scroll_type: ["bars", "content"]
        MDGridLayout:
            cols: 1
            spacing: 15
            size_hint_y: None
            height: dp(700)

            MDTopAppBar:
                id: title_setting
                title: "Setting"
                left_action_items: [["arrow-left", lambda x: app.callback()]]
                pos_hint: {"center_y": .96, "center_x": .5}
                md_bg_color: app.theme_cls.primary_color

            AnchorLayout:
                
                anchor_x: 'center'
                adaptive_size: True

                MDBoxLayout:
                    orientation: "horizontal"
                    adaptive_width: True

                    MDLabel:
                        id: light_dark_label
                        halign: 'center'
                        markup: True
                        font_name: "Vazir.ttf"
                        text: "Light/Dark"
                        theme_text_color: "Custom"
                        text_color: app.theme_cls.opposite_bg_light
                        size_hint: None, None
                        pos_hint: {'center_y': 0.5}
                        size: dp(100),dp(50)

                    MDIconButton:
                        icon: "theme-light-dark"
                        theme_icon_color: "Custom"
                        icon_color: app.theme_cls.primary_color
                        icon_size: "45sp"
                        on_press: app.light_dark()
                        pos_hint: { "center_y": .5}

            AnchorLayout:
                
                anchor_x: 'center'
                adaptive_size: True

                MDBoxLayout:
                    orientation: "vertical"
                    size_hint_x: None
                    width: root.width * 0.8

                    MDTextField:
                        id: local_port_input
                        hint_text: "Local Port"
                        font_name: "Vazir.ttf"
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
                        pos_hint: {"center_y": .5}

            AnchorLayout:
                
                anchor_x: 'center'
                adaptive_size: True

                MDBoxLayout:
                    orientation: "vertical"
                    adaptive_height: True
                    size_hint_x: None
                    width: root.width * 0.8
                    spacing: 0

                    MDDropDownItem:
                        id: operator_dropdown
                        text: "Connection Type"
                        font_name: "Vazir.ttf"
                        on_release: app.menu.open()
                        text_color: app.theme_cls.opposite_bg_light
                        md_bg_color: app.theme_cls.bg_light
                        pos_hint: {'center_x': 0.5}

                    MDTextField:
                        id: manual_ip_input
                        hint_text: "Cloudflare IP/Domain"
                        font_name_hint_text: "Vazir.ttf"
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
                        opacity: 0

            AnchorLayout:
                
                anchor_x: 'center'
                adaptive_size: True

                MDBoxLayout:
                    orientation: "vertical"
                    size_hint_x: None
                    width: root.width * 0.8

                    MDTextField:
                        id: config_port_input
                        hint_text: "Cloudflare Port"
                        font_name: "Vazir.ttf"
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
                        pos_hint: { "center_y": .5}

            AnchorLayout:
                
                anchor_x: 'center'
                adaptive_size: True

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_x: None
                    width: root.width * 0.5
                    spacing: 0

                    MDLabel:
                        id: random_fragment_label
                        halign: 'center'
                        markup: True
                        font_name: "Vazir.ttf"
                        text: "Random Fragment"
                        theme_text_color: "Custom"
                        text_color: app.theme_cls.opposite_bg_light
                        width: root.width * 0.1
                        pos_hint: { "center_y": .5}

                    MDCheckbox:
                        id: random_fragment_check
                        color_inactive:app.theme_cls.opposite_bg_light
                        color_active:app.theme_cls.primary_color
                        size_hint: None, None
                        size: dp(48), dp(48)
                        pos_hint: { "center_y": .5}

            AnchorLayout:
                
                anchor_x: 'center'
                adaptive_size: True

                MDBoxLayout:
                    orientation: "horizontal"
                    adaptive_width: True
                    spacing: 10

                    MDTextField:
                        id: socket_timeout_input
                        hint_text: "Socket Timeout"
                        font_name: "Vazir.ttf"
                        helper_text: "20-100"
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
                        size_hint: None, None
                        size: root.width * 0.35 , dp(65)


                    MDTextField:
                        id: socket_listen_input
                        hint_text: "Socket Listen Queue"
                        helper_text: ">= 128"
                        font_name: "Vazir.ttf"
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
                        size_hint: None, None
                        size: root.width * 0.35, dp(65)

            AnchorLayout:
                
                anchor_x: 'center'
                adaptive_size: True

                MDBoxLayout:
                    adaptive_width: True
                    padding: [0,0,0,50]

                    MDRaisedButton:
                        id: save_button
                        text: "Save Settings"
                        font_name: "Vazir.ttf"
                        text_color: app.theme_cls.bg_light
                        md_bg_color: app.theme_cls.primary_color
                        elevation_normal: 8
                        on_press: app.save_config()
                        pos_hint: {'center_x': .5}


<IconListItem>:
    IconLeftWidgetWithoutTouch:
        icon: root.icon
        width: dp(0)
"""

class TheScreen(ScreenManager):
    pass

class Main(Screen):
    pass

class Setting(Screen):
    pass

class IconListItem(OneLineIconListItem):
    icon = StringProperty()


PythonActivity = autoclass('org.kivy.android.PythonActivity')
AndroidString = autoclass('java.lang.String')
NotificationBuilder = autoclass('android.app.Notification$Builder')

def show_notification():
    context = PythonActivity.mActivity
    noti = NotificationBuilder(context)
    noti.setContentTitle(AndroidString("NetBright"))
    noti.setContentText(AndroidString("NetBright is running..."))
    noti.setAutoCancel(False)
    noti.setOngoing(True)
    nm = context.getSystemService(context.NOTIFICATION_SERVICE)
    nm.notify(0, noti.build())

def cancel_notification():
    context = PythonActivity.mActivity
    nm = context.getSystemService(context.NOTIFICATION_SERVICE)
    nm.cancel(0)

class MainApp(MDApp):
    def __init__(self, **kwargs):
        self.condition_of_tunnel = False
        self.dialog = None
        self.error = None
        self.prev_line = ""
        self.app_start = 0

        if os.path.exists("log_data.txt"):
            os.remove("log_data.txt")
        else:
            pass

        super().__init__(**kwargs)
        self.theme_cls.material_style = "M2"
        self.screen = Builder.load_string(KV)
        self.screen.get_screen("Main")

        if os.name == 'posix':
            print('os is linux')
            import resource
            soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_NOFILE)
            resource.setrlimit(resource.RLIMIT_NOFILE, (soft_limit, hard_limit))

        menu_items = [
            {
                "text": "Load Balance",
                "on_release": lambda x="Load Balance": self.set_item(x),
                "viewclass": "IconListItem",
                "height": dp(56),
                "icon": "scale-balance",
            },
            {
                "text": "Manual",
                "on_release": lambda x="Manual": self.set_item(x),
                "viewclass": "IconListItem",
                "height": dp(56),
                "icon": "pencil-outline",
            },

        ]
        self.menu = MDDropdownMenu(
            caller=self.screen.get_screen("Setting").ids.operator_dropdown,
            items=menu_items,
            position="center",
            radius=[24, 0, 24, 0],
            width_mult=5,
            hor_growth="right",
        )
        self.menu.bind()
        args = self.parse_args()
        config = configparser.ConfigParser()
        config.read(args.config)

        self.user_operator = str(config.get("settings", "user_operator"))
        self.listen_PORT = int(config.get("settings", "listen_PORT"))
        self.Cloudflare_IPs = [
            ip.strip() for ip in config.get("settings", "Cloudflare_IP").split(",")
        ]
        self.Cloudflare_port = int(config.get("settings", "Cloudflare_port"))
        self.my_socket_timeout = int(config.get("settings", "my_socket_timeout"))
        self.first_time_sleep = float(config.get("settings", "first_time_sleep"))
        self.accept_time_sleep = float(config.get("settings", "accept_time_sleep"))
        self.theme_cls.primary_palette = str(config.get("settings", "primary_palette"))
        self.theme_cls.theme_style = str(config.get("settings", "theme_style"))
        self.random_fragment = str(config.get("settings", "random_fragment"))
        self.socket_listen = int(config.get("settings", "socket_listen"))
        self.domain_addr = str(config.get("settings", "domain_addr"))

        self.screen.get_screen("Setting").ids.local_port_input.text = str(self.listen_PORT)
        self.screen.get_screen("Setting").ids.config_port_input.text = str(self.Cloudflare_port)
        self.screen.get_screen("Setting").ids.socket_timeout_input.text = str(self.my_socket_timeout)
        self.screen.get_screen("Setting").ids.socket_listen_input.text = str(self.socket_listen)
        if self.random_fragment == "normal":
            self.screen.get_screen("Setting").ids.random_fragment_check.state = "normal"
        else:
            self.screen.get_screen("Setting").ids.random_fragment_check.state = "down"

        if self.user_operator == "auto":
            self.screen.get_screen("Setting").ids.operator_dropdown.set_item("Load Balance")
            self.screen.get_screen("Setting").ids.operator_dropdown.width = self.screen.get_screen("Setting").width * 0.8
            self.screen.get_screen("Setting").ids.manual_ip_input.opacity = 0
            self.screen.get_screen("Setting").ids.manual_ip_input.width = 0
        else:
            if self.domain_addr != "None":
                self.screen.get_screen("Setting").ids.manual_ip_input.text = self.domain_addr
            else:
                self.screen.get_screen("Setting").ids.manual_ip_input.text = ",".join(self.Cloudflare_IPs)
            self.screen.get_screen("Setting").ids.operator_dropdown.set_item("Manual")
            self.screen.get_screen("Setting").ids.operator_dropdown.width = self.screen.get_screen("Setting").width * 0.8
            self.screen.get_screen("Setting").ids.manual_ip_input.opacity = 1
            self.screen.get_screen("Setting").ids.manual_ip_input.width = self.screen.get_screen("Setting").width * 0.8

    def callback(self):
        if self.screen.current == "Main":
            self.screen.current = "Setting"
        else:
            self.screen.current = "Main"

    def build(self):
        Window.bind(on_keyboard=self.key_input)
        loadingscreen.hide_loading_screen()
        f = open("log_data.txt", "a")
        f.close()
        thread_log = threading.Thread(target = self.update_log)
        thread_log.daemon = True
        thread_log.start()
        self.update_log_textfield("Developer => YeBeKhe\n")
        self.update_log_textfield("Twitter => twitter.com/yebekhe\n")
        return self.screen
    
    def on_pause(self): 
        return True

    def on_resume(self):
        pass


    def light_dark(self):
        self.theme_cls.primary_palette = (
            "Orange" if self.theme_cls.primary_palette == "Red" else "Red"
        )
        self.theme_cls.theme_style = (
            "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        )

    @mainthread
    def update_log_textfield(self, line):
        lines = self.screen.get_screen("Main").ids.log_textfield.text.splitlines()
        if len(lines) > 250:
            self.screen.get_screen("Main").ids.log_textfield.text = ""
        self.screen.get_screen("Main").ids.log_textfield.text += f"{line}\n"

    def update_log(self):
        while True:
            with open("log_data.txt", "r") as f:
                for line in f:
                    if (
                        "[UPSTREAM]"
                        in line
                        or "[DOWNSTREAM]"
                        in line
                    ):
                        break
                    else:
                        if line != self.prev_line:
                            self.update_log_textfield(line)
                            self.prev_line = line
                            break

    def set_item(self, text_item):
        self.screen.get_screen("Setting").ids.operator_dropdown.set_item(text_item)
        self.menu.dismiss()
        if self.screen.get_screen("Setting").ids.operator_dropdown.current_item == "Manual":
            self.screen.get_screen("Setting").ids.operator_dropdown.width = self.screen.get_screen("Setting").width * 0.8
            self.screen.get_screen("Setting").ids.manual_ip_input.width = self.screen.get_screen("Setting").width * 0.8
            self.screen.get_screen("Setting").ids.manual_ip_input.opacity = 1
        else:
            self.screen.get_screen("Setting").ids.operator_dropdown.width = self.screen.get_screen("Setting").width * 0.8
            self.screen.get_screen("Setting").ids.manual_ip_input.width = 0
            self.screen.get_screen("Setting").ids.manual_ip_input.opacity = 0

    def choose_random_ips(self):
        try:
            OP = ["MCI", "MTN", "RTL", "MKH", "HWB", "SHT"]
            response = UrlRequest(
                "https://raw.githubusercontent.com/yebekhe/cf-clean-ip-resolver/main/list.json"
            )
            while not response.is_finished:
                sleep(.1)
                Clock.tick()

            json_data = response.result
            data = json.loads(json_data)
            all_ips = []
            for op in OP:
                matching_ips = [
                    ipv4_address["ip"]
                    for ipv4_address in data["ipv4"]
                    if ipv4_address["operator"] == op
                ]
                all_ips.extend(matching_ips)

            random_indexes = random.sample(range(len(all_ips)), 20)
            random_ips = [all_ips[idx] for idx in random_indexes]
            return ", ".join(random_ips)
        except Exception as e:
            self.update_log_textfield(f"{e}\n")
            return Exception(e)

    def parse_args(self):
        parser = argparse.ArgumentParser(description="Python Proxy")
        parser.add_argument(
            "--config",
            type=str,
            default="config.ini",
            help="Path to the configuration file",
        )
        return parser.parse_args()

    def write_config(
        self,
        config_path,
        user_operator,
        listen_PORT,
        Cloudflare_IPs,
        domain_addr,
        Cloudflare_port,
        my_socket_timeout,
        first_time_sleep,
        accept_time_sleep,
        condition_of_tunnel,
        random_fragment,
        socket_listen
    ):
        config = configparser.ConfigParser()
        config.read(config_path)

        config.set("settings", "user_operator", str(user_operator))
        config.set("settings", "listen_PORT", str(listen_PORT))
        config.set("settings", "Cloudflare_IP", str(Cloudflare_IPs))
        config.set("settings", "domain_addr", str(domain_addr))
        config.set("settings", "Cloudflare_port", str(Cloudflare_port))
        config.set("settings", "my_socket_timeout", str(my_socket_timeout))
        config.set("settings", "first_time_sleep", str(first_time_sleep))
        config.set("settings", "accept_time_sleep", str(accept_time_sleep))
        config.set("settings", "condition_of_tunnel", str(condition_of_tunnel))
        config.set("settings", "primary_palette", str(self.theme_cls.primary_palette))
        config.set("settings", "theme_style", str(self.theme_cls.theme_style))
        config.set("settings", "random_fragment", str(random_fragment))
        config.set("settings", "socket_listen", str(socket_listen))

        with open(config_path, "w") as config_file:
            config.write(config_file)

    def is_valid_ip(self, address):
        pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
        match = re.match(pattern, address)
        if not match:
            return False
        octets = address.split(".")
        for octet in octets:
            if int(octet) > 255:
                return False
        return True

    def is_valid_domain(self, domain):
        try:
            socket.gethostbyname(domain)
            return True
        except socket.error:
            return False

    def resolve_ipv4_addresses(self, domain):
        dns.resolver.default_resolver=dns.resolver.Resolver(configure=False)
        dns.resolver.default_resolver.nameservers=['78.157.42.100']
        results = dns.resolver.resolve(domain,'A')
        ip_addresses = []
        for server in results:
            ip_address = server.to_text()
            ip_addresses.append(ip_address)
        return ip_addresses

    def save_config(self):
        try:
            self.random_fragment = str(self.screen.get_screen("Setting").ids.random_fragment_check.state)
            self.listen_PORT = int(self.screen.get_screen("Setting").ids.local_port_input.text)
            user_operator_full = self.screen.get_screen("Setting").ids.operator_dropdown.current_item
            operators = {"Load Balance": "auto", "Manual": "manual"}
            self.user_operator = operators.get(user_operator_full)
            if self.user_operator == "auto":
                if (
                    "the JSON object must be str, bytes or bytearray, not NoneType" in self.choose_random_ips()
                ):
                    raise Exception(
                        "I can't get IPs from server , Check Your Internet Connection!"
                    )
                else:
                    self.Cloudflare_IPs = self.choose_random_ips()
                    self.domain_addr = "None"
            else:
                if self.is_valid_ip(str(self.screen.get_screen("Setting").ids.manual_ip_input.text)):
                    self.Cloudflare_IPs = str(self.screen.get_screen("Setting").ids.manual_ip_input.text)
                    self.domain_addr = "None"
                elif "," in str(self.screen.get_screen("Setting").ids.manual_ip_input.text):
                    valid_ips = []
                    ip_list = str(self.screen.get_screen("Setting").ids.manual_ip_input.text).split(",")
                    for ip in ip_list:
                        if self.is_valid_ip(ip.strip()):
                            valid_ips.append(ip)
                    if valid_ips:
                        self.Cloudflare_IPs = ",".join(valid_ips)
                        self.domain_addr = "None"
                    else:
                        raise Exception("Cloudflare IP(s) is not valid!")
                elif self.is_valid_domain(str(self.screen.get_screen("Setting").ids.manual_ip_input.text)):
                    self.Cloudflare_IPs = ",".join(self.resolve_ipv4_addresses(str(self.screen.get_screen("Setting").ids.manual_ip_input.text)))
                    self.domain_addr = str(self.screen.get_screen("Setting").ids.manual_ip_input.text)
                else:
                    raise Exception("Cloudflare IP or Domain is not valid!")
            self.Cloudflare_port = int(self.screen.get_screen("Setting").ids.config_port_input.text)
            if int(self.screen.get_screen("Setting").ids.socket_timeout_input.text) < 20 or int(self.screen.get_screen("Setting").ids.socket_timeout_input.text) > 100:
                raise Exception("Entered timeout is not valid! Please Enter a value between 20 to 100")
            else:
                self.my_socket_timeout = self.screen.get_screen("Setting").ids.socket_timeout_input.text
            if int(self.screen.get_screen("Setting").ids.socket_listen_input.text) < 128:
                raise Exception("Entered Listen Queue is not valid! Please Enter a value between equal or upper 128")
            else:
                self.socket_listen = self.screen.get_screen("Setting").ids.socket_listen_input.text
            args = self.parse_args()
            self.write_config(
                args.config,
                self.user_operator,
                self.listen_PORT,
                self.Cloudflare_IPs,
                self.domain_addr,
                self.Cloudflare_port,
                self.my_socket_timeout,
                self.first_time_sleep,
                self.accept_time_sleep,
                self.condition_of_tunnel,
                self.random_fragment,
                self.socket_listen,
            )

            self.dialog = MDDialog(
                title="Congrates!",
                text="Settings Saved Succesfully!",
                buttons=[
                    MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())
                ],
            )
            self.dialog.open()
        except Exception as e:
            self.update_log_textfield(f"{e}\n")
            self.error = MDDialog(
                title="Oops!",
                text=f"Something Went Wrong! {e}",
                buttons=[
                    MDFlatButton(text="OK", on_release=lambda x: self.error.dismiss())
                ],
            )
            self.error.open()

    def key_input(self, window, key, scancode, codepoint, modifier):
        if key == 27:
            if self.screen.current == "Main":
                self.dialog = MDDialog(
                    title="Exit",
                    text="Are you sure?! You want to close the app?",
                    buttons=[
                        MDFlatButton(text="No, Wait...", on_release=lambda x: self.dialog.dismiss()),
                        MDFlatButton(text="Yes, Close NetBright!", on_release=lambda x: self.stop())
                    ],
                )
                self.dialog.open()
                return True
            else:
                self.screen.current = "Main"
                return True
        else:
            return False

    def start_tunnel(self):
        try:
            if self.condition_of_tunnel == False:
                self.condition_of_tunnel = True
                dpitunnel.condition_of_tunnel = "True"
                print(f"Tunnel Started!")
                self.update_log_textfield(f"Tunnel Started!\n")
                self.update_log_textfield(f"Cloudflare IP(s): {self.Cloudflare_IPs}!\n")
                self.screen.get_screen("Main").ids.start_button.icon = "toggle-switch-outline"
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Context = autoclass('android.content.Context')
                PowerManager = autoclass('android.os.PowerManager')
                pm = PythonActivity.mActivity.getSystemService(Context.POWER_SERVICE)
                self.wake_lock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "MyApp:WakeLockTag")
                show_notification()
                self.wake_lock.acquire()
                if self.app_start == 0 :
                    self.app_start = 1
                    t = threading.Thread(target=dpitunnel.main)
                    t.daemon = True
                    t.start()
            else:
                self.condition_of_tunnel = False
                dpitunnel.condition_of_tunnel = "False"
                self.screen.get_screen("Main").ids.start_button.icon = "toggle-switch-off-outline"
                print(f"Tunnel Stopped!")
                self.update_log_textfield(f"Tunnel Stopped!\n")
                self.wake_lock.release()
                cancel_notification()

        except Exception as e:
            self.update_log_textfield(f"{e}\n")
            self.error = MDDialog(
                title="Oops!",
                text=f"Something Went Wrong! {e}",
                buttons=[
                    MDFlatButton(text="OK", on_release=lambda x: self.error.dismiss())
                ],
            )
            self.error.open()


if __name__ == "__main__":
    MainApp().run()