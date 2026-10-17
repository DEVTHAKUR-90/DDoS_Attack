#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cross-platform setup script for Quantum Bruteforce v9.0
Works on Windows, Linux, macOS
"""

import os
import sys
import platform
import subprocess

PLATFORM_OS = platform.system()

def banner():
    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║         QUANTUM BRUTEFORCE v9.0 - SETUP INSTALLER            ║
║         FOR AUTHORIZED SECURITY TESTING ONLY                 ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)

def check_python():
    """Check if Python 3.6+ is installed."""
    if sys.version_info < (3, 6):
        print(f"[!] Python 3.6+ required. You have {sys.version}")
        sys.exit(1)
    print(f"[+] Python {sys.version.split()[0]} detected")

def install_dependencies():
    """Install required packages."""
    print("[+] Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("[+] Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("[!] Failed to install dependencies")
        print("[*] Try manual install: pip3 install -r requirements.txt")
        return False

def make_executable():
    """Make script executable on Unix systems."""
    if PLATFORM_OS in ('Linux', 'Darwin'):
        try:
            os.chmod("quantum_bruteforce_v9.py", 0o755)
            print("[+] Made script executable")
        except:
            pass

def create_config():
    """Create default config file if it doesn't exist."""
    import json
    config_file = "quantum_config.json"

    if os.path.exists(config_file):
        print("[+] Config file already exists")
        return

    default_config = {
        "max_threads": 5000,
        "packet_size": 1472,
        "timeout": 5,
        "buffer_size": 16777216,
        "batch_size": 100,
        "reconnect_threshold": 50,
        "verbose": False,
        "kernel_tune": True
    }

    try:
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        print("[+] Created default config file")
    except Exception as e:
        print(f"[!] Failed to create config: {e}")

def main():
    banner()

    print(f"[+] Platform: {PLATFORM_OS}")

    try:
        check_python()
        install_dependencies()
        make_executable()
        create_config()

        print("\n" + "="*65)
        print("|                  INSTALLATION COMPLETE                       |")
        print("="*65)
        print("|                                                              |")
        print("|  ✅ All dependencies installed                               |")
        print("|  🚀 Run: python3 quantum_bruteforce_v9.py                    |")
        print("|                                                              |")
        print("|  ⚠️  REMEMBER: For authorized testing only!                 |")
        print("|                                                              |")
        print("="*65)

    except KeyboardInterrupt:
        print("\n[!] Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] Setup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
