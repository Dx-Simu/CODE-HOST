#!/usr/bin/env python3
"""
NIKO-V14: FAST-DEPLOY EDITION (DARK-X PRO)
Developer: DX-CODEX (NIKO)
Status: Fixed Port-Binding & Ultra-Voice Persistence
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

class NikoFastEngine:
    def __init__(self):
        # Render-er port prothomei fix kore deya holo jate restart na hoy
        self.port = int(os.environ.get("PORT", 10000)) 
        self.host = '0.0.0.0'
        self.buffer_size = 4194304 
        self.render_url = "https://code-host.onrender.com"
        self.public_ip = "code-host.onrender.com"

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
        """Keeps Render instance active with 3-minute interval"""
        time.sleep(20)
        while True:
            try:
                requests.get(self.render_url, timeout=5)
            except:
                pass
            time.sleep(180) # Faster heartbeats for stability

    def banner(self):
        os.system('clear')
        proxy_link = f"https://wa.me/proxy?host={self.public_ip}&chatPort=443&mediaPort=443&chatTLS=true"
        
        print(f"{c}="*65)
        print(f"{g}╔╗╔╦╦╔═╔═╗   ╔═╗╦╔═╗╦ ╦╔╦╗╔═╗╦═╗")
        print(f"{g}║║║║╠╩╗║ ║───╠╣ ║║ ╦╠═╣ ║ ║╣ ╠╦╝")
        print(f"{g}╝╚╝╩╩ ╩╚═╝   ╚  ╩╚═╝╩ ╩ ╩ ╚═╝╩╚═")
        print(f"{y}\n      +-+-+-+-+-+-+")
        print(f"{y}      |D|A|R|K|-|X|")
        print(f"{y}      +-+-+-+-+-+-+")
        print(f"{c}="*65)
        print(f"{y}  [+] DEPLOYMENT: {g}SUCCESSFUL & FAST")
        print(f"{y}  [+] ENDPOINT  : {p}{self.render_url}")
        print(f"{y}  [+] VOICE     : {g}IMMORTAL CLOUD BOOSTER")
        print(f"{c}-"*65)
        print(f"{b}  [ DIRECT WHATSAPP LINK ]")
        print(f"{c}  {proxy_link}")
        print(f"{c}="*65)
        print(f"{b}  ID  |     SOURCE      |    TRAFFIC TYPE   |    QUALITY")
        print(f"{c}-"*65 + f"{n}")

    def handle_client(self, client_sock, addr, user_id):
        try:
            header_data = client_sock.recv(self.buffer_size)
            if not header_data:
                return

            # Fast Response for Render Health Checks
            if b"GET /" in header_data or b"HEAD /" in header_data:
                client_sock.sendall(
                    b"HTTP/1.1 200 OK\r\n"
                    b"Content-Type: text/plain\r\n"
                    b"Connection: close\r\n\r\n"
                    b"NIKO LIVE"
                )
                return

            request_str = header_data.decode('utf-8', errors='ignore')
            if 'CONNECT' in request_str:
                target = request_str.split(' ')[1]
                host, port = target.split(':')
                
                remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.tune_socket(remote_sock)
                remote_sock.connect((host, int(port)))

                client_sock.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
                print(f" {y}[{user_id:02}]  {c}{addr[0]:<13}  {p}VOICE/HD        {g}BOOSTED ↑↑{n}")
                
                self.bridge(client_sock, remote_sock)
        except:
            pass
        finally:
            client_sock.close()

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

    def run(self):
        # Start anti-sleep
        threading.Thread(target=self.anti_sleep_ping, daemon=True).start()
        
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Immediate binding to the port
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
            except:
                continue

if __name__ == "__main__":
    NikoFastEngine().run()
