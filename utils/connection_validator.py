"""
Connection validation utilities for VPVET backend.
Provides tools to validate backend connectivity and health.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
import requests
from flask import current_app

logger = logging.getLogger(__name__)

class ConnectionValidator:
    """Validates backend connections and provides health monitoring."""

    @staticmethod
    def validate_backend_connection(base_url: str, timeout: int = 5) -> Dict[str, any]:
        """
        Validate backend connectivity by checking the health endpoint.

        Args:
            base_url: Base URL of the backend API
            timeout: Request timeout in seconds

        Returns:
            Dict containing connection validation results
        """
        start_time = datetime.utcnow()
        health_url = f"{base_url.rstrip('/')}/health"

        try:
            logger.info(f"Validating backend connection to: {health_url}")

            response = requests.get(
                health_url,
                timeout=timeout,
                headers={
                    'Accept': 'application/json',
                    'User-Agent': 'VPVET-ConnectionValidator/1.0'
                }
            )

            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            if response.status_code == 200:
                data = response.json()
                return {
                    'is_connected': True,
                    'response_time_ms': round(response_time, 2),
                    'status': data.get('status', 'unknown'),
                    'environment': data.get('environment', 'unknown'),
                    'timestamp': datetime.utcnow().isoformat(),
                    'api_info': {
                        'api_base_url': data.get('api_base_url'),
                        'allowed_origins': data.get('allowed_origins'),
                        'mock_responses_enabled': data.get('mock_responses_enabled'),
                        'version': data.get('version')
                    }
                }
            else:
                return {
                    'is_connected': False,
                    'error': f"HTTP {response.status_code}",
                    'response_time_ms': round(response_time, 2),
                    'timestamp': datetime.utcnow().isoformat()
                }

        except requests.exceptions.Timeout:
            return {
                'is_connected': False,
                'error': 'Connection timeout',
                'timeout_seconds': timeout,
                'timestamp': datetime.utcnow().isoformat()
            }

        except requests.exceptions.ConnectionError:
            return {
                'is_connected': False,
                'error': 'Connection refused',
                'timestamp': datetime.utcnow().isoformat()
            }

        except requests.exceptions.RequestException as e:
            return {
                'is_connected': False,
                'error': f'Request error: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Unexpected error during connection validation: {str(e)}")
            return {
                'is_connected': False,
                'error': f'Unexpected error: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }

    @staticmethod
    def validate_environment_switch(current_url: str, target_url: str) -> Dict[str, any]:
        """
        Validate that switching to a target environment is safe.

        Args:
            current_url: Current backend URL
            target_url: Target backend URL to switch to

        Returns:
            Dict containing environment switch validation results
        """
        logger.info(f"Validating environment switch from {current_url} to {target_url}")

        # Validate both endpoints
        current_validation = ConnectionValidator.validate_backend_connection(current_url)
        target_validation = ConnectionValidator.validate_backend_connection(target_url)

        # Safety checks
        safety_issues = []

        # Check if target is responding
        if not target_validation['is_connected']:
            safety_issues.append("Target backend is not responding")

        # Check for localhost in production-like URLs
        if 'localhost' in target_url and target_validation.get('environment') == 'production':
            safety_issues.append("Localhost URL detected with production environment")

        # Check for HTTP vs HTTPS mismatch
        if target_url.startswith('https://') and current_validation.get('environment') == 'development':
            logger.warning("Switching from development to HTTPS URL")

        return {
            'is_safe': len(safety_issues) == 0,
            'safety_issues': safety_issues,
            'current_backend': current_validation,
            'target_backend': target_validation,
            'recommendation': 'safe_to_switch' if len(safety_issues) == 0 else 'do_not_switch',
            'timestamp': datetime.utcnow().isoformat()
        }

    @staticmethod
    def get_connection_metrics(base_url: str) -> Dict[str, any]:
        """
        Get detailed connection metrics for monitoring.

        Args:
            base_url: Base URL of the backend API

        Returns:
            Dict containing connection metrics
        """
        # Perform multiple health checks to get average response time
        response_times = []
        successful_checks = 0
        total_checks = 3

        for i in range(total_checks):
            result = ConnectionValidator.validate_backend_connection(base_url, timeout=3)
            if result['is_connected']:
                response_times.append(result['response_time_ms'])
                successful_checks += 1

        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        success_rate = (successful_checks / total_checks) * 100

        return {
            'avg_response_time_ms': round(avg_response_time, 2),
            'success_rate_percent': round(success_rate, 2),
            'total_checks': total_checks,
            'successful_checks': successful_checks,
            'min_response_time_ms': min(response_times) if response_times else 0,
            'max_response_time_ms': max(response_times) if response_times else 0,
            'timestamp': datetime.utcnow().isoformat()
        }

class ConnectionMonitor:
    """Monitors backend connection health over time."""

    def __init__(self):
        self.connection_history = []
        self.max_history_size = 100

    def record_connection_attempt(self, url: str, result: Dict[str, any]):
        """
        Record a connection attempt in the history.

        Args:
            url: Backend URL that was tested
            result: Connection validation result
        """
        record = {
            'url': url,
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        }

        self.connection_history.append(record)

        # Maintain history size
        if len(self.connection_history) > self.max_history_size:
            self.connection_history.pop(0)

        logger.info(f"Recorded connection attempt for {url}: {result['is_connected']}")

    def get_connection_stats(self, hours: int = 24) -> Dict[str, any]:
        """
        Get connection statistics for the specified time period.

        Args:
            hours: Number of hours to look back in history

        Returns:
            Dict containing connection statistics
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_connections = [
            record for record in self.connection_history
            if datetime.fromisoformat(record['timestamp']) > cutoff_time
        ]

        if not recent_connections:
            return {
                'total_attempts': 0,
                'successful_connections': 0,
                'success_rate': 0,
                'avg_response_time': 0,
                'period_hours': hours
            }

        successful_attempts = sum(1 for record in recent_connections if record['result']['is_connected'])
        response_times = [
            record['result'].get('response_time_ms', 0)
            for record in recent_connections
            if record['result'].get('response_time_ms')
        ]

        return {
            'total_attempts': len(recent_connections),
            'successful_connections': successful_attempts,
            'success_rate': round((successful_attempts / len(recent_connections)) * 100, 2),
            'avg_response_time': round(sum(response_times) / len(response_times), 2) if response_times else 0,
            'period_hours': hours,
            'last_attempt': recent_connections[-1]['timestamp'] if recent_connections else None
        }

# Global connection monitor instance
connection_monitor = ConnectionMonitor()