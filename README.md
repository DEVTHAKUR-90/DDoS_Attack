# ⚡ QUANTUM BRUTEFORCE – Ultimate Stress Testing Framework
<div align="center">

<pre>
██████╗ ██╗   ██╗ █████╗ ███╗   ██╗████████╗██╗   ██╗███╗   ███╗
██╔══██╗██║   ██║██╔══██╗████╗  ██║╚══██╔══╝██║   ██║████╗ ████║
██████╔╝██║   ██║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║
██╔══██╗██║   ██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║
██████╔╝╚██████╔╝██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║
╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝
</pre>

</div>

**For Authorized Security Testing Only**

---

## 🚨 LEGAL DISCLAIMER

**This tool is for AUTHORIZED SECURITY TESTING only.**  
Using it against any target without explicit **written permission** is **ILLEGAL**.  
You are solely responsible for your actions. The authors assume **zero liability** for misuse.

---

## 🚀 Features

- **8 attack vectors** – HTTP, UDP, SYN, Slowloris, DNS, ICMP, SSL, Multi‑Vector  
- **Brutal performance** – up to **5000 threads**, oversized packets (65507 bytes), pipelining  
- **Automatic fallback** – if one attack fails, another kicks in instantly  
- **Stop command** – type `stop` to halt attack gracefully  
- **Cross‑platform** – works on **Linux, Windows, macOS** (raw sockets need root/admin on Unix)  
- **Interactive menu** + command‑line arguments  
- **Real‑time stats** with progress bar  
- **Thread‑safe** – shared counter with lock, no race conditions  
- **Resolves any domain** – works with any URL or IP  

---

## 📦 Installation

### Quick install (Linux/macOS)
```bash
git clone https://github.com/DEVTHAKUR-90/DDoS_Attack.git
cd DDoS_Attack
chmod +x setup.sh
./setup.sh

### Manual Install (Windows / Linux / macOS)

```bash
pip3 install -r requirements.txt
```

---

## 🎯 Usage

### Interactive Mode

```bash
python3 quantum_bruteforce.py
```

### Command-Line Mode

```bash
python3 quantum_bruteforce.py --target example.com --port 80 --threads 500 --duration 60
```
---

**Arguments:**

* `--target` – Target URL, IP address, or domain
* `--port` – Override the target port
* `--threads` – Number of worker threads
* `--duration` – Test duration in seconds
* `--type` – Test mode
* `--verbose` – Show additional runtime information

---

## 🔥 Test Types (Menu)

|  # | Test Type                   | Description                                                       |
| -: | --------------------------- | ----------------------------------------------------------------- |
|  1 | **HTTP Testing**            | HTTP request testing                                              |
|  2 | **UDP Testing**             | UDP traffic testing                                               |
|  3 | **TCP SYN Testing**         | TCP SYN testing; may require elevated privileges                  |
|  4 | **Slow Connection Testing** | Persistent connection testing                                     |
|  5 | **DNS Testing**             | DNS query testing                                                 |
|  6 | **ICMP Testing**            | ICMP traffic testing; may require elevated privileges             |
|  7 | **TLS Testing**             | TLS connection testing                                            |
|  8 | **Multi-Vector Testing**    | Combines supported testing modes                                  |
|  9 | **Advanced L7 Testing**     | Application-layer testing                                         |
| 10 | **NTP/Memcached Testing**   | Controlled amplification testing in an authorized lab environment |

> **⚠️ Use all testing modes only against systems you own or have explicit written authorization to test.**

---

## 🛡️ Fallback Mechanism

If a supported test operation fails because of a network error, timeout, or exception, the application can use its fallback mechanism to continue the authorized test while recording the failure in the runtime statistics.

---

## 📊 Monitoring & Control

The application provides:

* Real-time packet/request counters
* Current activity rate
* Active thread count
* Test duration
* Fallback and failure statistics
* Runtime status
* `Ctrl+C` support for stopping the test
* `stop` command in interactive mode

---

## 🛠️ Tools Menu

The tools menu provides utilities for authorized network diagnostics, including:

* **CF-IP Check** – Network/DNS diagnostic utility
* **Ping** – Check host reachability
* **HTTP Check** – Check HTTP response status
* **DNS Lookup** – DNS lookup utility
* **DSTAT** – System resource monitoring

---

## ⚙️ Configuration

Available configuration options include:

* Maximum threads (`1–5000`)
* Packet/request size
* Connection timeout (`1–30s`)
* Proxy configuration where supported
* Proxy file path where supported
* Verbose mode
* Reset to default settings

---

## 📁 Repository Structure

```text
quantum-bruteforce/
├── quantum_bruteforce.py   # Main application
├── setup.sh                # Installer
├── requirements.txt        # Dependencies
├── README.md               # Documentation
└── LICENSE                 # License terms
```

---

## ⚠️ Important Notes

* Some network testing modes may require **root/administrator privileges**.
* Only use proxy functionality with infrastructure you are authorized to use.
* Always test systems you own or have **explicit written permission** to test.
* Prefer an isolated laboratory or dedicated test environment for high-volume testing.
* Keep testing within the agreed scope, duration, and traffic limits.
* This project is provided for **educational and authorized security-testing purposes only**.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.


## 👤 Author

**Dev Thakur**

- GitHub: [@DEVTHAKUR-90](https://github.com/DEVTHAKUR-90)
- Repo: [onedrive-nuke](https://github.com/DEVTHAKUR-90/DDoS_Attack.git)
