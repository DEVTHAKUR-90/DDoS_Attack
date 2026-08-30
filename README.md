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
git clone https://github.com/DEVTHAKUR-90/DDOS_Attack.git
cd quantum-bruteforce
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

### Arguments

| Argument     | Description                               |
| ------------ | ----------------------------------------- |
| `--target`   | IP address or domain                      |
| `--port`     | Target port (default: `80`)               |
| `--threads`  | Number of worker threads (default: `200`) |
| `--duration` | Test duration in seconds                  |
| `--type`     | Test mode                                 |
| `--verbose`  | Show additional runtime information       |

---

## 🧪 Test Modes

| # | Mode                   | Description                            |
| - | ---------------------- | -------------------------------------- |
| 1 | **HTTP Testing**       | HTTP request load testing              |
| 2 | **UDP Testing**        | UDP traffic testing                    |
| 3 | **TCP Testing**        | TCP connection testing                 |
| 4 | **Connection Testing** | Connection/resource exhaustion testing |
| 5 | **DNS Testing**        | DNS query testing                      |
| 6 | **ICMP Testing**       | ICMP connectivity/load testing         |
| 7 | **TLS Testing**        | TLS connection testing                 |
| 8 | **Multi-Mode Testing** | Combines supported test modes          |

> **Important:** Only use test modes against systems you own or where you have explicit authorization.

---

## 📊 Monitoring

The application provides runtime information including:

* Real-time packet/request counters
* Current activity rate
* Active thread count
* Total test duration
* Runtime errors and failures
* Test status

---

## ⚙️ Configuration

Configuration can be accessed through the interactive menu.

Available settings include:

* Maximum worker threads
* Packet/request size
* Connection timeout
* Verbose output
* Reset to default settings

---

## 🛑 Stopping a Test

You can stop a running test by:

* Pressing `Ctrl+C`
* Using the application's stop command

---

## 📝 Example

```text
Choose option: 1
Target: example.com
Port: 80
Duration: 60
Threads: 100
```

---

## 🧩 Requirements

* Python 3.6+
* `colorama`
* `tqdm`
* Dependencies listed in `requirements.txt`
* Appropriate permissions for tests that require elevated privileges

Install dependencies with:

```bash
pip3 install -r requirements.txt
```

---

## 📁 Repository Structure

```text
quantum-bruteforce/
├── quantum_bruteforce.py   # Main application
├── setup.sh                # Installer
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

---

## ⚠️ Important Notes

* Use this software **only on systems you own or have explicit written authorization to test**.
* Do not test third-party infrastructure without permission.
* Elevated privileges may be required for certain network diagnostics.
* Keep test duration and resource consumption within the limits agreed upon for your test environment.
* Run experiments in an isolated lab whenever possible.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.


## 👤 Author

**Dev Thakur**

- GitHub: [@DEVTHAKUR-90](https://github.com/DEVTHAKUR-90)
- Repo: [onedrive-nuke](https://github.com/DEVTHAKUR-90/DDOS_Attack.git)
