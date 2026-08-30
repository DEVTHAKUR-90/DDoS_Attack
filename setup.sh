#!/bin/bash
clear
echo -e "\033[36m"
cat << "EOF"
+----------------------------------------------------------------------+
|                                                                      |
|   ██████╗ ██╗   ██╗ █████╗ ███╗   ██╗████████╗██╗   ██╗███╗   ███╗   |
|   ██╔══██╗██║   ██║██╔══██╗████╗  ██║╚══██╔══╝██║   ██║████╗ ████║   |
|   ██████╔╝██║   ██║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║   |
|   ██╔══██╗██║   ██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║   |
|   ██████╔╝╚██████╔╝██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║   |
|   ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝   |
|                                                                      |
|              QUANTUM BRUTEFORCE – INSTALLER                          |
|              FOR AUTHORIZED SECURITY TESTING ONLY                    |
|                                                                      |
+----------------------------------------------------------------------+
EOF
echo -e "\033[0m"

echo -e "\033[93m[+] Installing Quantum Bruteforce...\033[0m"

if ! command -v python3 &> /dev/null; then
    echo -e "\033[91m[!] Python3 not found! Please install Python 3.6+.\033[0m"
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo -e "\033[91m[!] pip3 not found! Installing...\033[0m"
    sudo apt-get update -y > /dev/null 2>&1
    sudo apt-get install -y python3-pip > /dev/null 2>&1
fi

echo -e "\033[93m[+] Installing dependencies...\033[0m"
pip3 install --upgrade pip > /dev/null 2>&1
pip3 install -r requirements.txt > /dev/null 2>&1

chmod +x quantum_bruteforce.py

echo -e "\033[92m"
echo "+----------------------------------------------------------------------+"
echo "|                   INSTALLATION COMPLETE                              |"
echo "+----------------------------------------------------------------------+"
echo "|                                                                      |"
echo "|  ✅ All dependencies installed.                                      |"
echo "|  🚀 Run: python3 quantum_bruteforce.py                               |"
echo "|                                                                      |"
echo "|  ⚠️  REMEMBER: For authorized testing only!                          |"
echo "|                                                                      |"
echo "+----------------------------------------------------------------------+"
echo -e "\033[0m"