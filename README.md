# ⚡ DDoS Attack Framework – Bulletproof Edition
<div align="center">
<pre>
██████╗  ██████╗    ████╗    ██████╗
██╔═══██╗██╔═══██╗██╔═══██╗██╔═════╝
██║   ██║██║   ██║██║   ██║╚═████╗  
██║   ██║██║   ██║██║   ██║  ╚═══██╗
██████╔═╝██████╔═╝╚═████╔═╝██████╔═╝
╚═════╝  ╚═════╝    ╚═══╝  ╚═════╝  
</pre>

</div>

**Audited | All Bugs Fixed | Production-Ready**

**For Authorized Security Testing Only**

---

## 🚨 LEGAL DISCLAIMER

**This tool is for AUTHORIZED SECURITY TESTING only.**  
Using it against any target without explicit **written permission** is **ILLEGAL**.  
You are solely responsible for your actions. The authors assume **zero liability** for misuse.

---

## 🚀 Features

- **8 attack vectors** – HTTP Flood, TCP Flood, UDP Flood, Slowloris, ICMP Flood, DNS Flood, SSL/TLS Renegotiation, Multi-Vector
- **Bulletproof sockets** – Safe close() with shutdown(), zero FD leaks, guaranteed cleanup  
- **Brutal performance** – up to **20,000 threads**, batch processing, 256MB buffers, TCP_NODELAY
- **Thread-safe metrics** – All counters under locks, no race conditions, real-time PPS/Mbps
- **Graceful shutdown** – Ctrl+C with proper cleanup, thread tracking
- **Cross-platform** – Linux, Windows, macOS, Kali, Parrot (no privileges required)
- **Interactive menu only** – No CLI arguments needed  
- **Real-time monitoring** – Active threads, packets, bytes, throughput
- **Persistent config** – Settings saved/loaded to config.json  
- **DNS resolution** – Works with any URL or IP address  

---

## 📦 Installation

### Clone Repository

```bash
git clone https://github.com/DEVTHAKUR-90/DDoS_Attack.git
cd DDoS_Attack
```

### No Dependencies

No external packages required. Built on Python standard library only.

```bash
python3 --version  # Verify Python 3.8+
python3 attack.py  # Run
```

---

## 🎯 Usage

### Start Application

```bash
python3 attack.py
```

### Interactive Menu

Follow prompts:
1. **Enter Target** – IP:port, hostname, or full URL (e.g., `example.com`, `192.168.1.1:8080`, `https://example.com/api`)
2. **Select Attack Type** – Choose from 8 vectors
3. **Configure Performance** – Threads (100-20000), duration (0=unlimited), batch size (100-10000)
4. **Review Summary** – Confirm settings before launch
5. **Monitor Metrics** – Real-time PPS, Mbps, active thread count
6. **Stop** – Press Ctrl+C for graceful shutdown

---

## 🔥 Attack Vectors (8 Total)

|  # | Attack Type | Layer | Speed | Use Case |
| -: | --- | --- | --- | --- |
|  1 | **HTTP Flood** | 7 (Application) | 150+ Mbps | Web/API exhaustion |
|  2 | **TCP Flood** | 4 (Transport) | 400+ Mbps | Connection exhaustion |
|  3 | **UDP Flood** | 4 (Transport) | 800+ Mbps | Maximum throughput |
|  4 | **Slowloris** | 7 (Application) | Stealthy | Connection starvation |
|  5 | **ICMP Flood** | 3 (Network) | Fast | Ping flood |
|  6 | **DNS Flood** | Application | Query-based | DNS amplification |
|  7 | **SSL/TLS Flood** | 7 (Application) | CPU burn | Handshake exhaustion |
|  8 | **Multi-Vector** | Mixed | 1000+ Mbps | Simultaneous multi-layer |

> **⚠️ Use only against systems you own or have explicit written authorization to test.**

---

## 📊 Monitoring & Control

Real-time metrics displayed every 2 seconds:

* **Packets Sent** – Total packets/requests transmitted
* **Bytes Sent** – Total bytes transferred
* **PPS** – Packets per second
* **Mbps** – Megabits per second throughput
* **Active Threads** – Currently running worker threads
* **Duration** – Elapsed time and remaining time
* **Ctrl+C** – Graceful stop with cleanup

---

## ⚙️ Configuration

**Main Menu Options:**
* **Launch Attack** – Configure and run attack
* **View Settings** – Show current configuration
* **Advanced Settings** – Tune performance
* **Save Settings** – Persist to config.json
* **Load Settings** – Restore saved settings
* **System Info** – OS and Python version
* **Help** – Attack types & tips

**Advanced Tuning (Menu 3):**
* Payload Size – 64 to 65535 bytes
* Batch Size – 100 to 10000 packets/cycle
* Connection Timeout – 1 to 30 seconds
* Socket Buffer – 1MB to 256MB
* Random Ports – ON/OFF toggle

---

## 📁 Repository Structure

```text
DDoS_Attack/
├── attack.py               # Main application (33KB, 1000 lines)
├── config.json             # Persistent settings
├── requirements.txt        # Dependencies (empty)
├── README.md               # Documentation
└── LICENSE                 # License terms
```

---

## ⚠️ Important Notes

* **No elevated privileges required** – Works as standard user on all platforms
* **No external dependencies** – Uses Python standard library only
* **Always test systems you own** or have **explicit written permission** to test
* Prefer an isolated laboratory or dedicated test environment
* Keep testing within agreed scope, duration, and traffic limits
* This project is **educational and authorized security-testing purposes only**
* Complete reaudit: All bugs fixed, thread-safe, bulletproof socket lifecycle
* Monitor system resources during high-load testing (10000+ threads)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.


## 👤 Author

**Dev Thakur**

- GitHub: [@DEVTHAKUR-90](https://github.com/DEVTHAKUR-90)
- Repo: [DDoS_Attack](https://github.com/DEVTHAKUR-90/DDoS_Attack.git)
