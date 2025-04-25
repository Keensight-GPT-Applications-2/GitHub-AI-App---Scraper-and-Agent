import os
import sys
from pathlib import Path

# Ensure correct imports from updated generator
project_root = Path(__file__).resolve().parent  
sys.path.append(str(project_root))

from models.pydantic_generator import generate_pydantic_models, save_pydantic_models
from parser import parse_directory, get_latest_scraped_repo

def regenerate_all():
    print("🚀 Starting complete regeneration process...")
    
    # 1. Parse repository and generate models
    base_scraped_dir = "../scraper/scraped_repos"
    latest_repo_dir = get_latest_scraped_repo(base_scraped_dir)

    if latest_repo_dir:
        print(f"📂 Parsing the latest repository: {latest_repo_dir}")
        parsed_results = parse_directory(latest_repo_dir)

        if parsed_results:
            print("\n🔄 Generating Pydantic models...")
            models = generate_pydantic_models(parsed_results)
            print("\n💾 Saving Pydantic models...")
            save_pydantic_models(models)
            
            # 2. Generate microservices based on new models
            print("\n🔄 Generating microservices...")
            
            # Import here to avoid circular imports
            from generate_microservices import generate_microservices
            generate_microservices()
            
            print("\n✅ Regeneration completed successfully!")
        else:
            print("❌ No parsing results were generated.")
    else:
        print("❌ No scraped repositories found.")

if __name__ == "__main__":
    regenerate_all()