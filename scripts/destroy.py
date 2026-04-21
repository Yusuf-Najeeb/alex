#!/usr/bin/env python3
"""
Destroy the Alex Financial Advisor Part 7 backend infrastructure.

This script:
  1. Destroys the API Gateway + Lambda with Terraform.
  2. Cleans up local artifacts (Lambda zip, frontend build output).

The frontend is hosted on Vercel, so nothing to tear down on AWS for it.
Remove the Vercel project manually from the Vercel dashboard if desired.
"""

import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None, check=True, capture_output=False):
    """Run a command and optionally capture output."""
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")

    if capture_output:
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True,
            shell=isinstance(cmd, str),
        )
        if check and result.returncode != 0:
            print(f"Error: {result.stderr}")
            return None
        return result.stdout.strip()

    result = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str))
    if check and result.returncode != 0:
        return False
    return True


def confirm_destruction():
    """Ask for confirmation before destroying resources."""
    print("⚠️  WARNING: This will destroy all Part 7 backend infrastructure!")
    print("This includes:")
    print("  - API Gateway (HTTP API)")
    print("  - API Lambda function")
    print("  - IAM roles and policies")
    print("")
    print("Note: The Vercel frontend is NOT touched — remove it in the Vercel")
    print("dashboard if you want to tear it down too.")
    print("")

    response = input("Are you sure you want to continue? Type 'yes' to confirm: ")
    return response.lower() == "yes"


def destroy_terraform():
    """Destroy infrastructure with Terraform."""
    print("\n🏗️  Destroying infrastructure with Terraform...")

    terraform_dir = Path(__file__).parent.parent / "terraform" / "7_frontend"
    if not terraform_dir.exists():
        print(f"  ❌ Terraform directory not found: {terraform_dir}")
        return False

    if not (terraform_dir / ".terraform").exists():
        print("  ⚠️  Terraform not initialized, nothing to destroy")
        return True

    print("  Running terraform destroy...")
    print("  Type 'yes' when prompted to confirm destruction.")

    success = run_command(["terraform", "destroy"], cwd=terraform_dir)

    if success:
        print("  ✅ Infrastructure destroyed successfully")
    else:
        print("  ❌ Failed to destroy infrastructure")
        print("  You may need to manually clean up resources in AWS Console")

    return success


def clean_local_artifacts():
    """Clean up local build artifacts."""
    print("\n🧹 Cleaning up local artifacts...")

    artifacts = [
        Path(__file__).parent.parent / "backend" / "api" / "api_lambda.zip",
        Path(__file__).parent.parent / "frontend" / "out",
        Path(__file__).parent.parent / "frontend" / ".next",
    ]

    for artifact in artifacts:
        if not artifact.exists():
            continue
        if artifact.is_file():
            artifact.unlink()
            print(f"  Deleted: {artifact}")
        else:
            shutil.rmtree(artifact)
            print(f"  Deleted directory: {artifact}")

    print("  ✅ Local artifacts cleaned")


def main():
    print("💥 Alex Financial Advisor - Part 7 Infrastructure Destruction")
    print("=" * 60)

    if not confirm_destruction():
        print("\n❌ Destruction cancelled")
        sys.exit(0)

    destroy_terraform()
    clean_local_artifacts()

    print("\n" + "=" * 60)
    print("✅ Destruction complete!")
    print("\nTo redeploy the backend, run:")
    print("  uv run scripts/deploy.py")


if __name__ == "__main__":
    main()
