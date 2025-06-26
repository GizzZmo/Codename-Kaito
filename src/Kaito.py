import requests
import time
import sys

def check_vulnerabilities(target_url):
    """Check for common vulnerabilities in a web application"""
    
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

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 hacking_tool.py <target_url>")
        sys.exit(1)
    
    target_url = sys.argv[1]
    
    # Check for vulnerabilities
    vulnerable = check_vulnerabilities(target_url)
    
    # Report findings
    if vulnerable:
        print("[+] Target appears vulnerable!")
    else:
        print("[-] No obvious vulnerabilities detected.")

if __name__ == "__main__":
    main()
