import asyncio
import json
import logging
import os
from typing import Dict, Any

# Mocking the scraper call for simulation purposes
# In a real scenario, this would call GenericScraper.run()
async def simulate_scrape(url: str, schema: Dict[str, Any]):
    print(f"\n--- SCRAPING: {url} ---")
    print(f"Using Schema: {json.dumps(schema, indent=2)}")
    
    # Simulate a common failure pattern: Selector missing
    if "container" in schema and schema["container"] == ".product-item-v1":
        print("RESULT: FAILURE")
        print("REASON: Selector '.product-item-v1' not found in page.")
        return {
            "success": False,
            "error": "SelectorNotFound",
            "artifact_path": "data/artifacts/sample_job_failed.html",
            "screenshot_path": "data/artifacts/sample_job_failed.png"
        }
    
    # Simulate Success
    print("RESULT: SUCCESS")
    return {
        "success": True,
        "data": [
            {"title": "Reliable Product", "price": "$99.99"},
            {"title": "Solid Item", "price": "$45.00"}
        ],
        "confidence": 95.0
    }

async def main():
    # 1. First Attempt (Broken)
    url = "https://example.com/listings"
    schema_v1 = {
        "container": ".product-item-v1",
        "fields": {
            "title": "h2",
            "price": "span.price"
        }
    }
    
    result = await simulate_scrape(url, schema_v1)
    
    if not result["success"]:
        print(f"\n[INSPECT]: View artifacts at {result['artifact_path']}")
        print("[FIX]: Correcting selector based on artifact inspection...")
        
        # 2. Second Attempt (Fixed)
        schema_v2 = {
            "container": ".product-card", # Fixed selector
            "fields": {
                "title": "h3",
                "price": ".amount"
            }
        }
        
        result_fixed = await simulate_scrape(url, schema_v2)
        if result_fixed["success"]:
            print("\nVERIFIED: Data extracted correctly with fixed selectors.")
            print(f"Data Sample: {result_fixed['data'][0]}")

if __name__ == "__main__":
    asyncio.run(main())
