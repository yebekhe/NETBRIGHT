import requests
import subprocess
import json
import random
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivy.lang.builder import Builder
from kivy.properties import StringProperty
from kivymd.uix.list import OneLineIconListItem

KV = '''
<IconListItem>

    IconLeftWidget:
        icon: root.icon
        width: 200

MDScreen:
    BoxLayout:
        orientation: "vertical"
        size_hint_y: None
        height: root.height

        Widget:
            size_hint_y: None
            height: (root.height - dp(48) * 6) / 2

        GridLayout:
            cols: 1
            rows: 6
            padding: "24dp"
            spacing: "16dp"

            MDLabel:
                text: "DPI Tunnel"
                halign: "center"
                font_style: "H5"
                theme_text_color: "Primary"

            MDTextField:
                id: local_port_input
                hint_text: "Enter Your Desired Local Port:"
                helper_text: "I'm going to Listen to this port from localhost or 127.0.0.1"
                helper_text_mode: "persistent"

            MDDropDownItem:
                id: operator_dropdown
                text: "Select Your Operator"
                on_release: app.menu.open()

            MDTextField:
                id: cloudflare_ip_input
                hint_text: "Enter Your Cloudflare IP"
                helper_text: "Select Your Operator if you don't have any IP!"
                helper_text_mode: "persistent"
                opacity: 0
                height: 0


            MDTextField:
                id: config_port_input
                hint_text: "Enter Your Config Port:"
                helper_text: "Set 443 If you're using GetAfreeNode"
                helper_text_mode: "persistent"

            MDRaisedButton:
                id: start_button
                text: "Start Tunnel"
                md_bg_color: "orange"
                elevation_normal: 8
                on_press: app.start_tunnel()
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
           {"text": "Manual", "on_release": lambda x="Manual": self.set_item(x) , "viewclass": "IconListItem", "height": dp(56)},
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

    def set_item(self, text_item):
        self.screen.ids.operator_dropdown.set_item(text_item)
        self.cloudflare_input = self.screen.ids.cloudflare_ip_input
        if text_item == "Manual":
            self.cloudflare_input.opacity = 1
            self.cloudflare_input.height = dp(56)
        else:
            self.cloudflare_input.opacity = 0
            self.cloudflare_input.height = 0
        self.menu.dismiss()

    def start_tunnel(self):
        if self.condition_of_tunnel == False :
             self.condition_of_tunnel = True
             self.screen.ids.start_button.text = 'Stop Tunnel!'
             user_operator_full = self.screen.ids.operator_dropdown.current_item
             operators = {
                 "Manual": "manual",
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
             user_operator = operators.get(user_operator_full)
             response = requests.get("https://raw.githubusercontent.com/yebekhe/cf-clean-ip-resolver/main/list.json")
             json_data = response.content
             if user_operator == "manual":
                 Cloudflare_IP = self.screen.ids.cloudflare_ip_input.text
             elif user_operator == "MCI":
                 Cloudflare_IP = choose_random_ip_with_operator(json_data, "MCI")
             elif user_operator == "MTN":
                 Cloudflare_IP = choose_random_ip_with_operator(json_data, "MTN")
             elif user_operator == "RTL":
                 Cloudflare_IP = choose_random_ip_with_operator(json_data, "RTL")
             elif user_operator == "MKH":
                 Cloudflare_IP = choose_random_ip_with_operator(json_data, "MKH")
             elif user_operator == "HWB":
                 Cloudflare_IP = choose_random_ip_with_operator(json_data, "HWB")
             elif user_operator == "AST":
                 Cloudflare_IP = choose_random_ip_with_operator(json_data, "AST")
             elif user_operator == "SHT":
                 Cloudflare_IP = choose_random_ip_with_operator(json_data, "SHT")
             elif user_operator == "PRS":
                 Cloudflare_IP = choose_random_ip_with_operator(json_data, "PRS")
             elif user_operator == "MBT":
                 Cloudflare_IP = choose_random_ip_with_operator(json_data, "MBT")
             elif user_operator == "ASK":
                 Cloudflare_IP = choose_random_ip_with_operator(json_data, "ASK")
             elif user_operator == "RSP":
                 Cloudflare_IP = choose_random_ip_with_operator(json_data, "RSP")
             elif user_operator == "AFN":
                 Cloudflare_IP = choose_random_ip_with_operator(json_data, "AFN")
             elif user_operator == "ZTL":
                 Cloudflare_IP = choose_random_ip_with_operator(json_data, "ZTL")
             elif user_operator == "PSM":
                 Cloudflare_IP = choose_random_ip_with_operator(json_data, "PSM")
             elif user_operator == "ARX":
                 Cloudflare_IP = choose_random_ip_with_operator(json_data, "ARX")
             elif user_operator == "SMT":
                 Cloudflare_IP = choose_random_ip_with_operator(json_data, "SMT")
             elif user_operator == "FNV":
                 Cloudflare_IP = choose_random_ip_with_operator(json_data, "FNV")
             elif user_operator == "DBN":
                 Cloudflare_IP = choose_random_ip_with_operator(json_data, "DBN")
             elif user_operator == "APT":
                 Cloudflare_IP = choose_random_ip_with_operator(json_data, "APT")
             elif user_operator == "FNP":
                 Cloudflare_IP = choose_random_ip_with_operator(json_data, "FNP")
             elif user_operator == "RYN":
                 Cloudflare_IP = choose_random_ip_with_operator(json_data, "RYN")
             else:
                 Cloudflare_IP = '162.159.36.93'
             self.server = subprocess.Popen(["python3","side_job.py",f"{self.screen.ids.local_port_input.text}",f"{Cloudflare_IP}",f"{self.screen.ids.config_port_input.text}"])
        else :
             self.condition_of_tunnel = False
             self.screen.ids.start_button.text = 'Start Tunnel!'
             self.server.terminate()

def choose_random_ip_with_operator(json_data, operator_code):
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



MainApp().run()
