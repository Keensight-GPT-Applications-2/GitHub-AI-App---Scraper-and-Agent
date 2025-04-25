import os
import base64
import asyncio
import httpx
import sqlite3
import time
import re
import ast
import logging
from pathlib import Path
from typing import List, Optional, Dict, Callable, Tuple, Any
from dataclasses import dataclass
from dotenv import load_dotenv
import json
import psutil

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# GitHub API configuration
GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("❌ GitHub token not found! Set the GITHUB_TOKEN environment variable.")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "GitHubScraper/1.0"
}

# Database configuration
DB_FILE = "scraped_repos.db"
MAX_CACHE_AGE_DAYS = 7  # Refresh repos older than this

# Directory patterns to skip
SKIP_PATTERNS = {
    r'test[s]?/', r'__pycache__/', r'\.github/', r'docs/', 
    r'examples/', r'migrations/', r'venv/', r'env/',
    r'node_modules/', r'dist/', r'build/'
}

class ScraperConfig:
    MAX_FILE_SIZE = 1_000_000  # 1MB
    BATCH_SIZE = 20
    MAX_RETRIES = 3 
    MEMORY_THRESHOLD = 0.8  # 80% memory usage

class ResourceMonitor:
    def __init__(self, max_memory=ScraperConfig.MEMORY_THRESHOLD):
        self.max_memory = max_memory
        self.process = psutil.Process(os.getpid())

    async def check_resources(self):
        while True:
            mem_usage = self.process.memory_info().rss / (1024 ** 3)  # GB
            if mem_usage > self.max_memory * psutil.virtual_memory().total:
                logger.warning("High memory usage! Pausing processing...")
                await asyncio.sleep(5)
            await asyncio.sleep(1)

@dataclass
class RateLimitStatus:
    remaining: int
    limit: int
    reset_time: int

def init_db():
    """Initialize database with proper schema"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Repositories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS repositories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner TEXT NOT NULL,
            name TEXT NOT NULL,
            language TEXT,
            stars INTEGER DEFAULT 0,
            forks INTEGER DEFAULT 0,
            last_updated TEXT,
            scraped_at TEXT DEFAULT CURRENT_TIMESTAMP,
            metadata_json TEXT,
            UNIQUE(owner, name)
        )
    """)
    
    # Files table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            repo_id INTEGER,
            path TEXT NOT NULL,
            sha TEXT,
            language TEXT,
            function_count INTEGER DEFAULT 0,
            FOREIGN KEY (repo_id) REFERENCES repositories(id),
            UNIQUE(repo_id, path)
        )
    """)
    
    # Functions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS functions (
            file_id INTEGER,
            name TEXT NOT NULL,
            parameters TEXT,  -- JSON array
            return_type TEXT,
            docstring TEXT,
            start_line INTEGER,
            end_line INTEGER,
            source_code TEXT,
            FOREIGN KEY (file_id) REFERENCES files(id),
            UNIQUE(file_id, name)
        )
    """)
    
    conn.commit()
    conn.close()

async def check_rate_limit() -> RateLimitStatus:
    """Check current GitHub API rate limit status"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{GITHUB_API_URL}/rate_limit", headers=HEADERS)
        response.raise_for_status()
        data = response.json()["resources"]["core"]
        return RateLimitStatus(
            remaining=data["remaining"],
            limit=data["limit"],
            reset_time=data["reset"]
        )

async def wait_for_rate_limit_reset():
    """Wait until rate limit resets"""
    status = await check_rate_limit()
    if status.remaining > 0:
        return
    
    wait_time = max(5, status.reset_time - int(time.time())) + 5  # Add buffer
    logger.warning(f"Rate limit exceeded. Waiting {wait_time} seconds...")
    await asyncio.sleep(wait_time)

def should_skip_path(path: str) -> bool:
    """Check if path matches any skip patterns"""
    return any(re.search(pattern, path) for pattern in SKIP_PATTERNS)

def parse_python_function(node: ast.FunctionDef) -> Dict[str, Any]:
    """Extract detailed information from Python function"""
    return {
        "name": node.name,
        "parameters": [{
            "name": arg.arg,
            "type": ast.unparse(arg.annotation) if arg.annotation else None
        } for arg in node.args.args],
        "return_type": ast.unparse(node.returns) if node.returns else None,
        "docstring": ast.get_docstring(node),
        "start_line": node.lineno,
        "end_line": node.end_lineno,
        "source_code": ast.unparse(node)
    }

def analyze_python_file(content: str) -> List[Dict[str, Any]]:
    """Parse Python file and extract functions"""
    try:
        tree = ast.parse(content)
        return [
            parse_python_function(node)
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and not node.name.startswith('_')
        ]
    except Exception as e:
        logger.error(f"Python analysis error: {str(e)}")
        return []

async def search_repositories(
    query: str,
    language: Optional[str] = None,
    min_stars: Optional[int] = None,
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """Search GitHub repositories with filters"""
    params = {"q": query, "per_page": min(max_results, 100)}
    if language:
        params["q"] += f" language:{language}"
    if min_stars:
        params["q"] += f" stars:>={min_stars}"
    
    try:
        await wait_for_rate_limit_reset()
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GITHUB_API_URL}/search/repositories",
                headers=HEADERS,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()["items"][:max_results]
    except httpx.HTTPStatusError as e:
        logger.error(f"Search failed: {e.response.status_code} - {e.response.text}")
        return []

async def fetch_repository(owner: str, repo: str) -> Optional[Dict[str, Any]]:
    """Fetch detailed repository information"""
    try:
        await wait_for_rate_limit_reset()
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GITHUB_API_URL}/repos/{owner}/{repo}",
                headers=HEADERS,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to fetch repo {owner}/{repo}: {e}")
        return None

async def fetch_repo_tree(owner: str, repo: str, ref: str = "main") -> List[Dict[str, Any]]:
    """Fetch repository file tree recursively"""
    branches = [ref, "main", "master"]  # Try multiple branch names
    last_error = None
    
    for branch in branches:
        try:
            await wait_for_rate_limit_reset()
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{GITHUB_API_URL}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1",
                    headers=HEADERS,
                    timeout=30
                )
                response.raise_for_status()
                return response.json().get("tree", [])
        except httpx.HTTPStatusError as e:
            last_error = e
            continue
            
    raise ValueError(f"Failed to fetch tree: {str(last_error)}")

async def download_file(owner: str, repo: str, path: str, save_dir: Path) -> Optional[Path]:
    """Download and save a file from GitHub"""
    try:
        await wait_for_rate_limit_reset()
        async with httpx.AsyncClient() as client:
            # First get file metadata
            meta_response = await client.get(
                f"{GITHUB_API_URL}/repos/{owner}/{repo}/contents/{path}",
                headers=HEADERS,
                timeout=30
            )
            meta_response.raise_for_status()
            file_meta = meta_response.json()
            
            # Then download content
            if 'content' in file_meta and file_meta.get('encoding') == 'base64':
                content = base64.b64decode(file_meta['content']).decode('utf-8')
            elif 'download_url' in file_meta:
                download_response = await client.get(file_meta['download_url'], timeout=30)
                download_response.raise_for_status()
                content = download_response.text
            else:
                logger.warning(f"File {path} has no downloadable content")
                return None
            
            # Save file
            save_path = save_dir / path
            save_path.parent.mkdir(parents=True, exist_ok=True)
            save_path.write_text(content, encoding='utf-8')
            return save_path
            
    except Exception as e:
        logger.error(f"Failed to download {path}: {str(e)}")
        return None

async def process_repository(
    owner: str,
    repo: str,
    file_extensions: List[str] = [".py"],
    force_refresh: bool = False
) -> Dict[str, Any]:
    """Main function to process a repository"""
    # Check if we need to refresh
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, scraped_at FROM repositories WHERE owner = ? AND name = ?",
        (owner, repo)
    )
    repo_data = cursor.fetchone()
    
    if repo_data and not force_refresh:
        repo_id, scraped_at = repo_data
        if (time.time() - time.mktime(time.strptime(scraped_at, "%Y-%m-%d %H:%M:%S"))) < (MAX_CACHE_AGE_DAYS * 86400):
            logger.info(f"Repository {owner}/{repo} is up-to-date in cache")
            return {"status": "cached"}
    
    # Fetch fresh data
    repo_info = await fetch_repository(owner, repo)
    if not repo_info:
        return {"status": "failed", "error": "Could not fetch repo info"}
    
    # Prepare directory
    save_dir = Path(__file__).parent / "scraped_repos" / owner / repo
    save_dir.mkdir(parents=True, exist_ok=True)
    
    # Get file tree
    try:
        tree = await fetch_repo_tree(owner, repo, repo_info.get("default_branch", "main"))
    except Exception as e:
        return {"status": "failed", "error": str(e)}
    
    # Filter and download files
    tasks = []
    for item in tree:
        if (item["type"] == "blob" and 
            any(item["path"].endswith(ext) for ext in file_extensions) and 
            not should_skip_path(item["path"])):
            tasks.append(download_file(owner, repo, item["path"], save_dir))
    
    downloaded_files = await asyncio.gather(*tasks)
    successful_downloads = [f for f in downloaded_files if f is not None]
    
    # Analyze files and store metadata
    repo_id = None
    try:
        # Insert/update repo metadata
        cursor.execute(
            """INSERT OR REPLACE INTO repositories 
            (owner, name, language, stars, forks, last_updated, metadata_json) 
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                owner,
                repo,
                repo_info.get("language"),
                repo_info.get("stargazers_count", 0),
                repo_info.get("forks_count", 0),
                repo_info.get("updated_at"),
                json.dumps(repo_info)
            )
        )
        repo_id = cursor.lastrowid if repo_id is None else repo_id
        
        # Process each downloaded file
        for file_path in successful_downloads:
            if file_path.suffix != ".py":
                continue
                
            content = file_path.read_text(encoding='utf-8')
            functions = analyze_python_file(content)
            
            # Insert file record
            cursor.execute(
                """INSERT OR REPLACE INTO files 
                (repo_id, path, sha, language, function_count) 
                VALUES (?, ?, ?, ?, ?)""",
                (repo_id, str(file_path.relative_to(save_dir)), None, "python", len(functions))
            )
            file_id = cursor.lastrowid
            
            # Insert function records
            for func in functions:
                cursor.execute(
                    """INSERT OR REPLACE INTO functions 
                    (file_id, name, parameters, return_type, docstring, start_line, end_line, source_code) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        file_id,
                        func["name"],
                        json.dumps(func["parameters"]),
                        func["return_type"],
                        func["docstring"],
                        func["start_line"],
                        func["end_line"],
                        func["source_code"]
                    )
                )
        
        conn.commit()
        logger.info(f"Processed {len(successful_downloads)} files with {sum(len(f) for f in functions)} functions")
        return {
            "status": "success",
            "downloaded_files": len(successful_downloads),
            "analyzed_functions": sum(len(f) for f in functions),
            "repo_id": repo_id
        }
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {str(e)}")
        return {"status": "failed", "error": str(e)}
    finally:
        conn.close()

async def main():
    init_db()
    
    # Ask for organization/owner name first
    owner = input("Enter GitHub owner/organization: ").strip()
    
    # Ask for optional filters
    language = input("Filter by language (python/js/go, leave blank for any): ").strip() or None
    min_stars_input = input("Minimum stars (0 for any): ").strip()
    min_stars = int(min_stars_input) if min_stars_input.isdigit() else 0
    
    # Search repositories under the owner with filters
    query = f"user:{owner}"
    if language:
        query += f" language:{language}"
    if min_stars > 0:
        query += f" stars:>={min_stars}"
    
    results = await search_repositories(
        query=query,
        max_results=10
    )
    
    if not results:
        print(f"No repositories found for owner '{owner}' with the given filters.")
        return
    
    print("\nSearch Results:")
    for i, repo in enumerate(results, 1):
        print(f"{i}. {repo['full_name']} - {repo['description']} (★{repo['stargazers_count']})")
    
    choice_input = input(f"\nSelect repo to scrape (1-{len(results)}): ").strip()
    if not choice_input.isdigit() or not (1 <= int(choice_input) <= len(results)):
        print("Invalid selection. Exiting.")
        return
    choice = int(choice_input)
    selected = results[choice - 1]
    owner, repo = selected["full_name"].split("/")
    
    print(f"\nStarting scrape of {owner}/{repo}...")
    result = await process_repository(owner, repo)
    print("\nScraping result:", result)

if __name__ == "__main__":
    asyncio.run(main())
