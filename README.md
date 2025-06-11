# proxy_checker
💻 The ULTIMATE Proxy Checking Tool for Cybersecurity Professionals &amp; black hat Hackers!  🚀 Features: ✅ Supports HTTP, HTTPS, SOCKS4, SOCKS5 

HOW TO USE COMMANDS !

command ===> pip install requests
command ===> pip install pysocks

command ===> python3 proxy_checker.py your_proxies_list.txt

📝 How to Use:
Prepare Proxy List
Create a proxies.txt file with proxies in this format:

text
1.1.1.1:8080
user:pass@2.2.2.2:3128
http://3.3.3.3:80
socks5://4.4.4.4:1080
Execute Script
Run with your proxy list:

bash
python3 proxy_checker.py proxies.txt
Results
Working proxies are saved to:

checked_proxies/http_proxies.txt

checked_proxies/https_proxies.txt

checked_proxies/socks4_proxies.txt

checked_proxies/socks5_proxies.txt

