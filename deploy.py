"""Deployment script for gdpr-cnil-compliance-generator."""
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.request
import urllib.error

REPO_DIR = Path(r"c:\Users\Ender\Documents\Money\swarm\agent15_gdpr_saas")
REPO_NAME = "gdpr-cnil-compliance-generator"
GITHUB_USER = "EroNiiChan"

def get_token():
    p = subprocess.Popen(
        ['git', '-c', 'credential.interactive=never', 'credential', 'fill'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    inp = 'protocol=https\nhost=github.com\nusername=EroNiiChan\n\n'
    out, err = p.communicate(inp, timeout=10)
    for line in out.splitlines():
        if line.startswith('password='):
            return line.split('=', 1)[1]
    raise RuntimeError(f"Failed to extract GitHub token: {err}")

def run(cmd, cwd=REPO_DIR):
    print("Running:", cmd)
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, timeout=10)
    if res.stdout:
        print("STDOUT:", res.stdout.strip())
    if res.stderr:
        print("STDERR:", res.stderr.strip())
    if res.returncode != 0:
        raise RuntimeError(f"Command failed with code {res.returncode}")

def ensure_github_repo(token):
    headers = {
        'Authorization': f'Bearer {token}',
        'User-Agent': 'Agent15-SaaS',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Check if repo exists
    check_url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}"
    req = urllib.request.Request(check_url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"Repository {GITHUB_USER}/{REPO_NAME} already exists.")
            return
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise

    # Create repo
    print(f"Creating repository {GITHUB_USER}/{REPO_NAME}...")
    create_url = "https://api.github.com/user/repos"
    payload = json.dumps({
        "name": REPO_NAME,
        "description": "Zero-dependency 2026 GDPR & CNIL Cookie Compliance Auditor + DPA & Privacy Policy Generator",
        "homepage": f"https://{GITHUB_USER.lower()}.github.io/{REPO_NAME}/",
        "private": False,
        "has_issues": True,
        "has_projects": True,
        "has_wiki": False
    }).encode("utf-8")

    create_req = urllib.request.Request(create_url, data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(create_req, timeout=10) as resp:
        res_data = json.loads(resp.read().decode())
        print(f"Repository created successfully: {res_data.get('html_url')}")

def enable_github_pages(token):
    headers = {
        'Authorization': f'Bearer {token}',
        'User-Agent': 'Agent15-SaaS',
        'Accept': 'application/vnd.github.v3+json'
    }
    pages_url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/pages"
    
    # Check current pages status
    req = urllib.request.Request(pages_url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            print("GitHub Pages already enabled.")
            return
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"Pages status check returned {e.code}")

    # Enable pages
    print("Enabling GitHub Pages on main branch / ...")
    payload = json.dumps({
        "source": {
            "branch": "main",
            "path": "/"
        }
    }).encode("utf-8")
    
    post_req = urllib.request.Request(pages_url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(post_req, timeout=10) as resp:
            print("GitHub Pages enabled successfully!")
    except urllib.error.HTTPError as e:
        print(f"Pages creation returned HTTP {e.code}: {e.read().decode('utf-8', errors='ignore')}")

def main():
    token = get_token()
    print("Retrieved GitHub token successfully.")
    
    # 1. Ensure GitHub repo exists
    ensure_github_repo(token)
    
    # 2. Local git setup
    run("git init")
    run('git config user.name "EroNiiChan"')
    run('git config user.email "eroniichan@users.noreply.github.com"')
    
    # Check branch name or create main
    run("git checkout -B main")
    run("git add -A")
    subprocess.run('git commit -m "feat: initial release of 2026 GDPR & CNIL compliance auditor and legal generator"', cwd=REPO_DIR, shell=True, capture_output=True, timeout=10)
    
    # 3. Push to remote
    remote_auth_url = f"https://x-access-token:{token}@github.com/{GITHUB_USER}/{REPO_NAME}.git"
    clean_url = f"https://github.com/{GITHUB_USER}/{REPO_NAME}.git"
    
    subprocess.run("git remote remove origin", cwd=REPO_DIR, shell=True, capture_output=True, timeout=10)
    run(f'git remote add origin "{remote_auth_url}"')
    run("git push -u origin main --force")
    
    # Clean remote URL immediately
    run(f'git remote set-url origin "{clean_url}"')
    print("Cleaned remote URL.")
    
    # 4. Enable GitHub Pages
    time.sleep(1)
    enable_github_pages(token)
    
    print("\n--- DEPLOYMENT COMPLETE ---")
    print(f"Repository URL: {clean_url}")
    print(f"GitHub Pages URL: https://{GITHUB_USER.lower()}.github.io/{REPO_NAME}/")

if __name__ == "__main__":
    main()
