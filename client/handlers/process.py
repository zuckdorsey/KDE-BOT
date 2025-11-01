"""
Process manager handler
List, filter, and kill processes
"""

import psutil
import logging

logger = logging.getLogger(__name__)


class ProcessHandler:
    """Handle process management"""

    def list_processes(self, limit=10, sort_by='cpu'):
        """List top processes sorted by CPU or memory"""
        try:
            processes = []

            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    info = proc.info
                    processes.append({
                        'pid': info['pid'],
                        'name': info['name'],
                        'cpu': info['cpu_percent'] or 0,
                        'memory': info['memory_percent'] or 0
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # Sort processes
            if sort_by == 'cpu':
                processes.sort(key=lambda x: x['cpu'], reverse=True)
            elif sort_by == 'memory':
                processes.sort(key=lambda x: x['memory'], reverse=True)

            # Get top processes
            top_processes = processes[:limit]

            # Format details
            details = f"🔝 Top {limit} Processes (by {sort_by.upper()}):\n\n"

            for i, proc in enumerate(top_processes, 1):
                details += (
                    f"{i}. {proc['name']}\n"
                    f"   PID: {proc['pid']} | "
                    f"CPU: {proc['cpu']:.1f}% | "
                    f"RAM: {proc['memory']:.1f}%\n\n"
                )

            return {
                'status': 'success',
                'message': '💻 Process List',
                'processes': top_processes,
                'total': len(processes),
                'details': details
            }

        except Exception as e:
            logger.error(f"List processes error: {e}")
            return {
                'status': 'error',
                'message': f'Failed to list processes: {str(e)}'
            }

    def search_process(self, name):
        """Search for process by name"""
        try:
            matches = []

            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if name.lower() in proc.info['name'].lower():
                        matches.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cpu': proc.info['cpu_percent'] or 0,
                            'memory': proc.info['memory_percent'] or 0
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            if not matches:
                return {
                    'status': 'success',
                    'message': f'🔍 No processes found matching: {name}',
                    'processes': []
                }

            # Format details
            details = f"🔍 Found {len(matches)} process(es) matching '{name}':\n\n"

            for proc in matches:
                details += (
                    f"• {proc['name']}\n"
                    f"  PID: {proc['pid']} | "
                    f"CPU: {proc['cpu']:.1f}% | "
                    f"RAM: {proc['memory']:.1f}%\n\n"
                )

            return {
                'status': 'success',
                'message': f'🔍 Search Results for: {name}',
                'processes': matches,
                'count': len(matches),
                'details': details
            }

        except Exception as e:
            logger.error(f"Search process error: {e}")
            return {
                'status': 'error',
                'message': f'Failed to search processes: {str(e)}'
            }

    def kill_process(self, pid):
        """Kill process by PID"""
        try:
            process = psutil.Process(pid)
            name = process.name()

            # Kill process
            process.terminate()

            # Wait for process to terminate (max 5 seconds)
            try:
                process.wait(timeout=5)
            except psutil.TimeoutExpired:
                # Force kill if not terminated
                process.kill()

            logger.info(f"Process killed: {name} (PID: {pid})")

            return {
                'status': 'success',
                'message': f'✅ Process killed: {name} (PID: {pid})'
            }

        except psutil.NoSuchProcess:
            return {
                'status': 'error',
                'message': f'❌ Process not found (PID: {pid})'
            }
        except psutil.AccessDenied:
            return {
                'status': 'error',
                'message': f'❌ Access denied to kill process (PID: {pid})'
            }
        except Exception as e:
            logger.error(f"Kill process error: {e}")
            return {
                'status': 'error',
                'message': f'Failed to kill process: {str(e)}'
            }

    def get_process_info(self, pid):
        """Get detailed info about a specific process"""
        try:
            process = psutil.Process(pid)

            with process.oneshot():
                info = {
                    'pid': process.pid,
                    'name': process.name(),
                    'status': process.status(),
                    'cpu_percent': process.cpu_percent(),
                    'memory_percent': process.memory_percent(),
                    'memory_mb': process.memory_info().rss / 1024 / 1024,
                    'num_threads': process.num_threads(),
                    'create_time': process.create_time()
                }

            # Format details
            details = (
                f"💻 Process Information\n\n"
                f"📋 Name: {info['name']}\n"
                f"🆔 PID: {info['pid']}\n"
                f"📊 Status: {info['status']}\n"
                f"🔥 CPU: {info['cpu_percent']:.1f}%\n"
                f"💾 Memory: {info['memory_percent']:.1f}% ({info['memory_mb']:.1f} MB)\n"
                f"🧵 Threads: {info['num_threads']}\n"
            )

            return {
                'status': 'success',
                'message': f'💻 Process Info: {info["name"]}',
                'process': info,
                'details': details
            }

        except psutil.NoSuchProcess:
            return {
                'status': 'error',
                'message': f'❌ Process not found (PID: {pid})'
            }
        except Exception as e:
            logger.error(f"Get process info error: {e}")
            return {
                'status': 'error',
                'message': f'Failed to get process info: {str(e)}'
            }