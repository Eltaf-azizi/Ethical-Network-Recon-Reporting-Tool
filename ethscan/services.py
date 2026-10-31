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


    # --- Plain TCP -----------------------------------------------------
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=timeout
        )
    except Exception:
        return ""

    banner = ""
    try:
        # 1) Passive read (SSH, SMTP, FTP, MySQL, ...)
        try:
            data = await asyncio.wait_for(
                reader.read(2048), timeout=min(timeout, 1.5)
            )
            if data:
                banner = data.decode("utf-8", errors="ignore").strip()
        except asyncio.TimeoutError:
            pass

        # 2) HTTP probe
        if not banner and port in _HTTP_PORTS:
            try:
                writer.write(
                    b"HEAD / HTTP/1.1\r\nHost: "
                    + host.encode("utf-8", errors="ignore")
                    + b"\r\nConnection: close\r\n\r\n"
                )
                await writer.drain()
                data = await asyncio.wait_for(reader.read(2048), timeout=timeout)
                if data:
                    banner = data.decode("utf-8", errors="ignore").strip()
            except Exception:
                pass

        # 3) Redis PING (safe, read-only)
        if not banner and port == 6379:
            try:
                writer.write(b"PING\r\n")
                await writer.drain()
                data = await asyncio.wait_for(reader.read(256), timeout=timeout)
                if data:
                    banner = data.decode("utf-8", errors="ignore").strip()
            except Exception:
                pass

        # 4) Generic nudge
        if not banner:
            try:
                writer.write(b"\r\n")
                await writer.drain()
                data = await asyncio.wait_for(reader.read(1024), timeout=1.0)
                if data:
                    banner = data.decode("utf-8", errors="ignore").strip()
            except Exception:
                pass
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass

    return safe_truncate(banner, MAX_BANNER_LENGTH)


_OS_MARKERS: dict[str, str] = {
    "ubuntu": "Ubuntu",
    "debian": "Debian",
    "centos": "CentOS",
    "red hat": "Red Hat",
    "rhel": "Red Hat",
    "fedora": "Fedora",
    "alpine": "Alpine",
    "windows": "Windows",
    "microsoft": "Windows",
    "freebsd": "FreeBSD",
    "openbsd": "OpenBSD",
    "netbsd": "NetBSD",
    "darwin": "macOS",
    "linux": "Linux",
}



def infer_os(results) -> dict | None:
    """
    Very basic OS hint from banners. Returns None if there's no evidence.
    """
    evidence: list[str] = []
    seen: set[str] = set()

    for r in results:
        if getattr(r, "state", None) != "open" or not getattr(r, "banner", ""):
            continue
        lowered = r.banner.lower()
        for key, label in _OS_MARKERS.items():
            if key in lowered and label not in seen:
                seen.add(label)
                evidence.append(f"Port {r.port} banner contains '{key}'")

    if not evidence:
        return None

    if "Windows" in seen:
        family, confidence = "Windows", "low"
    elif "Ubuntu" in seen:
        family, confidence = "Linux (Ubuntu)", "medium"
    elif "Debian" in seen:
        family, confidence = "Linux (Debian)", "medium"
    elif {"Red Hat", "CentOS", "Fedora"} & seen:
        family, confidence = "Linux (RHEL-family)", "medium"
    elif {"FreeBSD", "OpenBSD", "NetBSD"} & seen:
        family, confidence = "BSD", "medium"
    elif "macOS" in seen:
        family, confidence = "macOS", "low"
    elif "Linux" in seen:
        family, confidence = "Linux", "low"
    else:
        family, confidence = "Unknown", "low"

    return {
        "family": family,
        "confidence": confidence,
        "ttl": None,  # requires raw sockets / root; deliberately omitted
        "evidence": evidence,
    }