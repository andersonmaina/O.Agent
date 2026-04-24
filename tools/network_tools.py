"""
Network utilities and IP manipulation tools
"""

import socket
import re
from typing import Dict, List, Optional


def is_valid_ip(ip: str) -> bool:
    """Check if string is a valid IP address (IPv4 or IPv6)."""
    return is_valid_ipv4(ip) or is_valid_ipv6(ip)


def is_valid_ipv4(ip: str) -> bool:
    """Check if string is a valid IPv4 address."""
    pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    return re.match(pattern, ip) is not None


def is_valid_ipv6(ip: str) -> bool:
    """Check if string is a valid IPv6 address."""
    pattern = r'^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$'
    return re.match(pattern, ip) is not None


def get_local_ip() -> str:
    """Get local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def get_hostname() -> str:
    """Get system hostname."""
    return socket.gethostname()


def get_host_by_name(ip: str) -> str:
    """Get hostname from IP address."""
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return "Unknown"


def get_ip_by_name(hostname: str) -> str:
    """Get IP address from hostname."""
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return "Unknown"


def is_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    """Check if a port is open on a host."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def parse_mac_address(mac: str) -> str:
    """Normalize MAC address format."""
    mac = mac.replace(":", "").replace("-", "").replace(".", "").upper()
    if len(mac) != 12:
        return "Invalid MAC address"
    return ":".join(mac[i:i+2] for i in range(0, 12, 2))


def is_valid_mac_address(mac: str) -> bool:
    """Check if string is a valid MAC address."""
    pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    return re.match(pattern, mac) is not None


def ip_to_int(ip: str) -> int:
    """Convert IPv4 address to integer."""
    if not is_valid_ipv4(ip):
        raise ValueError("Invalid IPv4 address")
    octets = ip.split(".")
    return (int(octets[0]) << 24) + (int(octets[1]) << 16) + (int(octets[2]) << 8) + int(octets[3])


def int_to_ip(num: int) -> str:
    """Convert integer to IPv4 address."""
    return f"{(num >> 24) & 255}.{(num >> 16) & 255}.{(num >> 8) & 255}.{num & 255}"


def get_subnet_mask(cidr: int) -> str:
    """Get subnet mask from CIDR notation."""
    if not 0 <= cidr <= 32:
        raise ValueError("CIDR must be between 0 and 32")
    mask = (0xFFFFFFFF << (32 - cidr)) & 0xFFFFFFFF
    return int_to_ip(mask)


def is_private_ip(ip: str) -> bool:
    """Check if IP is in private range."""
    if not is_valid_ipv4(ip):
        return False
    octets = [int(x) for x in ip.split(".")]
    # 10.0.0.0/8
    if octets[0] == 10:
        return True
    # 172.16.0.0/12
    if octets[0] == 172 and 16 <= octets[1] <= 31:
        return True
    # 192.168.0.0/16
    if octets[0] == 192 and octets[1] == 168:
        return True
    # 127.0.0.0/8 (loopback)
    if octets[0] == 127:
        return True
    return False


def is_loopback_ip(ip: str) -> bool:
    """Check if IP is loopback address."""
    return ip.startswith("127.")


def get_network_address(ip: str, cidr: int) -> str:
    """Get network address from IP and CIDR."""
    ip_int = ip_to_int(ip)
    mask = (0xFFFFFFFF << (32 - cidr)) & 0xFFFFFFFF
    network_int = ip_int & mask
    return int_to_ip(network_int)


def get_broadcast_address(ip: str, cidr: int) -> str:
    """Get broadcast address from IP and CIDR."""
    ip_int = ip_to_int(ip)
    mask = (0xFFFFFFFF << (32 - cidr)) & 0xFFFFFFFF
    broadcast_int = (ip_int & mask) | (~mask & 0xFFFFFFFF)
    return int_to_ip(broadcast_int)


def count_ips_in_subnet(cidr: int) -> int:
    """Count total IPs in a subnet."""
    if not 0 <= cidr <= 32:
        raise ValueError("CIDR must be between 0 and 32")
    return 2 ** (32 - cidr)


def is_valid_port(port: int) -> bool:
    """Check if port number is valid."""
    return isinstance(port, int) and 0 <= port <= 65535


def get_common_ports() -> Dict[int, str]:
    """Get dictionary of common ports and their services."""
    return {
        21: "FTP",
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        53: "DNS",
        80: "HTTP",
        110: "POP3",
        143: "IMAP",
        443: "HTTPS",
        993: "IMAPS",
        995: "POP3S",
        3306: "MySQL",
        5432: "PostgreSQL",
        6379: "Redis",
        8080: "HTTP-Alt",
        27017: "MongoDB",
    }
