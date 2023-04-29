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
import threading
import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.clock import Clock

Cloudflare_IP = "162.159.36.93"
listen_PORT = 2500
Cloudflare_port = 443
my_socket_timeout = 60
first_time_sleep = 0.01
accept_time_sleep = 0.01
condition_of_tunnel = False

def choose_random_ip_with_operator(json_data, operator_code):
    # Decode JSON data
    data = json.loads(json_data)

    # Search for IPv4 addresses with the specified operator code
    matching_ips = []
    for ipv4_address in data["ipv4"]:
        if ipv4_address["operator"] == operator_code:
            matching_ips.append(ipv4_address["ip"])

    # Count how many IPv4 addresses have the operator code
    matching_count = len(matching_ips)

    # If there are any matching IPs, choose one at random and return it
    if matching_count > 0:
        random_index = random.randint(0, matching_count - 1)
        random_ip = matching_ips[random_index]
        return random_ip
    else:
        return None

class MyBoxLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10

        self.label = Label(
            text='DPI Tunnel',
            halign='center',
            valign='middle',
            size_hint=(0.5, 0.2)
        )
        self.label.pos_hint = {'x': 0.25}
        self.add_widget(self.label)
        self.local_port_input = TextInput(
            hint_text='Enter Your Desired Local Port : ',
            halign='center',
            padding_x=[20, 20],
            size_hint=(0.5, 0.2)
        )
        self.local_port_input.pos_hint = {'x': 0.25}
        self.add_widget(self.local_port_input)
        self.local_port_input.bind(on_size=self.on_text_input_size)
        self.spinner = Spinner(
            text='Select an option',
            values=('Manual', 'Hamrah-Aval', "Irancell", "Rightel", "Mokhaberat", "HiWeb", "AsiaTech", "Shatel", "ParsOnline", "MobinNet", "Andishe-Sabz-Khazar", "Respina", "AfraNet", "Zi-Tel", "Pishgaman", "Araax", "SamanTel", "FanAva", "DidebanNet", "ApTel", "Fanap-Telecom", "RayNet"),
            size_hint=(0.5, 0.2)
        )
        self.spinner.bind(text=self.on_spinner_select)
        self.spinner.pos_hint = {'x': 0.25}
        self.add_widget(self.spinner)
        self.cloudflare_ip_input = TextInput(
            hint_text='Enter your Cloudflare IP',
            halign='center',
            padding_x=[20, 20],
            size_hint=(None, None),
            size=(0,0),
            opacity=0
        )
        self.cloudflare_ip_input.pos_hint = {'x': 0.25}
        self.cloudflare_ip_input.bind(on_size=self.on_text_input_size)
        self.add_widget(self.cloudflare_ip_input)

        self.config_port_input = TextInput(
            hint_text='Enter Your Config Port : ',
            halign='center',
            padding_x=[20, 20],
            size_hint=(0.5, 0.2)
        )
        self.config_port_input.pos_hint = {'x': 0.25}
        self.add_widget(self.config_port_input)
        self.config_port_input.bind(on_size=self.on_text_input_size)
        self.button = Button(text='Start Tunnel!', size_hint=(0.5, 0.2))
        self.button.pos_hint = {'x': 0.25}
        self.button.background_color = (1, 0.5, 0, 1)
        self.button.bind(on_press=self.on_button_press)
        self.add_widget(self.button)

    def on_text_input_size(self, instance, value):
        self.local_port_input.padding_y = [(self.local_port_input.height - self.local_port_input.line_height) / 2, 0]
    def on_spinner_select(self, spinner, text):
        if text == 'Manual':
            self.cloudflare_ip_input.size_hint = [0.5, 0.2]
            self.cloudflare_ip_input.size = self.label.texture_size
            self.cloudflare_ip_input.opacity=1
        else:
            self.cloudflare_ip_input.size_hint = [None, None]
            self.cloudflare_ip_input.size = [0,0]
            self.cloudflare_ip_input.opacity=0

    def on_button_press(self, instance):
         global condition_of_tunnel
         if condition_of_tunnel == False :
            self.button.text = 'Stop Tunnel!'
            threading.Thread(target=self.start_tunnel).start()
            condition_of_tunnel = True
         else :
            self.close_app()
            return True

    def close_app(self):
        popup = Popup(title="Confirmation", content=Label(text="Are you sure you want to exit?"), size_hint=(None, None), size=(400, 200))
        yes_button = Button(text="Yes")
        no_button = Button(text="No")
        yes_button.bind(on_release=self.final_close_app) # Change this line
        no_button.bind(on_release=popup.dismiss)
        popup_content = BoxLayout(orientation='vertical')
        popup_content.add_widget(Label(text='Are you sure you want to close the app?'))
        popup_content.add_widget(yes_button)
        popup_content.add_widget(no_button)
        popup.content = popup_content
        popup.open()

    def final_close_app(self, *args):
        app = App.get_running_app().stop() # Change this line
        Clock.schedule_once(lambda dt: app.stop(), 0.1)

    def start_tunnel(self):
         if os.name == 'posix':
             import resource
             soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_NOFILE)
             resource.setrlimit(resource.RLIMIT_NOFILE, (soft_limit, hard_limit))
             socket_timeout = 60
             sleep_time = 0.01

         listen_PORT = int(self.local_port_input.text)

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

         Cloudflare_port = int(self.config_port_input.text)

         ThreadedServer('',listen_PORT).listen()

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


    def stop(self):
        self.sock.close()

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
        # sock.send(fragment_data)
        sock.sendall(fragment_data)
        time.sleep(fragment_sleep)

class MyApp(App):
    def build(self):
        return MyBoxLayout()

if __name__ == '__main__':
    MyApp().run()
