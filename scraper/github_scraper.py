import os
import base64
import requests
from pathlib import Path
from typing import List
from dotenv import load_dotenv

load_dotenv()

# GitHub API base URL
GITHUB_API_URL = "https://api.github.com"

# Retrieve GitHub Personal Access Token from environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("GitHub token not found! Set the GITHUB_TOKEN environment variable.")

HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

def fetch_repo_tree(owner: str, repo: str) -> List[dict]:
    """Fetch the repository tree from GitHub."""
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/git/trees/main?recursive=1"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json().get("tree", [])

def download_file(owner: str, repo: str, file_path: str, save_dir: Path):
    """Download and decode a file from the GitHub repository."""
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/contents/{file_path}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    data = response.json()
    if 'content' in data and data.get('encoding') == 'base64':
        # Decode the base64 content
        file_content = base64.b64decode(data['content']).decode('utf-8')
    else:
        print(f"File {file_path} is not base64 encoded or empty.")
        return

    # Save the decoded content to the appropriate directory
    save_path = save_dir / file_path
    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(file_content)

def scrape_github_repo(owner: str, repo: str, file_extension: str = ".py"):
    """Scrape all files with a given extension from a GitHub repository."""
    save_dir = Path(f"scraped_repos/{owner}/{repo}")
    save_dir.mkdir(parents=True, exist_ok=True)

    print(f"Fetching repository tree for {owner}/{repo}...")
    tree = fetch_repo_tree(owner, repo)

    print("Downloading files...")
    for item in tree:
        if item["type"] == "blob" and item["path"].endswith(file_extension):
            print(f"Downloading: {item['path']}")
            download_file(owner, repo, item["path"], save_dir)

    print(f"Files downloaded to {save_dir}")

if __name__ == "__main__":
    # Ask the user for the repository owner and name
    owner = input("Enter the GitHub owner/organization name: ").strip()
    repo = input("Enter the GitHub repository name: ").strip()

    # Run the scraper with the provided details
    scrape_github_repo(owner, repo)
