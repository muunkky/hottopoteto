"""
CLI commands for credential management.
"""
import argparse
import logging
import os
import getpass
from pathlib import Path
from typing import List, Dict, Any, Optional
from core.security.credentials import check_all_credentials, check_domain_credentials, get_required_credentials

logger = logging.getLogger(__name__)

def add_credentials_command(subparsers):
    """Add credentials command to the CLI."""
    parser = subparsers.add_parser("credentials", help="Manage API keys and other credentials")
    sub = parser.add_subparsers(dest="credentials_command", required=True)
    
    # Check credentials command
    check_parser = sub.add_parser("check", help="Check if required credentials are set")
    check_parser.add_argument("--domain", help="Check credentials for a specific domain")
    
    # List required credentials
    list_parser = sub.add_parser("list", help="List required credentials")
    list_parser.add_argument("--domain", help="List credentials for a specific domain")
    
    # Set credentials interactively
    setup_parser = sub.add_parser("setup", help="Set up credentials interactively")
    setup_parser.add_argument("--domain", help="Set up credentials for a specific domain")
    setup_parser.add_argument("--global", action="store_true", dest="global_env", 
                              help="Store credentials in root .env instead of domain-specific file")
    
    # Update a specific credential
    update_parser = sub.add_parser("update", help="Update a specific credential")
    update_parser.add_argument("name", help="Name of the credential to update")
    update_parser.add_argument("--global", action="store_true", dest="global_env", 
                              help="Update in root .env instead of domain-specific file")

def handle_credentials_command(args):
    """Handle credentials command."""
    if args.credentials_command == "check":
        if args.domain:
            status = check_domain_credentials(args.domain)
            _print_credential_status(status, args.domain)
        else:
            all_status = check_all_credentials()
            for domain, status in all_status.items():
                _print_credential_status(status, domain)
    
    elif args.credentials_command == "list":
        # Get all required credentials
        required_creds = get_required_credentials(args.domain)
        
        if args.domain:
            _print_credential_requirements(required_creds.get(args.domain, []), args.domain)
        else:
            for domain, creds in required_creds.items():
                _print_credential_requirements(creds, domain)
    
    elif args.credentials_command == "setup":
        _setup_credentials_interactive(args.domain, args.global_env)
        
    elif args.credentials_command == "update":
        _update_credential(args.name, args.global_env)

def _get_env_path(domain: Optional[str], global_env: bool = False) -> Path:
    """Get the appropriate .env file path based on domain and global flag."""
    if global_env:
        return Path(".env")
        
    if domain:
        # Domain-specific .env file
        domain_path = Path(f"core/domains/{domain}/.env.{domain}")
        if domain_path.exists() or not Path(".env").exists():
            return domain_path
    
    # Default to root .env
    return Path(".env")

def _read_env_file(path: Path) -> Dict[str, str]:
    """Read an .env file into a dictionary."""
    env_vars = {}
    if path.exists():
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip()
    return env_vars

def _write_env_file(path: Path, env_vars: Dict[str, str]) -> None:
    """Write dictionary of env vars to an .env file, preserving comments."""
    # Read existing file to preserve comments
    existing_lines = []
    if path.exists():
        with open(path, "r") as f:
            existing_lines = f.readlines()
    
    # Track which vars we've updated
    updated_keys = set()
    
    # Update existing lines or add them at the end
    new_lines = []
    for line in existing_lines:
        if line.strip() and not line.strip().startswith("#") and "=" in line:
            key = line.split("=", 1)[0].strip()
            if key in env_vars:
                new_lines.append(f"{key}={env_vars[key]}\n")
                updated_keys.add(key)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    # Add any new variables that weren't in the original file
    for key, value in env_vars.items():
        if key not in updated_keys:
            new_lines.append(f"{key}={value}\n")
    
    # Ensure directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write the updated file
    with open(path, "w") as f:
        f.writelines(new_lines)

def _setup_credentials_interactive(domain: Optional[str], global_env: bool) -> None:
    """Set up credentials interactively."""
    # Get all required credentials
    required_creds = get_required_credentials(domain)
    
    if domain and domain not in required_creds:
        print(f"No registered credentials for domain: {domain}")
        return
    
    # Determine which domains to process
    domains_to_process = [domain] if domain else required_creds.keys()
    
    print("Setting up credentials. Leave blank to skip a credential.")
    for d in domains_to_process:
        print(f"\n=== {d.upper()} Domain Credentials ===")
        env_path = _get_env_path(d, global_env)
        existing_env = _read_env_file(env_path)
        updated_env = existing_env.copy()
        
        for cred in required_creds.get(d, []):
            name = cred["name"]
            current = existing_env.get(name, os.getenv(name, ""))
            masked = "*" * len(current) if current else "(not set)"
            
            print(f"\n{name}: {cred['description']}")
            print(f"Current value: {masked}")
            
            if cred.get("required", True):
                prompt = f"Enter new value for {name} (leave blank to keep current): "
            else:
                prompt = f"Enter new value for {name} (optional, leave blank to skip): "
                
            # Use getpass for sensitive values
            new_value = getpass.getpass(prompt)
            
            if new_value:
                # User provided a new value
                updated_env[name] = new_value
                print(f"Updated {name}")
            elif not current and cred.get("required", True):
                # No current value and required
                print(f"Warning: {name} is required but not set.")
            
        # Save updated env vars
        _write_env_file(env_path, updated_env)
        print(f"\nCredentials saved to {env_path}")

def _update_credential(name: str, global_env: bool) -> None:
    """Update a specific credential value."""
    # Find which domain this credential belongs to
    from core.security.credentials import _required_credentials
    
    domain = None
    for d, creds in _required_credentials.items():
        if any(cred["name"] == name for cred in creds):
            domain = d
            break
    
    if not domain:
        print(f"Unknown credential: {name}")
        return
        
    env_path = _get_env_path(domain, global_env)
    existing_env = _read_env_file(env_path)
    
    current = existing_env.get(name, os.getenv(name, ""))
    masked = "*" * len(current) if current else "(not set)"
    
    print(f"\nUpdating {name} for domain {domain}")
    print(f"Current value: {masked}")
    
    new_value = getpass.getpass(f"Enter new value for {name}: ")
    
    if new_value:
        existing_env[name] = new_value
        _write_env_file(env_path, existing_env)
        print(f"Updated {name} in {env_path}")
    else:
        print("No value provided, keeping current value.")

def _print_credential_status(status: Dict[str, bool], domain: str):
    """Print credential status in a readable format."""
    print(f"\n=== {domain} Domain Credentials ===")
    
    if not status:
        print("No credentials required")
        return
        
    for name, exists in status.items():
        if exists:
            print(f"✅ {name}: Set")
        else:
            print(f"❌ {name}: Missing")

def _print_credential_requirements(creds: List[Dict[str, Any]], domain: str):
    """Print credential requirements in a readable format."""
    print(f"\n=== {domain} Domain Required Credentials ===")
    
    if not creds:
        print("No credentials required")
        return
        
    for cred in creds:
        req_str = "Required" if cred.get("required", True) else "Optional"
        print(f"{cred['name']}: {cred['description']} ({req_str})")
        
        # Check if set
        if os.getenv(cred['name']):
            print(f"  ✅ Currently set\n")
        else:
            print(f"  ❌ Not currently set\n")
