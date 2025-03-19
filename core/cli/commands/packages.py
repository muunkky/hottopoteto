"""
CLI commands for managing packages
"""
import os
import sys
import subprocess
import click
import logging
from core.registry import PackageRegistry

logger = logging.getLogger(__name__)

def list_packages():
    """List all installed packages"""
    packages = PackageRegistry.list_packages()
    
    if not packages:
        click.echo("No packages installed")
        return
    
    core_packages = []
    extension_packages = []
    
    for package in packages:
        pkg_type = PackageRegistry.get_package_type(package)
        if pkg_type == 'core':
            core_packages.append(package)
        else:
            extension_packages.append(package)
    
    if core_packages:
        click.echo(f"Core Package:")
        for package in sorted(core_packages):
            version = getattr(PackageRegistry.get_package(package).get('module'), '__version__', '0.1.0')
            click.echo(f"  - {package} (v{version})")
    
    if extension_packages:        
        click.echo(f"Installed Extension Packages ({len(extension_packages)}):")
        for package in sorted(extension_packages):
            version = getattr(PackageRegistry.get_package(package).get('module'), '__version__', '0.1.0')
            click.echo(f"  - {package} (v{version})")

def install_package(package_name, dev=False):
    """Install a package"""
    cmd = [sys.executable, "-m", "pip", "install"]
    
    if dev:
        cmd.append("-e")
        
    # Handle GitHub URLs, PyPI packages and local paths
    if package_name.startswith(("git+", "http://", "https://")):
        cmd.append(package_name)
    elif os.path.exists(package_name):
        cmd.append(os.path.abspath(package_name))
    else:
        # Try to add hottopoteto- prefix if not provided
        if not package_name.startswith("hottopoteto-"):
            full_name = f"hottopoteto-{package_name}"
        else:
            full_name = package_name
        cmd.append(full_name)
    
    click.echo(f"Installing {package_name}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        click.echo(f"Successfully installed {package_name}")
        click.echo("Restart the application to load the new package")
    else:
        click.echo(f"Failed to install {package_name}: {result.stderr}")

def uninstall_package(package_name):
    """Uninstall a package"""
    # Add hottopoteto- prefix if not provided
    if not package_name.startswith("hottopoteto-"):
        full_name = f"hottopoteto-{package_name}"
    else:
        full_name = package_name
        
    cmd = [sys.executable, "-m", "pip", "uninstall", "-y", full_name]
    
    click.echo(f"Uninstalling {full_name}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        click.echo(f"Successfully uninstalled {package_name}")
        click.echo("Restart the application for changes to take effect")
    else:
        click.echo(f"Failed to uninstall {package_name}: {result.stderr}")

def create_package(name, domain=None, plugin=None):
    """Create a new package template"""
    try:
        from core.package_template import create_package_template
        
        # Format package name
        if not name.startswith("hottopoteto-"):
            package_name = f"hottopoteto-{name}"
        else:
            package_name = name
            
        # Extract module name (without hottopoteto- prefix)
        if package_name.startswith("hottopoteto-"):
            module_name = package_name[len("hottopoteto-"):]
        else:
            module_name = package_name
            
        options = {
            "domain": domain,
            "plugin": plugin
        }
        
        click.echo(f"Creating package template for '{package_name}'...")
        path = create_package_template(package_name, module_name, options)
        click.echo(f"✓ Created package template at: {path}")
        click.echo(f"\nNext steps:")
        click.echo(f"1. cd {package_name}")
        click.echo(f"2. pip install -e .")
        click.echo(f"3. Start customizing your package")
    except Exception as e:
        click.echo(f"Failed to create package: {e}")

# For click-based CLI - leave these for compatibility
@click.group(name="packages")
def packages_group():
    """Package management commands"""
    pass

@packages_group.command(name="list")
def list_cmd():
    list_packages()

@packages_group.command(name="install")
@click.argument("package_name")
@click.option("--dev", is_flag=True, help="Install in development mode")
def install_cmd(package_name, dev):
    install_package(package_name, dev)

@packages_group.command(name="uninstall")
@click.argument("package_name")
def uninstall_cmd(package_name):
    uninstall_package(package_name)

@packages_group.command(name="create")
@click.argument("name")
@click.option("--domain", help="Include domain template")
@click.option("--plugin", help="Include plugin template")
def create_cmd(name, domain, plugin):
    create_package(name, domain, plugin)
