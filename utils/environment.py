"""
Environment detection and configuration management for VPVET backend.
Provides automatic environment detection with production safety features.
"""

import os
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

def get_environment_config() -> Dict[str, any]:
    """
    Detect the current environment and return appropriate configuration.

    Returns:
        Dict containing environment-specific configuration
    """
    # Detect environment based on multiple indicators
    flask_env = os.getenv('FLASK_ENV', 'development')
    database_url = os.getenv('DATABASE_URL', '')
    railway_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN', '')

    # Determine if we're in development or production
    is_development = (
        flask_env == 'development' or
        'localhost' in database_url or
        '127.0.0.1' in database_url or
        not railway_domain
    )

    is_production = not is_development

    environment = 'development' if is_development else 'production'

    # Configure allowed origins based on environment
    if is_development:
        allowed_origins = [
            'http://localhost:3000',
            'http://localhost:3001',
            'http://localhost:3002',
            'http://localhost:3003',
            'http://127.0.0.1:3000',
            'http://127.0.0.1:3001',
            'http://127.0.0.1:3002',
            'http://127.0.0.1:3003'
        ]
        api_base_url = 'http://localhost:5000/api'
        log_level = 'DEBUG'
        enable_mock_responses = True
    else:
        # Production - use Railway domain and specific frontend URL
        frontend_url = os.getenv('FRONTEND_URL', 'https://your-runaway-domain.com')
        allowed_origins = [frontend_url]

        # Construct API base URL from Railway domain
        if railway_domain:
            api_base_url = f'https://{railway_domain}/api'
        else:
            # Fallback for production
            api_base_url = os.getenv('API_BASE_URL', 'https://api.vpvet.app/api')

        log_level = 'INFO'
        enable_mock_responses = False

    config = {
        'environment': environment,
        'is_development': is_development,
        'is_production': is_production,
        'allowed_origins': allowed_origins,
        'api_base_url': api_base_url,
        'database_url': database_url,
        'log_level': log_level,
        'enable_mock_responses': enable_mock_responses,
        'railway_domain': railway_domain,
        'frontend_url': os.getenv('FRONTEND_URL', 'http://localhost:3000')
    }

    # Log environment detection for debugging
    logger.info(f"Environment detected: {environment}")
    logger.info(f"Allowed origins: {allowed_origins}")
    logger.info(f"API base URL: {api_base_url}")
    logger.info(f"Mock responses enabled: {enable_mock_responses}")

    return config

def validate_environment_config(config: Dict[str, any]) -> bool:
    """
    Validate the environment configuration for safety.

    Args:
        config: Environment configuration dictionary

    Returns:
        True if configuration is valid and safe
    """
    # Check required fields
    required_fields = ['environment', 'allowed_origins', 'api_base_url']
    for field in required_fields:
        if field not in config:
            logger.error(f"Missing required field in environment config: {field}")
            return False

    # Validate environment type
    if config['environment'] not in ['development', 'production']:
        logger.error(f"Invalid environment: {config['environment']}")
        return False

    # Validate origins format
    if not isinstance(config['allowed_origins'], list) or len(config['allowed_origins']) == 0:
        logger.error("Invalid allowed_origins configuration")
        return False

    # Production safety checks
    if config['is_production']:
        # Ensure no localhost origins in production
        for origin in config['allowed_origins']:
            if 'localhost' in origin or '127.0.0.1' in origin:
                logger.error(f"Localhost origin detected in production config: {origin}")
                return False

        # Ensure HTTPS in production
        if not config['api_base_url'].startswith('https://'):
            logger.error(f"HTTP URL detected in production config: {config['api_base_url']}")
            return False

    logger.info("Environment configuration validation passed")
    return True

def get_cors_origins() -> List[str]:
    """
    Get CORS origins based on current environment configuration.

    Returns:
        List of allowed CORS origins
    """
    config = get_environment_config()
    return config['allowed_origins']

def is_development_environment() -> bool:
    """
    Check if the current environment is development.

    Returns:
        True if running in development environment
    """
    config = get_environment_config()
    return config['is_development']

def is_production_environment() -> bool:
    """
    Check if the current environment is production.

    Returns:
        True if running in production environment
    """
    config = get_environment_config()
    return config['is_production']