#!/usr/bin/env python3
"""
NIKO-V15: HYPER-VOICE EDITION (QUANTUM CORE)
Developer: DX-CODEX (NIKO)
Features: DSCP Voice Tagging | QoS Priority | Anti-Drop
"""

import socket
import threading
import select
import os
import time
import requests
import sys

# DX VISUALS
r = '\033[1;91m'; p = '\033[1;95m'; y = '\033[1;93m'
g = '\033[1;92m'; n = '\033[1;0m'; b = '\033[1;94m'; c = '\033[1;96m'

class NikoHyperVoice:
    def __init__(self):
        self.port = int(os.environ.get("PORT", 8080)) # Render default often 10000, changed to generic fallback
        self.host = '0.0.0.0'
        # Optimized Buffers: High OS buffer for stability, controlled app buffer for speed
        self.os_buffer = 1048576 * 2  # 2MB Socket Buffer
        self.app_buffer = 32768       # 32KB Chunks for low latency (Voice Speed)
        self.render_url = os.environ.get("RENDER_EXTERNAL_URL", "http://localhost") 
        self.public_ip = self.render_url.replace("https://", "").replace("http://", "").replace("/", "")

    def tune_socket(self, sock):
        """Advanced Socket Tuning for QoS and Voice Priority"""
        try:
            # 1. Disable Nagle's Algorithm (No Delay)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            
            # 2. Set QoS to Voice/DSCP EF (Expedited Forwarding - 0xB8)
            # This tells routers this packet is URGENT VOICE
            if hasattr(socket, 'IP_TOS'):
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_TOS, 0xB8)
            
            # 3. High Priority in OS Queue (Linux Specific optimization)
            if hasattr(socket, 'SO_PRIORITY'):
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_PRIORITY, 6)

            # 4. Maximize Buffer for Throughput
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.os_buffer)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.os_buffer)
            
            # 5. Keep Alive to prevent WhatsApp disconnects
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            
        except Exception as e:
            pass # Ignore errors on non-Linux systems

    def anti_sleep_ping(self):
        """Smart Keep-Alive Mechanism"""
        time.sleep(5)
        print(f"{y} [+] SYSTEM: {g}Anti-Sleep Guardian Active...{n}")
        while True:
            try:
                if "localhost" not in self.render_url:
                    requests.get(self.render_url, timeout=10)
            except:
                pass
            time.sleep(240) # 4 Minutes interval (Render safe zone)

    def banner(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        # WhatsApp Proxy String format
        wa_proxy = f"https://wa.me/proxy?host={self.public_ip}&chatPort=443&mediaPort=443&ssl=true"
        
        print(f"{c}="*60)
        print(f"{g}   _  __  ____  __ __  ____         _  __  _  ____")
        print(f"{g}  / |/ / /  _/ / //_/ / __ \       | |/ / <  / __/")
        print(f"{g} /    / _/ /  / ,<   / /_/ / ____  |   /  / /__ \ ")
        print(f"{g}/_/|_/ /___/ /_/|_|  \____/ /___/  |__/  /_/____/ ")
        print(f"{y}\n    [ HYPER-VOICE ALGORITHM ACTIVATED ]")
        print(f"{c}="*60)
        print(f"{y} [+] STATUS     : {g}ONLINE & ACCELERATED")
        print(f"{y} [+] ALGORITHM  : {p}DSCP-EF (VOICE PRIORITY)")
        print(f"{y} [+] LATENCY    : {g}MINIMIZED (TCP_NODELAY)")
        print(f"{c}-"*60)
        print(f"{b} [ COPY THIS FOR WHATSAPP ]")
        print(f"{n} {wa_proxy}")
        print(f"{c}="*60 + f"{n}")

    def handle_connect(self, client_sock, target_host, target_port):
        """Establishes connection to remote server (WhatsApp/Web)"""
        try:
            remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tune_socket(remote_sock)
            remote_sock.connect((target_host, int(target_port)))

            # Handshake OK
            client_sock.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            
            # Bridge Data with Priority
            self.bridge(client_sock, remote_sock)
        except:
            pass
        finally:
            client_sock.close()
            try: remote_sock.close()
            except: pass

    def bridge(self, client, remote):
        """High-Speed Data Tunnel"""
        sockets = [client, remote]
        try:
            while True:
                # Select is efficient for waiting on I/O
                readable, _, _ = select.select(sockets, [], [], 60)
                if not readable: break
                
                for sock in readable:
                    other = remote if sock is client else client
                    try:
                        data = sock.recv(self.app_buffer)
                        if not data: return
                        other.sendall(data)
                    except: return
        except: pass

    def handle_request(self, client_sock, addr):
        try:
            # Peek at header to route traffic
            header = client_sock.recv(4096)
            if not header: return

            req = header.decode('utf-8', errors='ignore')
            
            # 1. Handle Proxy Connect (WhatsApp uses CONNECT method)
            if 'CONNECT' in req:
                try:
                    target_info = req.split(' ')[1]
                    host, port = target_info.split(':')
                    print(f"{r} [WA-DATA] {c}{addr[0]} {y}>> {g}VOICE TUNNEL ESTABLISHED {n}")
                    self.handle_connect(client_sock, host, port)
                except:
                    pass
                return

            # 2. Handle HTTP Health Check (For Render/Uptime)
            if 'GET /' in req or 'HEAD /' in req:
                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/plain\r\n"
                    "Connection: close\r\n\r\n"
                    "NIKO HYPER-VOICE RUNNING"
                )
                client_sock.sendall(response.encode())
                client_sock.close()
                return

        except:
            client_sock.close()

    def run(self):
        # Start Background Tasks
        threading.Thread(target=self.anti_sleep_ping, daemon=True).start()
        
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server.bind((self.host, self.port))
            server.listen(500)
            self.banner()
            
            while True:
                try:
                    client_sock, addr = server.accept()
                    self.tune_socket(client_sock) # Apply Priority Tags immediately
                    
                    t = threading.Thread(target=self.handle_request, args=(client_sock, addr))
                    t.daemon = True
                    t.start()
                except KeyboardInterrupt:
                    break
                except:
                    continue
        except Exception as e:
            print(f"{r}[!] CRITICAL ERROR: {e}{n}")

if __name__ == "__main__":
    NikoHyperVoice().run()
