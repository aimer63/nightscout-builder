#!/usr/bin/env python3
"""
CGM-Remote-Monitor Release Build Script

This script builds Docker deployment artifacts for CGM-Remote-Monitor (Nightscout)
without modifying any upstream source code. It creates a self-contained zip file
containing the Docker image and configuration files.

Features:
- Builds Docker image from official Dockerfile
- Exports image as tarball for offline deployment
- Packages docker-compose.yml and environment templates
- Creates versioned zip file in released/

-------------------------------------------------------------------------------
Build Process:

1. Verify clean git state and extract version from tag
2. Build Docker image using official Dockerfile
3. Export image as cgm-remote-monitor.tar
4. Copy configuration templates
5. Create versioned zip archive in released/

-------------------------------------------------------------------------------
Usage:

# Build from current checkout (must be on a version tag)
python3 build.py

# The script will create:
# released/cgm-remote-monitor-v15.0.7.zip

-------------------------------------------------------------------------------
Release Workflow:

1. In cgm-remote-monitor repo, sync with upstream:
   cd ~/devel/cgm-remote-monitor
   git fetch upstream --tags

2. Checkout desired version:
   git checkout tags/15.0.7

3. Build release from nightscout-builder:
   cd ~/devel/nightscout-builder
   python3 build.py

4. The zip file in released/ is ready to deploy

IMPORTANT:
- Must be on a clean git checkout at a version tag in cgm-remote-monitor
- Docker must be running and have sufficient disk space
- The resulting zip can be deployed without this repository
"""

import argparse
import subprocess
import shutil
import sys
from pathlib import Path
import re
import zipfile

# Directory structure
BUILDER_DIR = Path(__file__).parent.resolve()
REPO_ROOT = Path.home() / "devel" / "cgm-remote-monitor"
RELEASED_DIR = BUILDER_DIR / "released"
BUILD_DIR = BUILDER_DIR / "build"

# Source files
SRC_DOCKERFILE = REPO_ROOT / "Dockerfile"
SRC_DOCKER_COMPOSE = BUILDER_DIR / "docker-compose.yml"
SRC_ENV_EXAMPLE = BUILDER_DIR / ".env.example"
SRC_README_ENV = BUILDER_DIR / "ENVIRONMENT.md"
SRC_RELEASE_README = BUILDER_DIR / "README-release.md"
SRC_NGINX_TEMPLATE = BUILDER_DIR / "nginx-template.conf"

# Build artifacts
DOCKER_IMAGE_TAG = "cgm-remote-monitor:local"
DOCKER_IMAGE_TAR = BUILD_DIR / "cgm-remote-monitor.tar"


def run(cmd, cwd=None, check=True, capture=False):
    """Run a shell command.

    Args:
        cmd: Command list to run
        cwd: Working directory
        check: Exit on failure if True
        capture: If True, capture output and return it. If False, stream to console.
    """
    print(f"🔨 Running: {' '.join(cmd)}")

    if capture:
        # Capture output for processing
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"❌ Command failed: {' '.join(cmd)}")
            print(f"Error: {result.stderr}")
            sys.exit(1)
        return result
    else:
        # Stream output in real-time
        process = subprocess.Popen(cmd, cwd=cwd, stdout=None, stderr=None, text=True)
        process.wait()

        if check and process.returncode != 0:
            print(f"❌ Command failed: {' '.join(cmd)}")
            sys.exit(1)

        # Return a mock result object for compatibility
        class MockResult:
            def __init__(self, returncode, stdout=""):
                self.returncode = returncode
                self.stdout = stdout

        return MockResult(process.returncode)


def check_prerequisites():
    """Verify Docker is available and git state is clean."""
    print("📋 Checking prerequisites...")

    # Check Docker
    try:
        subprocess.run(["docker", "info"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Error: Docker is not running or not installed")
        sys.exit(1)

    # Check git state
    result = run(
        ["git", "status", "--porcelain"], cwd=REPO_ROOT, check=False, capture=True
    )
    if result.stdout.strip():
        print("❌ Error: Working directory is not clean")
        print("Uncommitted changes:")
        print(result.stdout)
        print("\nPlease commit or stash changes before building.")
        sys.exit(1)

    # Check we're on a tag
    result = run(
        ["git", "describe", "--tags", "--exact-match"],
        cwd=REPO_ROOT,
        check=False,
        capture=True,
    )
    if result.returncode != 0:
        print("⚠️  Warning: Not on a version tag")
        print(
            "Current state:",
            run(
                ["git", "describe", "--tags"], cwd=REPO_ROOT, capture=True
            ).stdout.strip(),
        )
        response = input("Continue anyway? (y/N): ")
        if response.lower() != "y":
            sys.exit(1)

    print("✅ Prerequisites checked\n")


def extract_version():
    """Extract version from git tag."""
    result = run(
        ["git", "describe", "--tags", "--exact-match"], cwd=REPO_ROOT, capture=True
    )
    tag = result.stdout.strip()

    # Remove 'v' prefix if present
    version = tag.lstrip("v")

    # Validate semver format
    if not re.match(r"^\d+\.\d+\.\d+", version):
        print(f"⚠️  Warning: Tag '{tag}' doesn't match semver format (X.Y.Z)")
        response = input(f"Use version '{version}' anyway? (y/N): ")
        if response.lower() != "y":
            sys.exit(1)

    return version


def clean_build_dir():
    """Remove old build artifacts."""
    print("🧹 Cleaning build directory...")
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    print("✅ Build directory cleaned\n")


def build_docker_image():
    """Build Docker image from official Dockerfile."""
    print("🐳 Building Docker image...")

    # Verify Dockerfile exists
    if not SRC_DOCKERFILE.exists():
        print(f"❌ Error: Dockerfile not found at {SRC_DOCKERFILE}")
        sys.exit(1)

    # Build image
    run(
        [
            "docker",
            "build",
            "-t",
            DOCKER_IMAGE_TAG,
            "-f",
            str(SRC_DOCKERFILE),
            str(REPO_ROOT),
        ]
    )

    print("✅ Docker image built\n")


def export_docker_image():
    """Export Docker image as tarball."""
    print("📦 Exporting Docker image...")

    run(["docker", "save", "-o", str(DOCKER_IMAGE_TAR), DOCKER_IMAGE_TAG])

    # Get image size
    size_mb = DOCKER_IMAGE_TAR.stat().st_size / (1024 * 1024)
    print(f"✅ Docker image exported ({size_mb:.1f} MB)\n")


def create_archive(version):
    """Create versioned zip archive."""
    print("🗜️  Creating release archive...")

    # Ensure released directory exists
    RELEASED_DIR.mkdir(parents=True, exist_ok=True)

    # Archive filename
    archive_name = f"cgm-remote-monitor-v{version}.zip"
    archive_path = RELEASED_DIR / archive_name

    # Remove old archive if exists
    if archive_path.exists():
        print(f"🗑️  Removing old archive: {archive_name}")
        archive_path.unlink()

    # Create zip file
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add docker-compose.yml
        if SRC_DOCKER_COMPOSE.exists():
            zf.write(SRC_DOCKER_COMPOSE, "docker-compose.yml")
            print("  📄 Added: docker-compose.yml")
        else:
            print(f"  ⚠️  Missing: docker-compose.yml")

        # Add .env.example
        if SRC_ENV_EXAMPLE.exists():
            zf.write(SRC_ENV_EXAMPLE, ".env.example")
            print("  📄 Added: .env.example")
        else:
            print(f"  ⚠️  Missing: .env.example")

        # Add ENVIRONMENT.md
        if SRC_README_ENV.exists():
            zf.write(SRC_README_ENV, "ENVIRONMENT.md")
            print("  📄 Added: ENVIRONMENT.md")
        else:
            print(f"  ⚠️  Missing: ENVIRONMENT.md")

        # Add README.md
        if SRC_RELEASE_README.exists():
            zf.write(SRC_RELEASE_README, "README.md")
            print("  📄 Added: README.md")
        else:
            print(f"  ⚠️  Missing: README-release.md")

        # Add nginx template
        if SRC_NGINX_TEMPLATE.exists():
            zf.write(SRC_NGINX_TEMPLATE, "nginx-template.conf")
            print("  📄 Added: nginx-template.conf")
        else:
            print(f"  ⚠️  Missing: nginx-template.conf")

        # Add Docker image tarball
        if DOCKER_IMAGE_TAR.exists():
            zf.write(DOCKER_IMAGE_TAR, "cgm-remote-monitor.tar")
            print("  🐳 Added: cgm-remote-monitor.tar")
        else:
            print(f"  ❌ Missing: cgm-remote-monitor.tar")
            sys.exit(1)

    # Get archive size
    archive_size_mb = archive_path.stat().st_size / (1024 * 1024)

    print(f"\n✅ Release archive created: {archive_path}")
    print(f"   Size: {archive_size_mb:.1f} MB")

    return archive_path


def print_summary(version, archive_path):
    """Print build summary and deployment instructions."""
    print("\n" + "=" * 80)
    print("🎉 BUILD SUCCESSFUL!")
    print("=" * 80)
    print(f"\n📦 Release: cgm-remote-monitor-v{version}")
    print(f"📂 Archive: {archive_path}")
    print("\n📋 CONTENTS:")
    print("  - docker-compose.yml      Docker Compose configuration")
    print("  - cgm-remote-monitor.tar  Docker image export")
    print("  - .env.example            Environment variable template")
    print("  - ENVIRONMENT.md          Environment documentation")
    print("  - README.md               Deployment instructions")
    print("  - nginx-template.conf     Nginx reverse proxy template")
    print("\n🚀 DEPLOYMENT:")
    print("  1. Copy archive to server:")
    print(f"     scp {archive_path} user@server:/opt/nightscout/")
    print("\n  2. On server, extract and deploy:")
    print("     cd /opt/nightscout")
    print(f"     unzip {archive_path.name}")
    print("     cp .env.example .env")
    print("     nano .env  # Configure your settings")
    print("     docker load < cgm-remote-monitor.tar")
    print("     docker compose up -d")
    print("\n" + "=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Build CGM-Remote-Monitor release artifacts",
        epilog="""
Examples:
  # Build release from current tag
  python3 build.py

  # Build with verbose output
  python3 build.py --verbose

The cgm-remote-monitor repo must be on a clean git checkout at a version tag.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    args = parser.parse_args()

    print("🚀 CGM-Remote-Monitor Release Builder\n")

    # Run build steps
    check_prerequisites()
    version = extract_version()
    print(f"📌 Building version: {version}\n")

    clean_build_dir()
    build_docker_image()
    export_docker_image()
    archive_path = create_archive(version)

    # Cleanup build directory
    print("🧹 Cleaning up build directory...")
    shutil.rmtree(BUILD_DIR)
    print("✅ Cleanup complete\n")

    print_summary(version, archive_path)


if __name__ == "__main__":
    main()
