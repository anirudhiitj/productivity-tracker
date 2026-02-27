"""
Network mapper that associates processes with network connections.
Uses psutil to query active connections and performs DNS reverse lookups.
"""

import logging
import socket
from typing import List, Dict, Optional
import psutil

logger = logging.getLogger(__name__)


class NetworkMapper:
    """Maps processes to their network connections."""

    def __init__(self, cache_dns: bool = True):
        """
        Initialize network mapper.

        Args:
            cache_dns: Whether to cache DNS lookup results
        """
        self.cache_dns = cache_dns
        self.dns_cache: Dict[str, str] = {}

    def reverse_dns_lookup(self, ip_address: str) -> Optional[str]:
        """
        Perform reverse DNS lookup on IP address.

        Args:
            ip_address: IP address to lookup

        Returns:
            Domain name if found, otherwise IP address or None.
        """
        if not ip_address or ip_address == "0.0.0.0":
            return None

        # Check cache
        if self.cache_dns and ip_address in self.dns_cache:
            return self.dns_cache[ip_address]

        try:
            # Perform reverse DNS lookup
            domain_name, _, _ = socket.gethostbyaddr(ip_address)

            # Cache result
            if self.cache_dns:
                self.dns_cache[ip_address] = domain_name

            logger.debug(f"Reverse DNS: {ip_address} → {domain_name}")
            return domain_name

        except (socket.herror, socket.gaierror, OSError) as e:
            # DNS lookup failed, return IP or None
            logger.debug(f"Reverse DNS failed for {ip_address}: {e}")
            if self.cache_dns:
                self.dns_cache[ip_address] = ip_address
            return ip_address

        except Exception as e:
            logger.error(f"Unexpected error in reverse DNS lookup: {e}")
            return None

    def get_process_connections(self, pid: int) -> List[Dict]:
        """
        Get all network connections initiated by a specific process.

        Args:
            pid: Process ID

        Returns:
            List of connection dictionaries with remote domain info.
        """
        try:
            process = psutil.Process(pid)
            connections = process.net_connections(kind="inet")

            result = []
            for conn in connections:
                connection_info = {
                    "pid": pid,
                    "local_ip": conn.laddr.ip if conn.laddr else None,
                    "local_port": conn.laddr.port if conn.laddr else None,
                    "remote_ip": conn.raddr.ip if conn.raddr else None,
                    "remote_port": conn.raddr.port if conn.raddr else None,
                    "remote_domain": None,
                    "connection_type": conn.type,
                    "status": conn.status,
                }

                # Perform DNS reverse lookup for remote IP
                if connection_info["remote_ip"]:
                    remote_domain = self.reverse_dns_lookup(
                        connection_info["remote_ip"]
                    )
                    connection_info["remote_domain"] = remote_domain

                result.append(connection_info)

            return result

        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.debug(f"Cannot get connections for PID {pid}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting process connections: {e}")
            return []

    def get_all_process_connections(self) -> Dict[int, List[Dict]]:
        """
        Get all network connections by all processes.

        Returns:
            Dictionary mapping PID to list of connections.
        """
        connections_by_pid = {}

        try:
            all_connections = psutil.net_connections(kind="inet")

            for conn in all_connections:
                pid = conn.pid
                if not pid:
                    continue

                if pid not in connections_by_pid:
                    connections_by_pid[pid] = []

                connection_info = {
                    "pid": pid,
                    "local_ip": conn.laddr.ip if conn.laddr else None,
                    "local_port": conn.laddr.port if conn.laddr else None,
                    "remote_ip": conn.raddr.ip if conn.raddr else None,
                    "remote_port": conn.raddr.port if conn.raddr else None,
                    "remote_domain": None,
                    "connection_type": conn.type,
                    "status": conn.status,
                }

                # Perform DNS reverse lookup
                if connection_info["remote_ip"]:
                    remote_domain = self.reverse_dns_lookup(
                        connection_info["remote_ip"]
                    )
                    connection_info["remote_domain"] = remote_domain

                connections_by_pid[pid].append(connection_info)

        except Exception as e:
            logger.error(f"Error getting all connections: {e}")

        return connections_by_pid

    def get_domains_for_process(self, pid: int) -> List[str]:
        """
        Get unique domain names associated with a process.

        Args:
            pid: Process ID

        Returns:
            List of unique domain names.
        """
        connections = self.get_process_connections(pid)
        domains = set()

        for conn in connections:
            if conn.get("remote_domain"):
                domains.add(conn["remote_domain"])

        return list(domains)

    def is_localhost_connection(self, remote_ip: Optional[str]) -> bool:
        """
        Check if connection is to localhost.

        Args:
            remote_ip: Remote IP address

        Returns:
            True if localhost, False otherwise.
        """
        if not remote_ip:
            return False

        localhost_patterns = ["127.0.0.1", "::1", "localhost"]
        return any(pattern in remote_ip for pattern in localhost_patterns)

    def clear_dns_cache(self) -> None:
        """Clear the DNS lookup cache."""
        self.dns_cache.clear()
        logger.info("DNS cache cleared")

    def get_dns_cache_stats(self) -> Dict:
        """
        Get statistics about DNS cache.

        Returns:
            Dictionary with cache statistics.
        """
        return {
            "cache_enabled": self.cache_dns,
            "cached_entries": len(self.dns_cache),
            "cache_size_bytes": sum(
                len(k) + len(v) for k, v in self.dns_cache.items()
            ),
        }
