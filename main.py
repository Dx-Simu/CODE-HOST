#!/usr/bin/env python3
"""
NIKO-V12: KERNEL-GOD MODE (DARK-X PRO)
Feature: Auto-Link Generation & Direct WhatsApp Setup
Developer: DX-CODEX (NIKO)
"""

import socket
import threading
import select
import os
import time
import requests

# DX COLORS
r='\033[1;91m'; p='\033[1;95m'; y='\033[1;93m'
g='\033[1;92m'; n='\033[1;0m'; b='\033[1;94m'; c='\033[1;96m'

class NikoGodEngine:
    def __init__(self, host='0.0.0.0'):
        # Render dynamic port support
        self.port = int(os.environ.get("PORT", 8888))
        self.host = host
        self.buffer_size = 4194304 # 4MB Massive Buffer
        # Get public IP or Render URL
        self.public_ip = os.environ.get("RENDER_EXTERNAL_URL", "127.0.0.1").replace("https://", "").replace("http://", "")
        self.render_url = os.environ.get("RENDER_EXTERNAL_URL", "https://code-host.onrender.com")

    def tune_socket(self, sock):
        try:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_TOS, 0xB8)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.buffer_size)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.buffer_size)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            sock.settimeout(None)
        except:
            pass

    def anti_sleep_ping(self):
        if not self.render_url: return
        while True:
            try:
                requests.get(self.render_url, timeout=10)
            except: pass
            time.sleep(300)

    def banner(self):
        os.system('clear')
        # Direct WhatsApp Proxy Link logic
        proxy_link = f"https://wa.me/proxy?host={self.public_ip}&chatPort={self.port}&mediaPort={self.port}&chatTLS=true"
        
        print(f"{c}="*65)
        print(f"{g}  ╔╗╔╦╦╔═╔═╗   ╔═╗╦╔═╗╦ ╦╔╦╗╔═╗╦═╗")
        print(f"{g}  ║║║║╠╩╗║ ║───╠╣ ║║ ╦╠═╣ ║ ║╣ ╠╦╝")
        print(f"{g}  ╝╚╝╩╩ ╩╚═╝   ╚  ╩╚═╝╩ ╩ ╩ ╚═╝╩╚═")
        print(f"{y}\n        +-+-+-+-+-+-+")
        print(f"{y}        |D|A|R|K|-|X|")
        print(f"{y}        +-+-+-+-+-+-+")
        print(f"{c}="*65)
        print(f"{y}  [+] STATUS  : {g}CODE MODE ACTIVE")
        print(f"{y}  [+] PORT    : {p}{self.port}")
        print(f"{y}  [+] IP/HOST : {p}{self.public_ip}")
        print(f"{c}-"*65)
        print(f"{b}  [ DIRECT PROXY LINK ]")
        print(f"{c}  {proxy_link}")
        print(f"{c}="*65)
        print(f"{b}  ID  |     SOURCE      |    TRAFFIC TYPE   |    QUALITY")
        print(f"{c}-"*65 + f"{n}")

    def bridge(self, s1, s2):
        sockets = [s1, s2]
        try:
            while True:
                readable, _, _ = select.select(sockets, [], [], 0.001)
                for s in readable:
                    data = s.recv(self.buffer_size)
                    if not data: return
                    target = s2 if s is s1 else s1
                    target.sendall(data)
        except: pass
        finally:
            s1.close(); s2.close()

    def handle_client(self, client_sock, addr, user_id):
        try:
            header_data = client_sock.recv(self.buffer_size)
            if not header_data: return

            # Render Health Check Bypass
            if b"GET /" in header_data[:10]:
                client_sock.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nNIKO-CODE ENGINE LIVE")
                return

            request_str = header_data.decode('utf-8', errors='ignore')
            if 'CONNECT' in request_str:
                target = request_str.split(' ')[1]
                host, port = target.split(':')
                
                remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.tune_socket(remote_sock)
                remote_sock.connect((host, int(port)))

                client_sock.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
                print(f" {y}[{user_id:02}]  {c}{addr[0]:<13}  {p}VOICE/SSL      {g}BOOSTED ↑↑{n}")
                self.bridge(client_sock, remote_sock)
        except: pass
        finally: client_sock.close()

    def run(self):
        threading.Thread(target=self.anti_sleep_ping, daemon=True).start()
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(1000)
        self.banner()
        
        id_gen = 0
        while True:
            try:
                client_sock, addr = server.accept()
                id_gen += 1
                self.tune_socket(client_sock)
                threading.Thread(target=self.handle_client, args=(client_sock, addr, id_gen), daemon=True).start()
            except: continue

if __name__ == "__main__":
    NikoGodEngine().run()
