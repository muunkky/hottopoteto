"""
Secure credential management utilities.
"""
import os
import logging
from typing import Dict, List, Optional, Union, Any
from dotenv import load_dotenv
from pathlib import Path

logger = logging.getLogger(__name__)

# Registry of required credentials by domain
_required_credentials = {}

def load_all_env_files():
    """
    Load environment variables from all .env files in order:
    1. Domain-specific .env files
    2. Core .env file
    3. Root .env file (overrides others)
    """
    # Load domain-specific .env files
    domains_dir = Path("core/domains")
    if domains_dir.exists():
        for domain_dir in domains_dir.iterdir():
            if domain_dir.is_dir():
                domain = domain_dir.name
                env_path = domain_dir / f".env.{domain}"
                if env_path.exists():
                    logger.debug(f"Loading env file: {env_path}")
                    load_dotenv(env_path)
    
    # Load core .env
    core_env = Path("core/.env.core")
    if core_env.exists():
        logger.debug(f"Loading env file: {core_env}")
        load_dotenv(core_env)
    
    # Load root .env (overrides)
    root_env = Path(".env")
    if root_env.exists():
        logger.debug(f"Loading env file: {root_env}")
        load_dotenv(root_env, override=True)

# Load all env files
load_all_env_files()

def register_domain_credentials(domain: str, credentials: List[Dict[str, Any]]) -> None:
    """
    Register required credentials for a domain.
    
    Args:
        domain: Domain name
        credentials: List of credential specifications with fields:
            - name: Environment variable name
            - description: Human-readable description
            - required: Whether this credential is required (default: True)
    """
    _required_credentials[domain] = credentials
    logger.debug(f"Registered credential requirements for domain: {domain}")

def get_credential(name: str, required: bool = True) -> Optional[str]:
    """
    Get a credential from environment variables.
    
    Args:
        name: Environment variable name
        required: Whether to raise an error if missing
        
    Returns:
        The credential value or None if not required and missing
        
    Raises:
        ValueError: If the credential is required but missing
    """
    value = os.getenv(name)
    
    if value is None and required:
        # Create a helpful error message
        domain_info = ""
        for domain, creds in _required_credentials.items():
            for cred in creds:
                if cred["name"] == name:
                    domain_info = f" for {domain} domain"
                    break
                    
        error_message = (
            f"Missing required environment variable {name}{domain_info}\n"
            f"Please set this variable in your .env file or environment"
        )
        
        logger.error(error_message)
        raise ValueError(error_message)
        
    return value

def check_domain_credentials(domain: str) -> Dict[str, bool]:
    """
    Check if all required credentials are available for a domain.
    
    Args:
        domain: Domain name
        
    Returns:
        Dictionary mapping credential names to availability
    """
    if domain not in _required_credentials:
        logger.warning(f"No credential requirements registered for domain: {domain}")
        return {}
        
    result = {}
    for cred in _required_credentials[domain]:
        name = cred["name"]
        required = cred.get("required", True)
        value = os.getenv(name)
        result[name] = value is not None
        
        if value is None and required:
            logger.warning(f"Missing required credential: {name}")
    
    return result

def check_all_credentials() -> Dict[str, Dict[str, bool]]:
    """
    Check all registered credentials.
    
    Returns:
        Dictionary mapping domains to credential status
    """
    result = {}
    for domain in _required_credentials:
        result[domain] = check_domain_credentials(domain)
    return result

def get_required_credentials(domain: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get required credentials for a domain or all domains.
    
    Args:
        domain: Optional domain name to filter by
        
    Returns:
        Dictionary of domain name to list of credential specifications
    """
    if domain:
        return {domain: _required_credentials.get(domain, [])} if domain in _required_credentials else {}
    return _required_credentials
