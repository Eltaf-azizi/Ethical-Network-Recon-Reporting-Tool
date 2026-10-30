"""
Service identification, banner grabbing, and a basic OS hint.

Design notes:
- We only attempt protocol-specific probes for a small set of well-known
  services. Anything else gets a generic read.
- The OS hint is a hint. The report says so. Do not overclaim.
"""

import asyncio
import ssl

from .constants import MAX_BANNER_LENGTH
from .utils import safe_truncate


SERVICES: dict[int, str] = {
    20: "ftp-data", 21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp",
    53: "domain", 67: "dhcp", 68: "dhcp", 69: "tftp", 80: "http",
    110: "pop3", 111: "rpcbind", 119: "nntp", 123: "ntp",
    135: "msrpc", 137: "netbios-ns", 139: "netbios-ssn",
    143: "imap", 161: "snmp", 162: "snmptrap", 179: "bgp",
    194: "irc", 389: "ldap", 443: "https", 445: "microsoft-ds",
    465: "smtps", 514: "syslog", 515: "printer", 548: "afpovertcp",
    554: "rtsp", 587: "submission", 631: "ipp", 636: "ldaps",
    873: "rsync", 902: "vmware-auth", 989: "ftps-data", 990: "ftps",
    993: "imaps", 995: "pop3s", 1080: "socks", 1194: "openvpn",
    1433: "ms-sql-s", 1521: "oracle", 1723: "pptp", 2049: "nfs",
    2082: "cpanel", 2083: "cpanel-ssl", 2181: "zookeeper",
    2375: "docker", 2376: "docker-ssl", 3128: "squid",
    3306: "mysql", 3389: "ms-wbt-server", 4444: "metasploit",
    5000: "upnp", 5432: "postgresql", 5601: "kibana",
    5672: "amqp", 5900: "vnc", 5984: "couchdb", 6379: "redis",
    7001: "weblogic", 8000: "http-alt", 8008: "http-alt",
    8080: "http-proxy", 8081: "http-alt", 8443: "https-alt",
    8888: "http-alt", 9000: "cslistener", 9090: "websm",
    9200: "elasticsearch", 9300: "elasticsearch",
    11211: "memcached", 27017: "mongodb", 27018: "mongodb",
    50000: "sap", 61616: "activemq",
}

_TLS_PORTS = {443, 8443, 636, 993, 995, 465, 990}
_HTTP_PORTS = {80, 8000, 8008, 8080, 8081, 8888, 5000, 9000, 9090}


def service_for_port(port: int) -> str:
    """Return a best-effort service name for a port."""
    return SERVICES.get(port, "unknown")


async def grab_banner(host: str, port: int, timeout: float) -> str:
    """
    Best-effort banner grab. Never raises — returns "" if nothing is read.
    """
    # --- TLS ports -----------------------------------------------------
    if port in _TLS_PORTS:
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port, ssl=ctx),
                timeout=timeout,
            )
            sslobj = writer.get_extra_info("ssl_object")
            if sslobj is not None:
                version = sslobj.version() or "?"
                cipher = sslobj.cipher()
                cipher_name = cipher[0] if cipher else "?"
                banner = f"TLS {version} / {cipher_name}"
            else:
                banner = ""
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
            return safe_truncate(banner, MAX_BANNER_LENGTH)
        except Exception:
            return ""
