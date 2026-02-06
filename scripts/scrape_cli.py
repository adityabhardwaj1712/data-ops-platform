import asyncio
import sys
import os
import json
import argparse

# Add backend to path
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(os.path.join(project_root, "backend"))

from app.scraper.logic.generic import GenericScraper
from app.llm.schema_builder import AISchemaBuilder

async def run_scrape(url: str, prompt: str = None, schema_json: str = None):
    scraper = GenericScraper()
    builder = AISchemaBuilder()
    
    # 1. Determine Schema
    if prompt:
        print(f"--- Generating schema for prompt: {prompt} ---")
        schema = await builder.build(prompt)
    elif schema_json:
        schema = json.loads(schema_json)
    else:
        schema = {"title": "title", "text": "body"}
        
    print(f"--- Using Schema: {json.dumps(schema, indent=2)} ---")
    
    # 2. Scrape
    print(f"--- Scraping URL: {url} ---")
    result = await scraper.scrape(url, schema, debug=True)
    
    if result.success:
        print("\n✅ Extraction Success!")
        print(json.dumps(result.data, indent=2))
        print(f"\nConfidence: {result.confidence}%")
        print(f"Strategy Used: {result.strategy_used}")
    else:
        print("\n❌ Extraction Failed!")
        print(f"Reason: {result.failure_reason}")
        print(f"Errors: {result.errors}")

def main():
    parser = argparse.ArgumentParser(description="DataOps Scraper CLI")
    parser.add_argument("url", help="URL to scrape")
    parser.add_argument("--prompt", help="AI prompt for schema generation")
    parser.add_argument("--schema", help="JSON string for hardcoded schema")
    
    args = parser.parse_args()
    
    asyncio.run(run_scrape(args.url, args.prompt, args.schema))

if __name__ == "__main__":
    main()
