import os
import sys
import time
import concurrent.futures
import requests
import threading
from collections import defaultdict

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    END = '\033[0m'

class ProxyChecker:
    def __init__(self, timeout=10, test_url='https://ipinfo.io/json'):
        self.timeout = timeout
        self.test_url = test_url
        self.checked_proxies = {
            'http': [],
            'https': [],
            'socks4': [],
            'socks5': [],
            'dead': 0
        }
        self.lock = threading.Lock()
        self.proxy_stats = defaultdict(int)

    def print_banner(self):
        banner = f"""
{Colors.CYAN}
██████╗ ██████╗  ██████╗ ██╗  ██╗██╗   ██╗
██╔══██╗██╔══██╗██╔═══██╗╚██╗██╔╝╚██╗ ██╔╝
██████╔╝██████╔╝██║   ██║ ╚███╔╝  ╚████╔╝ 
██╔═══╝ ██╔══██╗██║   ██║ ██╔██╗   ╚██╔╝  
██║     ██║  ██║╚██████╔╝██╔╝ ██╗   ██║   
╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   
{Colors.END}"""
        print(banner)
        print(f"{Colors.YELLOW}Proxy Checker v2.0 | Made with Black hat Edition{Colors.END}\n")

    def _test_proxy(self, proxy, protocol):
        try:
            # Parse authentication and host
            if '@' in proxy:
                auth, hostport = proxy.split('@', 1)
                user, password = auth.split(':', 1)
                host, port = hostport.rsplit(':', 1)
            else:
                user, password = None, None
                host, port = proxy.rsplit(':', 1)

            # Build proxy URL
            if protocol in ['http', 'https']:
                scheme = protocol
                proxy_url = f"{scheme}://{host}:{port}"
                if user and password:
                    proxy_url = f"{scheme}://{user}:{password}@{host}:{port}"
            else:  # SOCKS
                scheme = 'socks5' if protocol == 'socks5' else 'socks4'
                proxy_url = f"{scheme}://{host}:{port}"
                if user and password:
                    proxy_url = f"{scheme}://{user}:{password}@{host}:{port}"

            proxies = {'http': proxy_url, 'https': proxy_url}
            start_time = time.time()
            
            # Test proxy connection
            response = requests.get(
                self.test_url,
                proxies=proxies,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                latency = int((time.time() - start_time) * 1000)
                ip_data = response.json()
                country = ip_data.get('country', 'Unknown')
                
                with self.lock:
                    self.checked_proxies[protocol].append(proxy)
                    print(f"{Colors.GREEN}[+] LIVE {protocol.upper()} {proxy} | {country} | {latency}ms{Colors.END}")
                return True
                
        except Exception as e:
            return False

    def check_proxy(self, proxy):
        found_valid = False
        protocols = ['http', 'https', 'socks4', 'socks5']
        
        for protocol in protocols:
            if self._test_proxy(proxy, protocol):
                found_valid = True
                self.proxy_stats[protocol] += 1
            else:
                self.proxy_stats['dead'] += 1
                
        if not found_valid:
            with self.lock:
                print(f"{Colors.RED}[-] DEAD {proxy}{Colors.END}")

    def save_proxies(self):
        os.makedirs('checked_proxies', exist_ok=True)
        for protocol in ['http', 'https', 'socks4', 'socks5']:
            if self.checked_proxies[protocol]:
                with open(f'checked_proxies/{protocol}_proxies.txt', 'w') as f:
                    f.write('\n'.join(self.checked_proxies[protocol]))

    def show_stats(self):
        print(f"\n{Colors.CYAN}=== CHECKING STATISTICS ===")
        print(f"{Colors.WHITE}HTTP Proxies:   {Colors.GREEN}{self.proxy_stats['http']}")
        print(f"{Colors.WHITE}HTTPS Proxies:  {Colors.GREEN}{self.proxy_stats['https']}")
        print(f"{Colors.WHITE}SOCKS4 Proxies: {Colors.GREEN}{self.proxy_stats['socks4']}")
        print(f"{Colors.WHITE}SOCKS5 Proxies: {Colors.GREEN}{self.proxy_stats['socks5']}")
        print(f"{Colors.WHITE}Dead Checks:    {Colors.RED}{self.proxy_stats['dead']}{Colors.END}")

    def start_check(self, proxy_file):
        if not os.path.exists(proxy_file):
            print(f"{Colors.RED}[!] Proxy file not found!{Colors.END}")
            return

        with open(proxy_file, 'r') as f:
            proxies = [line.strip() for line in f if line.strip()]

        print(f"\n{Colors.YELLOW}[*] Checking {len(proxies)} proxies...{Colors.END}")
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            executor.map(self.check_proxy, proxies)
            
        self.save_proxies()
        self.show_stats()
        print(f"{Colors.YELLOW}\n[!] Completed in {time.time()-start_time:.2f} seconds{Colors.END}")

if __name__ == "__main__":
    checker = ProxyChecker()
    checker.print_banner()
    
    if len(sys.argv) != 2:
        print(f"{Colors.RED}[!] Usage: {sys.argv[0]} <proxy_file>{Colors.END}")
        sys.exit(1)
        
    checker.start_check(sys.argv[1])
