#!/usr/bin/env python3
# ADVANCED PROXY CHECKER - SHADOW NETWORKS

import os
import sys
import time
import requests
import concurrent.futures
from socket import socket, AF_INET, SOCK_STREAM
from urllib.parse import urlparse

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    END = '\033[0m'

BANNER = f"""{Colors.RED}
  ██████  ██▓  ▄████  ███▄ ▄███▓ ▄▄▄        ▄████  ██░ ██  ▒█████    ██████ ▄▄▄█████▓
▒██    ▒ ▓██▒ ██▒ ▀█▒▓██▒▀█▀ ██▒▒████▄     ██▒ ▀█▒▓██░ ██▒▒██▒  ██▒▒██    ▒ ▓  ██▒ ▓▒
░ ▓██▄   ▒██▒▒██░▄▄▄░▓██    ▓██░▒██  ▀█▄  ▒██░▄▄▄░▒██▀▀██░▒██░  ██▒░ ▓██▄   ▒ ▓██░ ▒░
  ▒   ██▒░██░░▓█  ██▓▒██    ▒██ ░██▄▄▄▄██ ░▓█  ██▓░▓█ ░██ ▒██   ██░  ▒   ██▒░ ▓██▓ ░ 
▒██████▒▒░██░░▒▓███▀▒▒██▒   ░██▒ ▓█   ▓██▒░▒▓███▀▒░▓█▒░██▓░ ████▓▒░▒██████▒▒  ▒██▒ ░ 
▒ ▒▓▒ ▒ ░░▓   ░▒   ▒ ░ ▒░   ░  ░ ▒▒   ▓▒█░ ░▒   ▒  ▒ ░░▒░▒░ ▒░▒░▒░ ▒ ▒▓▒ ▒ ░  ▒ ░░   
░ ░▒  ░ ░ ▒ ░  ░   ░ ░  ░      ░  ▒   ▒▒ ░  ░   ░  ▒ ░▒░ ░  ░ ▒ ▒░ ░ ░▒  ░ ░    ░    
░  ░  ░   ▒ ░░ ░   ░ ░      ░     ░   ▒   ░ ░   ░  ░  ░░ ░░ ░ ░ ▒  ░  ░  ░    ░      
      ░   ░        ░        ░         ░  ░      ░  ░  ░  ░    ░ ░        ░           
                                                                                     
{Colors.END}
{Colors.RED}[+] SHADOW NETWORKS PROXY CHECKER
{Colors.RED}[+] CREATED BY WILLIAM - BLACK HAT EDITION
{Colors.RED}[!] WARNING: USE RESPONSIBLY - UNAUTHORIZED ACCESS ILLEGAL{Colors.END}
"""

class ProxyChecker:
    def __init__(self):
        self.checked_proxies = {
            'http': [],
            'https': [],
            'socks4': [],
            'socks5': [],
            'dead': 0
        }
        self.timeout = 10
        self.test_url = "https://ipinfo.io/json"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def print_banner(self):
        print(BANNER)

    def check_proxy(self, proxy):
        try:
            protocol, proxy = self.parse_proxy(proxy)
            if not protocol:
                return

            if protocol in ['http', 'https']:
                return self.check_http_proxy(proxy, protocol)
            elif protocol in ['socks4', 'socks5']:
                return self.check_socks_proxy(proxy, protocol)
                
        except Exception as e:
            self.checked_proxies['dead'] += 1
            return False

    def parse_proxy(self, proxy):
        if '://' not in proxy:
            proxy = f"http://{proxy}"
            
        parsed = urlparse(proxy)
        protocol = parsed.scheme.lower()
        netloc = parsed.netloc
        
        if '@' in netloc:
            auth, host = netloc.split('@', 1)
        else:
            auth, host = None, netloc
            
        if ':' in host:
            host, port = host.split(':', 1)
        else:
            port = 8080
            
        return protocol, f"{host}:{port}" if not auth else f"{auth}@{host}:{port}"

    def check_http_proxy(self, proxy, protocol):
        proxies = {
            "http": f"{protocol}://{proxy}",
            "https": f"{protocol}://{proxy}"
        }
        
        try:
            start = time.time()
            response = requests.get(self.test_url, 
                                   proxies=proxies,
                                   headers=self.headers,
                                   timeout=self.timeout)
            latency = int((time.time() - start) * 1000)
            
            if response.status_code == 200:
                ip_data = response.json()
                print(f"{Colors.GREEN}[+] LIVE {protocol.upper()} {proxy} | {ip_data['country']} | {latency}ms{Colors.END}")
                self.checked_proxies[protocol].append(proxy)
                return True
        except:
            self.checked_proxies['dead'] += 1
            print(f"{Colors.RED}[-] DEAD {proxy}{Colors.END}")
            return False

    def check_socks_proxy(self, proxy, protocol):
        try:
            host, port = proxy.split(':')
            if '@' in host:
                auth, host = host.split('@')
                user, password = auth.split(':')
            else:
                user, password = None, None

            sock = socket(AF_INET, SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((host, int(port)))
            
            if protocol == 'socks4':
                socks_proto = 0x01
            else:
                socks_proto = 0x02
                
            # SOCKS handshake
            sock.sendall(bytes([0x05, 0x01, 0x00]))
            auth_response = sock.recv(2)
            
            if auth_response == bytes([0x05, 0x00]):
                # Request connection to test URL
                sock.sendall(bytes([0x05, 0x01, 0x00, 0x03, len(host.encode())]) + host.encode() + bytes([int(port) >> 8, int(port) & 0xff]))
                response = sock.recv(10)
                
                if response[1] == 0x00:
                    start = time.time()
                    test_response = requests.get(self.test_url,
                                                proxies={'http': f"socks5://{proxy}"},
                                                timeout=self.timeout)
                    latency = int((time.time() - start) * 1000)
                    ip_data = test_response.json()
                    print(f"{Colors.GREEN}[+] LIVE {protocol.upper()} {proxy} | {ip_data['country']} | {latency}ms{Colors.END}")
                    self.checked_proxies[protocol].append(proxy)
                    return True
        except:
            self.checked_proxies['dead'] += 1
            print(f"{Colors.RED}[-] DEAD {proxy}{Colors.END}")
            return False
        finally:
            sock.close()

    def save_proxies(self):
        if not os.path.exists('checked_proxies'):
            os.makedirs('checked_proxies')
            
        for protocol in ['http', 'https', 'socks4', 'socks5']:
            with open(f'checked_proxies/{protocol}_proxies.txt', 'w') as f:
                f.write('\n'.join(self.checked_proxies[protocol]))

    def show_stats(self):
        print(f"\n{Colors.CYAN}=== CHECKING STATISTICS ===")
        print(f"{Colors.WHITE}HTTP Proxies: {Colors.GREEN}{len(self.checked_proxies['http'])}")
        print(f"{Colors.WHITE}HTTPS Proxies: {Colors.GREEN}{len(self.checked_proxies['https'])}")
        print(f"{Colors.WHITE}SOCKS4 Proxies: {Colors.GREEN}{len(self.checked_proxies['socks4'])}")
        print(f"{Colors.WHITE}SOCKS5 Proxies: {Colors.GREEN}{len(self.checked_proxies['socks5'])}")
        print(f"{Colors.WHITE}Dead Proxies: {Colors.RED}{self.checked_proxies['dead']}{Colors.END}")

    def start_check(self, proxy_file):
        if not os.path.exists(proxy_file):
            print(f"{Colors.RED}[!] Proxy file not found!{Colors.END}")
            return

        with open(proxy_file, 'r') as f:
            proxies = [line.strip() for line in f if line.strip()]

        print(f"\n{Colors.YELLOW}[*] Starting proxy check with {len(proxies)} proxies...{Colors.END}")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            executor.map(self.check_proxy, proxies)
            
        self.save_proxies()
        self.show_stats()

if __name__ == "__main__":
    checker = ProxyChecker()
    checker.print_banner()
    
    if len(sys.argv) != 2:
        print(f"{Colors.RED}[!] Usage: {sys.argv[0]} <proxy_file>{Colors.END}")
        sys.exit(1)
        
    checker.start_check(sys.argv[1])
