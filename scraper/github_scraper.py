import os
import base64
import asyncio
import httpx
import sqlite3
import time
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# GitHub API base URL
GITHUB_API_URL = "https://api.github.com"

# Retrieve GitHub Token
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("❌ GitHub token not found! Set the GITHUB_TOKEN environment variable.")

HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

# Database for caching scraped repositories
DB_FILE = "scraped_repos.db"

# Initialize the database if it doesn't exist
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS repositories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner TEXT,
            repo TEXT,
            last_updated TEXT,
            UNIQUE(owner, repo)
        )
    """)
    conn.commit()
    conn.close()

# Check if a repository is already scraped
def is_repo_scraped(owner, repo):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM repositories WHERE owner = ? AND repo = ?", (owner, repo))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

# Save repository metadata to the database
def save_repo(owner, repo, last_updated):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO repositories (owner, repo, last_updated) VALUES (?, ?, ?)",
                   (owner, repo, last_updated))
    conn.commit()
    conn.close()

# Retry decorator for handling network errors
def retry(max_retries=3, delay=5):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (httpx.HTTPStatusError, httpx.RequestError, httpx.TimeoutException) as e:
                    print(f"⚠️ Attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        print(f"🔄 Retrying in {delay} seconds...")
                        await asyncio.sleep(delay)
            raise ValueError(f"❌ Failed after {max_retries} attempts.")
        return wrapper
    return decorator

# Fetch repository tree with retries
@retry()
async def fetch_repo_tree(owner: str, repo: str) -> List[dict]:
    """Fetch the repository tree from GitHub."""
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/git/trees/main?recursive=1"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return response.json().get("tree", [])

# Fetch raw file content if base64 is unavailable
@retry()
async def fetch_raw_file(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=30)
        response.raise_for_status()
        return response.text

# Download a file with retries
@retry()
async def download_file(owner: str, repo: str, file_path: str, save_dir: Path):
    """Download and decode a file from the GitHub repository."""
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/contents/{file_path}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()

        if 'content' in data and data.get('encoding') == 'base64':
            file_content = base64.b64decode(data['content']).decode('utf-8')
        elif 'download_url' in data:
            file_content = await fetch_raw_file(data['download_url'])
        else:
            print(f"⚠️ File {file_path} is empty or cannot be downloaded.")
            return

        save_path = save_dir / file_path
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(file_content)
        print(f"✅ Successfully downloaded: {file_path}")

# Scrape GitHub repository with improved error handling
async def scrape_github_repo(owner: str, repo: str, file_extension: str = ".py"):
    """Scrape all files with a given extension from a GitHub repository."""
    save_dir = Path(f"scraped_repos/{owner}/{repo}")
    save_dir.mkdir(parents=True, exist_ok=True)

    if is_repo_scraped(owner, repo):
        print(f"⚠️ Repository {owner}/{repo} already scraped. Skipping.")
        return

    print(f"🔍 Fetching repository tree for {owner}/{repo}...")
    try:
        tree = await fetch_repo_tree(owner, repo)
    except ValueError as e:
        print(f"❌ Error fetching repo tree: {e}")
        return

    print("📂 Downloading files...")
    tasks = []
    for item in tree:
        if item["type"] == "blob" and item["path"].endswith(file_extension):
            print(f"⬇️ Downloading: {item['path']}")
            tasks.append(download_file(owner, repo, item["path"], save_dir))

    await asyncio.gather(*tasks, return_exceptions=True)

    # Save repository metadata after scraping
    save_repo(owner, repo, time.strftime("%Y-%m-%d"))

    print(f"✅ Files successfully downloaded to {save_dir}")

if __name__ == "__main__":
    init_db()  # Initialize caching database

    owner = input("Enter the GitHub owner/organization name: ").strip()
    repo = input("Enter the GitHub repository name: ").strip()

    asyncio.run(scrape_github_repo(owner, repo))
