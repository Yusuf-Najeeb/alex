#!/usr/bin/env python3
"""
Deploy the Alex Financial Advisor Part 7 backend infrastructure.

This script:
  1. Packages the API Lambda function (Docker).
  2. Deploys infrastructure with Terraform (API Gateway + Lambda only).
  3. Prints the API Gateway URL so you can paste it into Vercel as
     NEXT_PUBLIC_API_URL.

The frontend itself is deployed via Vercel (GitHub-connected), not via
this script, so there is no S3 upload or CloudFront invalidation here.
"""

import json
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None, check=True, capture_output=False, env=None):
    """Run a command and optionally capture output."""
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")

    if capture_output:
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True,
            shell=isinstance(cmd, str), env=env,
        )
        if check and result.returncode != 0:
            print(f"Error: {result.stderr}")
            sys.exit(1)
        return result.stdout.strip()

    result = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str), env=env)
    if check and result.returncode != 0:
        sys.exit(1)
    return None


def check_prerequisites():
    """Check that all required tools are installed."""
    print("🔍 Checking prerequisites...")

    tools = {
        "docker": "Docker is required for Lambda packaging",
        "terraform": "Terraform is required for infrastructure deployment",
        "aws": "AWS CLI is required",
    }

    for tool, message in tools.items():
        try:
            run_command([tool, "--version"], capture_output=True)
            print(f"  ✅ {tool} is installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"  ❌ {message}")
            sys.exit(1)

    try:
        run_command(["docker", "info"], capture_output=True)
        print("  ✅ Docker is running")
    except subprocess.CalledProcessError:
        print("  ❌ Docker is not running. Please start Docker Desktop.")
        sys.exit(1)

    try:
        run_command(["aws", "sts", "get-caller-identity"], capture_output=True)
        print("  ✅ AWS credentials configured")
    except subprocess.CalledProcessError:
        print("  ❌ AWS credentials not configured. Run 'aws configure'")
        sys.exit(1)


def package_lambda():
    """Package the Lambda function using Docker."""
    print("\n📦 Packaging API Lambda function...")

    api_dir = Path(__file__).parent.parent / "backend" / "api"
    if not api_dir.exists():
        print(f"  ❌ API directory not found: {api_dir}")
        sys.exit(1)

    run_command(["uv", "run", "package_docker.py"], cwd=api_dir)

    lambda_zip = api_dir / "api_lambda.zip"
    if not lambda_zip.exists():
        print(f"  ❌ Lambda package not created: {lambda_zip}")
        sys.exit(1)

    size_mb = lambda_zip.stat().st_size / (1024 * 1024)
    print(f"  ✅ Lambda package created: {lambda_zip} ({size_mb:.2f} MB)")


def deploy_terraform():
    """Deploy infrastructure with Terraform."""
    print("\n🏗️  Deploying infrastructure with Terraform...")

    terraform_dir = Path(__file__).parent.parent / "terraform" / "7_frontend"
    if not terraform_dir.exists():
        print(f"  ❌ Terraform directory not found: {terraform_dir}")
        sys.exit(1)

    if not (terraform_dir / ".terraform").exists():
        print("  Initializing Terraform...")
        run_command(["terraform", "init"], cwd=terraform_dir)

    print("  Planning deployment...")
    run_command(["terraform", "plan"], cwd=terraform_dir)

    print("\n  Applying deployment...")
    run_command(["terraform", "apply", "-auto-approve"], cwd=terraform_dir)

    outputs = run_command(
        ["terraform", "output", "-json"],
        cwd=terraform_dir,
        capture_output=True,
    )
    return json.loads(outputs)


def main():
    print("🚀 Alex Financial Advisor - Part 7 Backend Deployment")
    print("=" * 50)

    check_prerequisites()
    package_lambda()
    outputs = deploy_terraform()

    api_url = outputs["api_gateway_url"]["value"]
    lambda_name = outputs["lambda_function_name"]["value"]

    print("\n" + "=" * 50)
    print("✅ Deployment complete!")
    print(f"\n🌐 API Gateway URL:\n   {api_url}")
    print("\n📋 Next steps:")
    print("   1. In Vercel → Project Settings → Environment Variables, set:")
    print(f"        NEXT_PUBLIC_API_URL = {api_url}")
    print("      then redeploy the Vercel project.")
    print("   2. Once you have your Vercel URL, add it to")
    print("      terraform/7_frontend/terraform.tfvars:")
    print('        cors_origins = "http://localhost:3000,https://<your>.vercel.app"')
    print("      and re-run this script (or `terraform apply`).")
    print(f"\n📊 Lambda logs: AWS Console > Lambda > {lambda_name}")


if __name__ == "__main__":
    main()
