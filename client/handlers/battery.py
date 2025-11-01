"""
Battery status monitoring handler
Shows battery level, charging status, time remaining
"""

import psutil
import logging

logger = logging.getLogger(__name__)


class BatteryHandler:
                """Handle battery status monitoring"""

                def get_battery_status(self):
                    """Get detailed battery information"""
                    try:
                        battery = psutil.sensors_battery()

                        if battery is None:
                            return {
                                'status': 'success',
                                'message': '🔌 No battery detected (Desktop PC)',
                                'has_battery': False
                            }

                        # Calculate battery percentage (rounded to integer)
                        percent = int(round(battery.percent))

                        # Get charging status
                        plugged = battery.power_plugged
                        charging_status = '🔌 Charging' if plugged else '🔋 On Battery'

                        # Get time remaining
                        time_remaining = battery.secsleft

                        if time_remaining == psutil.POWER_TIME_UNLIMITED:
                            time_str = 'Unlimited (Plugged in)'
                        elif time_remaining == psutil.POWER_TIME_UNKNOWN:
                            time_str = 'Unknown'
                        else:
                            hours = time_remaining // 3600
                            minutes = (time_remaining % 3600) // 60
                            time_str = f'{hours}h {minutes}m remaining'

                        # Battery icon based on level
                        if percent >= 90:
                            icon = '🔋'
                        elif percent >= 60:
                            icon = '🔋'
                        elif percent >= 30:
                            icon = '🔋'
                        elif percent >= 15:
                            icon = '⚠️'
                        else:
                            icon = '❗'

                        return {
                            'status': 'success',
                            'message': f'{icon} Battery Status',
                            'has_battery': True,
                            'percent': percent,
                            'charging': plugged,
                            'charging_status': charging_status,
                            'time_remaining': time_str,
                            'details': f'{icon} {percent}% - {charging_status}\n⏱️ {time_str}'
                        }

                    except Exception as e:
                        logger.error(f"Battery status error: {e}")
                        return {
                            'status': 'error',
                            'message': f'Failed to get battery status: {str(e)}'
                        }

                def get_battery_alert(self):
                    """Check if battery needs charging"""
                    try:
                        battery = psutil.sensors_battery()

                        if battery is None:
                            return None

                        if not battery.power_plugged and battery.percent < 20:
                            return {
                                'status': 'warning',
                                'message': f'⚠️ Low Battery: {battery.percent}%\n\nPlease charge your device!'
                            }

                        return None

                    except Exception as e:
                        logger.error(f"Battery alert error: {e}")
                        return None