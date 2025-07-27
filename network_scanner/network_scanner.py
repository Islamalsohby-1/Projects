import socket
import ipaddress
import concurrent.futures
import requests
import ftplib
import telnetlib
import ssl
import time
import os
from datetime import datetime
from tabulate import tabulate
from typing import List, Dict, Tuple
import subprocess

# ANSI color codes for pretty output
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RESET = "\033[0m"

# Constants
COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995, 1433, 3306, 3389, 5900, 8080, 8443]
TIMEOUT = 1.0
LOG_FILE = "scan_log.txt"

def log_message(message: str) -> None:
    """Log messages to a file with a timestamp."""
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

def get_default_subnet() -> str:
    """Attempt to get the default subnet from the system's network configuration."""
    try:
        output = subprocess.check_output("ipconfig" if os.name == "nt" else "ifconfig", shell=True).decode()
        for line in output.splitlines():
            if "Subnet Mask" in line or "netmask" in line:
                if "255.255.255.0" in line:
                    ip_line = next((l for l in output.splitlines() if "IPv4 Address" in l or "inet " in l), None)
                    if ip_line:
                        ip = ip_line.split()[-1] if "IPv4 Address" in ip_line else ip_line.split()[1]
                        return f"{ip.rsplit('.', 1)[0]}.0/24"
        return "192.168.1.0/24"  # Fallback
    except subprocess.CalledProcessError:
        return "192.168.1.0/24"

def parse_ip_range(ip_range: str) -> List[str]:
    """Parse an IP range or subnet into a list of IP addresses."""
    try:
        network = ipaddress.ip_network(ip_range, strict=False)
        return [str(ip) for ip in network.hosts()]
    except ValueError as e:
        log_message(f"Error parsing IP range {ip_range}: {e}")
        print(f"{COLOR_RED}Error: Invalid IP range. Use format like '192.168.1.0/24'.{COLOR_RESET}")
        return []

def is_host_alive(ip: str) -> bool:
    """Check if a host is alive using a ping (ICMP echo request)."""
    try:
        param = "-n" if os.name == "nt" else "-c"
        result = subprocess.run(
            f"ping {param} 1 -w 1000 {ip}",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    except subprocess.SubprocessError:
        return False

def scan_port(ip: str, port: int) -> Tuple[str, int, str]:
    """Scan a single port on a given IP address."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        result = sock.connect_ex((ip, port))
        sock.close()
        return ip, port, "open" if result == 0 else "closed"
    except socket.error as e:
        log_message(f"Error scanning {ip}:{port}: {e}")
        return ip, port, "error"

def grab_banner(ip: str, port: int) -> str:
    """Attempt to grab a service banner for more detailed info."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        sock.connect((ip, port))
        banner = sock.recv(1024).decode("utf-8", errors="ignore").strip()
        sock.close()
        return banner[:100] or "No banner"
    except socket.error:
        return "No banner"

def check_ftp_anonymous(ip: str, port: int = 21) -> Tuple[str, str]:
    """Check if FTP allows anonymous login and grab banner."""
    try:
        ftp = ftplib.FTP()
        ftp.set_pasv(True)
        ftp.connect(ip, port, timeout=TIMEOUT)
        ftp.login("anonymous", "guest")
        ftp.quit()
        banner = grab_banner(ip, port)
        return "High", f"Anonymous FTP login allowed ({banner})"
    except ftplib.all_errors:
        return "Low", "Anonymous FTP login not allowed"

def check_ssh_telnet(ip: str, port: int) -> Tuple[str, str]:
    """Check if SSH or Telnet is open and grab banner."""
    try:
        banner = grab_banner(ip, port)
        if "SSH" in banner:
            return "Medium", f"SSH open, version: {banner}"
        return "High", f"Telnet open, version: {banner} (insecure protocol)"
    except socket.error:
        return "Low", "Telnet/SSH not accessible"

def check_http_headers(ip: str, port: int = 80) -> Tuple[str, str]:
    """Check HTTP server for info leakage and outdated versions."""
    try:
        url = f"http://{ip}:{port}"
        response = requests.get(url, timeout=TIMEOUT, allow_redirects=False)
        server = response.headers.get("Server", "Unknown")
        if server != "Unknown":
            # Simplified check for outdated versions
            if "Apache" in server and any(v in server for v in ["2.2", "2.4.0"]):
                return "High", f"Outdated HTTP server: {server}"
            return "Medium", f"HTTP server leaks info: {server}"
        return "Low", "No HTTP server info leaked"
    except requests.RequestException:
        return "Low", "HTTP server not accessible"

def check_smb(ip: str) -> Tuple[str, str]:
    """Check for open SMB shares."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        result = sock.connect_ex((ip, 445))
        sock.close()
        if result == 0:
            return "High", "SMB share open (potential unauthenticated access)"
        return "Low", "SMB share not accessible"
    except socket.error:
        return "Low", "SMB check error"

def check_ssl_cert(ip: str, port: int = 443) -> Tuple[str, str]:
    """Check for weak or self-signed SSL certificates."""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((ip, port), timeout=TIMEOUT) as sock:
            with context.wrap_socket(sock, server_hostname=ip) as ssock:
                cert = ssock.getpeercert()
                issuer = dict(x[0] for x in cert.get("issuer", []))
                not_after = cert.get("notAfter")
                if issuer.get("commonName") == ip or "self-signed" in str(cert).lower():
                    return "High", "Self-signed SSL certificate detected"
                if not_after and datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z") < datetime.now():
                    return "High", "Expired SSL certificate"
                return "Low", "SSL certificate appears valid"
    except (ssl.SSLError, socket.error) as e:
        return "Low", f"SSL check failed: {str(e)}"

def scan_host(ip: str) -> List[Dict[str, str]]:
    """Scan a single host for open ports and vulnerabilities."""
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_port = {executor.submit(scan_port, ip, port): port for port in COMMON_PORTS}
        for future in concurrent.futures.as_completed(future_to_port):
            ip, port, status = future.result()
            if status == "open":
                vuln_result = {"IP": ip, "Port": str(port), "Service": get_service_name(port), "Severity": "", "Vulnerabilities": ""}
                if port == 21:
                    severity, vuln = check_ftp_anonymous(ip, port)
                elif port in [22, 23]:
                    severity, vuln = check_ssh_telnet(ip, port)
                elif port in [80, 8080, 8443]:
                    severity, vuln = check_http_headers(ip, port)
                elif port == 445:
                    severity, vuln = check_smb(ip)
                elif port == 443:
                    severity, vuln = check_ssl_cert(ip, port)
                else:
                    severity, vuln = "Low", "No specific vulnerability check implemented"
                vuln_result["Severity"] = severity
                vuln_result["Vulnerabilities"] = vuln
                results.append(vuln_result)
    return results

def get_service_name(port: int) -> str:
    """Return the common service name for a given port."""
    services = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS", 80: "HTTP",
        110: "POP3", 135: "MS RPC", 139: "NetBIOS", 143: "IMAP", 443: "HTTPS",
        445: "SMB", 993: "IMAPS", 995: "POP3S", 1433: "MSSQL", 3306: "MySQL",
        3389: "RDP", 5900: "VNC", 8080: "HTTP-Alt", 8443: "HTTPS-Alt"
    }
    return services.get(port, "Unknown")

def print_progress(current: int, total: int) -> None:
    """Print a progress bar for the scan."""
    percent = (current / total) * 100
    bar_length = 50
    filled = int(bar_length * current // total)
    bar = "█" * filled + "-" * (bar_length - filled)
    print(f"\r{COLOR_YELLOW}Scanning: [{bar}] {percent:.1f}%{COLOR_RESET}", end="", flush=True)

def save_to_csv(results: List[Dict[str, str]], filename: str = "scan_results.csv") -> None:
    """Save scan results to a CSV file."""
    with open(filename, "w") as f:
        f.write("IP Address,Port,Service,Severity,Vulnerabilities\n")
        for result in results:
            f.write(f"{result['IP']},{result['Port']},{result['Service']},{result['Severity']},\"{result['Vulnerabilities']}\"\n")
    print(f"{COLOR_GREEN}Results saved to {filename}{COLOR_RESET}")

def generate_report(results: List[Dict[str, str]]) -> str:
    """Generate a formatted table report from scan results."""
    table_data = [[r["IP"], r["Port"], r["Service"], r["Severity"], r["Vulnerabilities"]] for r in results]
    headers = ["IP Address", "Port", "Service", "Severity", "Vulnerabilities"]
    return tabulate(table_data, headers=headers, tablefmt="fancy_grid")

def summarize_results(results: List[Dict[str, str]]) -> str:
    """Generate a summary of vulnerabilities by severity."""
    severity_counts = {"High": 0, "Medium": 0, "Low": 0}
    for result in results:
        severity_counts[result["Severity"]] += 1
    summary = f"\n{COLOR_YELLOW}Vulnerability Summary:{COLOR_RESET}\n"
    summary += f"  High Severity: {severity_counts['High']}\n"
    summary += f"  Medium Severity: {severity_counts['Medium']}\n"
    summary += f"  Low Severity: {severity_counts['Low']}\n"
    return summary

def main():
    """Main function to run the network scanner."""
    print(f"{COLOR_GREEN}=== Network Vulnerability Scanner ==={COLOR_RESET}")
    default_subnet = get_default_subnet()
    ip_range = input(f"Enter IP range or subnet (e.g., 192.168.1.0/24, default: {default_subnet}): ") or default_subnet
    print(f"{COLOR_YELLOW}Scanning IP range: {ip_range}{COLOR_RESET}")
    log_message(f"Starting scan for {ip_range}")
    start_time = time.time()

    # Parse IP range
    ip_list = parse_ip_range(ip_range)
    if not ip_list:
        print(f"{COLOR_RED}Exiting due to invalid IP range.{COLOR_RESET}")
        return

    # Host discovery
    print(f"{COLOR_YELLOW}Discovering live hosts...{COLOR_RESET}")
    live_ips = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(ip_list), 50)) as executor:
        future_to_ip = {executor.submit(is_host_alive, ip): ip for ip in ip_list}
        for i, future in enumerate(concurrent.futures.as_completed(future_to_ip), 1):
            ip = future_to_ip[future]
            if future.result():
                live_ips.append(ip)
            print_progress(i, len(ip_list))
    print(f"\n{COLOR_GREEN}Found {len(live_ips)} live hosts{COLOR_RESET}")

    # Scan live hosts
    all_results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(live_ips) * 2, 20)) as executor:
        future_to_ip = {executor.submit(scan_host, ip): ip for ip in live_ips}
        for i, future in enumerate(concurrent.futures.as_completed(future_to_ip), 1):
            all_results.extend(future.result())
            print_progress(i, len(live_ips))

    # Generate and print report
    print(f"\n\n{COLOR_GREEN}Scan Results ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}):{COLOR_RESET}")
    if all_results:
        print(generate_report(all_results))
        print(summarize_results(all_results))
        save_to_csv(all_results)
    else:
        print(f"{COLOR_YELLOW}No open ports or vulnerabilities found.{COLOR_RESET}")

    print(f"{COLOR_GREEN}Scan completed in {time.time() - start_time:.2f} seconds.{COLOR_RESET}")
    log_message(f"Scan completed in {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
