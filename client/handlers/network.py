"""
Network information handler
Shows IP addresses, WiFi info, network stats
"""

import psutil
import socket
import logging
import subprocess
import platform

try:
    import netifaces

    HAS_NETIFACES = True
except ImportError:
    HAS_NETIFACES = False

logger = logging.getLogger(__name__)


class NetworkHandler:
    """Handle network information"""

    def __init__(self):
        self.os_name = platform.system()

    def get_network_info(self):
        """Get comprehensive network information"""
        try:
            info = {
                'status': 'success',
                'message': '🌐 Network Information',
                'hostname': socket.gethostname(),
                'interfaces': self._get_interfaces(),
                'wifi': self._get_wifi_info(),
                'public_ip': self._get_public_ip()
            }

            # Format details
            details = f"🖥️ Hostname: {info['hostname']}\n\n"

            # Interfaces
            if info['interfaces']:
                details += "📡 Network Interfaces:\n"
                for iface in info['interfaces']:
                    details += f"  • {iface['name']}: {iface['ip']}\n"
                details += "\n"

            # WiFi info
            if info['wifi']:
                details += f"📶 WiFi:\n"
                details += f"  • SSID: {info['wifi'].get('ssid', 'N/A')}\n"
                details += f"  • Signal: {info['wifi'].get('signal', 'N/A')}\n\n"

            # Public IP
            if info['public_ip']:
                details += f"🌍 Public IP: {info['public_ip']}\n"

            info['details'] = details

            return info

        except Exception as e:
            logger.error(f"Network info error: {e}")
            return {
                'status': 'error',
                'message': f'Failed to get network info: {str(e)}'
            }

    def _get_interfaces(self):
        """Get network interfaces and their IPs"""
        interfaces = []

        try:
            if HAS_NETIFACES:
                # Using netifaces (more reliable)
                for iface in netifaces.interfaces():
                    addrs = netifaces.ifaddresses(iface)
                    if netifaces.AF_INET in addrs:
                        for addr in addrs[netifaces.AF_INET]:
                            ip = addr['addr']
                            if ip != '127.0.0.1':
                                interfaces.append({
                                    'name': iface,
                                    'ip': ip
                                })
            else:
                # Fallback to psutil
                stats = psutil.net_if_addrs()
                for iface, addrs in stats.items():
                    for addr in addrs:
                        if addr.family == socket.AF_INET and addr.address != '127.0.0.1':
                            interfaces.append({
                                'name': iface,
                                'ip': addr.address
                            })

        except Exception as e:
            logger.error(f"Interface enumeration error: {e}")

        return interfaces

    def _get_wifi_info(self):
        """Get WiFi connection info"""
        try:
            if self.os_name == 'Linux':
                # Try nmcli (NetworkManager)
                try:
                    result = subprocess.run(
                        ['nmcli', '-t', '-f', 'active,ssid,signal', 'dev', 'wifi'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )

                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if line.startswith('yes:'):
                            parts = line.split(':')
                            if len(parts) >= 3:
                                return {
                                    'ssid': parts[1],
                                    'signal': f"{parts[2]}%"
                                }
                except FileNotFoundError:
                    pass

                # Try iwconfig
                try:
                    result = subprocess.run(
                        ['iwconfig'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )

                    for line in result.stdout.split('\n'):
                        if 'ESSID' in line:
                            ssid = line.split('ESSID:"')[1].split('"')[0]
                            return {'ssid': ssid}
                except:
                    pass

            elif self.os_name == 'Windows':
                # Windows: netsh
                try:
                    result = subprocess.run(
                        ['netsh', 'wlan', 'show', 'interfaces'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )

                    ssid = None
                    signal = None

                    for line in result.stdout.split('\n'):
                        if 'SSID' in line and 'BSSID' not in line:
                            ssid = line.split(':')[1].strip()
                        elif 'Signal' in line:
                            signal = line.split(':')[1].strip()

                    if ssid:
                        return {'ssid': ssid, 'signal': signal or 'N/A'}
                except:
                    pass

            elif self.os_name == 'Darwin':
                # macOS
                try:
                    result = subprocess.run(
                        ['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport',
                         '-I'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )

                    ssid = None
                    for line in result.stdout.split('\n'):
                        if 'SSID:' in line:
                            ssid = line.split(':')[1].strip()
                            break

                    if ssid:
                        return {'ssid': ssid}
                except:
                    pass

        except Exception as e:
            logger.error(f"WiFi info error: {e}")

        return None

    def _get_public_ip(self):
        """Get public IP address"""
        try:
            import requests
            response = requests.get('https://api.ipify.org', timeout=5)
            return response.text
        except:
            return None

    def get_network_stats(self):
        """Get network usage statistics"""
        try:
            stats = psutil.net_io_counters()

            # Convert bytes to human readable
            def bytes_to_human(n):
                symbols = ('KB', 'MB', 'GB', 'TB')
                prefix = {}
                for i, s in enumerate(symbols):
                    prefix[s] = 1 << (i + 1) * 10
                for symbol in reversed(symbols):
                    if n >= prefix[symbol]:
                        value = float(n) / prefix[symbol]
                        return f'{value:.2f} {symbol}'
                return f'{n} B'

            return {
                'status': 'success',
                'message': '📊 Network Statistics',
                'sent': bytes_to_human(stats.bytes_sent),
                'received': bytes_to_human(stats.bytes_recv),
                'packets_sent': stats.packets_sent,
                'packets_recv': stats.packets_recv,
                'details': (
                    f"📤 Sent: {bytes_to_human(stats.bytes_sent)}\n"
                    f"📥 Received: {bytes_to_human(stats.bytes_recv)}\n"
                    f"📦 Packets Sent: {stats.packets_sent:,}\n"
                    f"📦 Packets Recv: {stats.packets_recv:,}"
                )
            }

        except Exception as e:
            logger.error(f"Network stats error: {e}")
            return {
                'status': 'error',
                'message': f'Failed to get network stats: {str(e)}'
            }