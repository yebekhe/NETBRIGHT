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
import Fragmentor
import shutil
import webbrowser
import numpy as np
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process, Value
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
from kivy.uix.scrollview import ScrollView
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition
from kivy.core.window import Window
from kivy.utils import platform

Window.keyboard_anim_args = {'d': .2, 't': 'in_out_expo'}
Window.softinput_mode = "below_target"

if platform == "android":
    from kvdroid.tools.network import network_status, wifi_status, mobile_status
    from kvdroid.tools import change_statusbar_color, navbar_color
    from modules.android_notification import AndroidNotification
    android_notification = AndroidNotification()

class TheScreen(ScreenManager):
    pass

class Main(Screen):
    pass

class Setting(Screen):
    pass

class IconListItem(OneLineIconListItem):
    icon = StringProperty()

class MainApp(MDApp):
    def __init__(self, **kwargs):
        self.condition_of_tunnel = 0
        self.dialog = None
        self.error = None
        self.prev_line = ""
        self.app_start = 0
        self.stop_flag = threading.Event()

        super().__init__(**kwargs)
        self.theme_cls.material_style = "M2"
        self.screen = Builder.load_file( 'ui/MainApp.kv' )

        if os.name == 'posix':
            print('os is linux')
            import resource
            soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_NOFILE)
            resource.setrlimit(resource.RLIMIT_NOFILE, (soft_limit, hard_limit))

        if platform == "android":
            from android.permissions import request_permissions, Permission, check_permission
            if check_permission(Permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS) == False:
                permissions = [Permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS]
                request_permissions(permissions)
            else:
                pass

        menu_items = [
            {
                "text": "Cloudflare IPs",
                "on_release": lambda x="Cloudflare IPs": self.set_item(x),
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
        
        self.startup_load()

    def callback(self, scr):
        self.screen.transition = NoTransition()
        if scr == "Main":
            if self.save_config() == True:
                pass
        self.screen.current = scr

    def build(self):
        Window.bind(on_keyboard=self.key_input)
        if platform == "android":
            from android import loadingscreen
            import jnius
            from jnius import autoclass
            loadingscreen.hide_loading_screen()
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Context = autoclass('android.content.Context')
            PowerManager = autoclass('android.os.PowerManager')
            pm = PythonActivity.mActivity.getSystemService(Context.POWER_SERVICE)
            self.wake_lock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "MyApp:WakeLockTag")
            self.wake_lock.acquire()
            
        return self.screen

    def startup_load(self):
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
            self.screen.get_screen("Setting").ids.operator_dropdown.set_item("Cloudflare IPs")
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

    def send_notif(self, title, text):
        if platform == "android":
            android_notification.notify(
                title=title,
                message=text
            )

    def send_toast(self, title, text):
        if platform == "android":
            android_notification.notify(
                title=title,
                message=text,
                toast=True
            )
        else:
            self.dialog = MDDialog(
                title=title,
                text=text,
                buttons=[
                    MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())
                ],
            )
            self.dialog.open()
    
    def cancel_notif(self):
        if platform == "android":
            android_notification.cancel_notification()

    def check_internet(self):
        if platform == "android":
            if network_status() != False :
                return True
            else:
                return False

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
            urls = ["mci.ircf.space", "mcic.ircf.space", "mtn.ircf.space", "mtnc.ircf.space", "mkh.ircf.space", "rtl.ircf.space"]
            ip_addresses = []
            for url in urls:
                ip_addresses = np.concatenate((ip_addresses, self.resolve_ipv4_addresses(url)))   
            return ", ".join(ip_addresses)
        except Exception as e:
            return False

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
        dns.resolver.default_resolver.nameservers=['94.140.14.14']
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
            operators = {"Cloudflare IPs": "auto", "Manual": "manual"}
            self.user_operator = operators.get(user_operator_full)
            if self.user_operator == "auto":
                if self.choose_random_ips() != False:
                    self.Cloudflare_IPs = self.choose_random_ips()
                    self.domain_addr = "None"
                else:
                    raise Exception(
                            "I can't get IPs from server , Check Your Internet Connection!"
                    )
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
            if self.app_start == 0 :
                self.send_toast("Congrates!", "Settings Saved Succesfully!")
            else:
                self.dialog = MDDialog(
                    title="Congrates!",
                    text="Close NETBRIGHT and Re-Open it to apply changes?",
                    buttons=[
                        MDFlatButton(text="No , I'll do it later!", on_release=lambda x: self.dialog.dismiss()),
                        MDFlatButton(text="Yes, Close NetBright!", on_release=lambda x: self.app_close())
                    ],
                )
                self.dialog.open()
            return True
        except Exception as e:
            self.error = MDDialog(
                title="Oops! Something Went Wrong!",
                text=f"{e}",
                buttons=[
                    MDFlatButton(text="OK", on_release=lambda x: self.error.dismiss())
                ],
            )
            self.error.open()
            return False

    def app_close(self):
        if platform == "android":
            self.android_notification.cancel_notification()
        self.stop()

    def key_input(self, window, key, scancode, codepoint, modifier):
        if key == 27:
            if self.screen.current == "Main":
                self.dialog = MDDialog(
                    title="Exit",
                    text="Are you sure?! You want to close the app?",
                    buttons=[
                        MDFlatButton(text="No, Wait...", on_release=lambda x: self.dialog.dismiss()),
                        MDFlatButton(text="Yes, Close NetBright!", on_release=lambda x: self.app_close())
                    ],
                )
                self.dialog.open()
                return True
            else:
                self.callback("Main")
                return True
        else:
            return False

    def start_tunnel(self):
        try:
            if self.condition_of_tunnel == 0:
                self.condition_of_tunnel = 1
                print(f"Tunnel Started!")
                self.screen.get_screen("Main").ids.start_button.icon = "toggle-switch-outline"
                self.app_start = 1 
                self.t = threading.Thread(target=Fragmentor.main,)
                self.t.daemon = True
                self.t.start()
                self.screen.get_screen("Main").ids.toggle_label.text = "Tunnel is running!"
                self.send_notif("Tunnel Started!", f'Listening on 127.0.0.1:{self.screen.get_screen("Setting").ids.local_port_input.text}')
            else:
                self.condition_of_tunnel = 0
                self.t.join(.1)
                self.screen.get_screen("Main").ids.start_button.icon = "toggle-switch-off-outline"
                self.screen.get_screen("Main").ids.toggle_label.text = "Click on toggle to start Tunnel!"
                print(f"Tunnel Stopped!")
                self.cancel_notif()

        except Exception as e:
            self.error = MDDialog(
                title="Oops! Something Went Wrong!",
                text=f"{e}",
                buttons=[
                    MDFlatButton(text="OK", on_release=lambda x: self.error.dismiss())
                ],
            )
            self.error.open()


if __name__ == "__main__":
    MainApp().run()