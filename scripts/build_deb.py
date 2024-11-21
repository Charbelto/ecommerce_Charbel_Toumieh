from pathlib import Path
import os
import shutil
import subprocess
from typing import List, Dict

SERVICES = {
    'customer': '0.1.0',
    'inventory': '0.1.0',
    'sales': '0.1.0',
    'reviews': '0.1.0',
    'auth': '0.1.0'
}

def create_debian_structure(service_name: str, version: str, base_dir: Path) -> Path:
    """Create the basic debian package structure"""
    package_name = f"ecommerce-{service_name}-service"
    deb_root = base_dir / f"deb_{service_name}"
    
    # Create directory structure
    (deb_root / "DEBIAN").mkdir(parents=True)
    (deb_root / f"opt/ecommerce/{service_name}").mkdir(parents=True)
    
    # Create control file
    control_content = f"""Package: {package_name}
Version: {version}
Architecture: all
Maintainer: Your Name <your.email@example.com>
Description: E-commerce {service_name} microservice
 Part of the e-commerce microservices platform.
Depends: python3 (>= 3.9), python3-pip
Priority: optional
"""
    
    with open(deb_root / "DEBIAN/control", "w") as f:
        f.write(control_content)
    
    return deb_root

def copy_service_files(service_name: str, deb_root: Path):
    """Copy service files to the debian package structure"""
    service_dir = Path(f"services/{service_name}")
    dest_dir = deb_root / f"opt/ecommerce/{service_name}"
    
    # Copy service files
    if service_dir.exists():
        shutil.copytree(service_dir, dest_dir, dirs_exist_ok=True)
    
    # Copy shared utilities
    utils_dir = Path("utils")
    if utils_dir.exists():
        shutil.copytree(utils_dir, dest_dir / "utils", dirs_exist_ok=True)

def create_systemd_service(service_name: str, deb_root: Path):
    """Create systemd service file"""
    systemd_dir = deb_root / "etc/systemd/system"
    systemd_dir.mkdir(parents=True)
    
    service_content = f"""[Unit]
Description=E-commerce {service_name} service
After=network.target

[Service]
Type=simple
User=ecommerce
Group=ecommerce
WorkingDirectory=/opt/ecommerce/{service_name}
ExecStart=/usr/bin/python3 -m uvicorn {service_name}_service:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
"""
    
    with open(systemd_dir / f"ecommerce-{service_name}.service", "w") as f:
        f.write(service_content)

def build_deb_package(service_name: str, version: str, base_dir: Path):
    """Build the debian package for a service"""
    deb_root = create_debian_structure(service_name, version, base_dir)
    copy_service_files(service_name, deb_root)
    create_systemd_service(service_name, deb_root)
    
    # Build the package
    subprocess.run(["dpkg-deb", "--build", deb_root])
    
    # Cleanup
    shutil.rmtree(deb_root)

def main():
    base_dir = Path("build")
    base_dir.mkdir(exist_ok=True)
    
    for service, version in SERVICES.items():
        print(f"Building {service} service package...")
        try:
            build_deb_package(service, version, base_dir)
            print(f"Successfully built package for {service}")
        except Exception as e:
            print(f"Failed to build package for {service}: {str(e)}")

if __name__ == "__main__":
    main()