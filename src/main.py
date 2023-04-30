import kivy
import requests
import subprocess
import json
import random
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.clock import Clock

class DPITunnel(BoxLayout):
    def __init__(self, **kwargs):
        self.condition_of_tunnel = False
        self.server = None
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 20
        self.padding = [20, 40]

        self.label = Label(
            text='DPI Tunnel',
            halign='center',
            valign='middle',
            font_size=30,
            size_hint=(None, None),
            size=(400, 60),
            pos_hint={'center_x': 0.5}
        )
        self.add_widget(self.label)

        self.local_port_input = TextInput(
            hint_text='Enter Your Desired Local Port:',
            halign='center',
            padding=[20, 10],
            font_size=16,
            size_hint=(0.8, None),
            height=50,
            pos_hint={'center_x': 0.5}
        )
        self.add_widget(self.local_port_input)

        self.spinner = Spinner(
            text='Select Your Operator',
            values=('Manual', 'Hamrah-Aval', 'Irancell', 'Rightel', 'Mokhaberat', 'HiWeb', 'AsiaTech', 'Shatel', 'ParsOnline', 'MobinNet', 'Andishe-Sabz-Khazar', 'Respina', 'AfraNet', 'Zi-Tel', 'Pishgaman', 'Araax', 'SamanTel', 'FanAva', 'DidebanNet', 'ApTel', 'Fanap-Telecom', 'RayNet'),
            font_size=16,
            size_hint=(0.8, None),
            height=50,
            pos_hint={'center_x': 0.5}
        )
        self.spinner.bind(text=self.on_spinner_select)
        self.add_widget(self.spinner)

        self.cloudflare_ip_input = TextInput(
            hint_text='Enter Your Cloudflare IP ',
            halign='center',
            padding=[0, 0],
            font_size=16,
            size_hint=(None, None),
            height=0,
            pos_hint={'center_x': 0.5},
            opacity=0
        )
        self.add_widget(self.cloudflare_ip_input)

        self.config_port_input = TextInput(
            hint_text='Enter Your Config Port:',
            halign='center',
            padding=[20, 10],
            font_size=16,
            size_hint=(0.8, None),
            height=50,
            pos_hint={'center_x': 0.5},
        )
        self.add_widget(self.config_port_input)

        self.start_button = Button(
            text='Start Tunnel',
            font_size=18,
            size_hint=(0.5, None),
            height=50,
            pos_hint={'center_x': 0.5}
        )
        self.start_button.background_color = (1, 0.5, 0, 1)
        self.start_button.bind(on_press=self.on_start_button_press)
        self.add_widget(self.start_button)

    def on_spinner_select(self, spinner, text):
        if text == 'Manual':
            self.cloudflare_ip_input.padding = [20, 10]
            self.cloudflare_ip_input.height = 50
            self.cloudflare_ip_input.size_hint = (0.8, None)
            self.cloudflare_ip_input.opacity = 1
        else:
            self.cloudflare_ip_input.padding = [0, 0]
            self.cloudflare_ip_input.height = 0
            self.cloudflare_ip_input.size_hint = (None, None)
            self.cloudflare_ip_input.opacity = 0

    def on_start_button_press(self, instance):
        if self.condition_of_tunnel == False :
             self.condition_of_tunnel = True
             self.start_button.text = 'Stop Tunnel!'
             user_operator_full = self.spinner.text
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
                 Cloudflare_IP = self.cloudflare_ip_input.text
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
             self.server = subprocess.Popen(["python3","side_job.py",f"{self.local_port_input.text}",f"{Cloudflare_IP}",f"{self.config_port_input.text}"])
        else :
            self.condition_of_tunnel = False
            self.start_button.text = 'Start Tunnel!'
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

class MyApp(App):
    def build(self):
        return DPITunnel()

if __name__ == '__main__':
    MyApp().run()

