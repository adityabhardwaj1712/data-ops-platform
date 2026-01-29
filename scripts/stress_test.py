"""
Multi-Site Stress Test (Task 30)
Executes scrapes on 5 diverse sites and tracks reliability metrics.
"""
import asyncio
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add backend_fastapi to path
sys.path.append(str(Path("backend_fastapi").absolute()))

# Create artifacts dir
os.makedirs("artifacts", exist_ok=True)

from app.scraper.generic import GenericScraper

TEST_SITES = [
    {
        "name": "HackerNews (Static)",
        "url": "https://news.ycombinator.com/",
        "schema": {"container": ".athing", "fields": {"title": ".titleline > a", "score": ".score"}},
        "strategy": "static"
    },
    {
        "name": "BooksToScrape (Listing)",
        "url": "https://books.toscrape.com/",
        "schema": {"container": ".product_pod", "fields": {"name": "h3 a", "price": ".price_color"}},
        "strategy": "static"
    },
    {
        "name": "QuotesToScrape (Simple)",
        "url": "https://quotes.toscrape.com/",
        "schema": {"container": ".quote", "fields": {"text": ".text", "author": ".author"}},
        "strategy": "static"
    },
    {
        "name": "ScrapeThisSite (Ajax/JS)",
        "url": "https://www.scrapethissite.com/pages/ajax-javascript/",
        "schema": {"container": ".film", "fields": {"title": ".film-title", "year": ".film-year"}},
        "strategy": "browser"
    },
    {
        "name": "ScrapeThisSite (Simple)",
        "url": "https://www.scrapethissite.com/pages/simple/",
        "schema": {"container": ".country", "fields": {"name": ".country-name", "capital": ".country-capital"}},
        "strategy": "static"
    }
]

async def run_stress_test():
    print("\n🔥 STARTING MULTI-SITE STRESS TEST (Sprint 4)")
    print("="*60)
    
    scraper = GenericScraper()
    results = []

    for site in TEST_SITES:
        print(f"\n📡 Testing: {site['name']}...")
        print(f"   URL: {site['url']}")
        
        start_time = datetime.utcnow()
        try:
            result = await scraper.run(
                url=site['url'],
                schema=site['schema'],
                strategy=site['strategy'],
                timeout=30
            )
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            status = "✅ SUCCESS" if result.success else f"❌ FAILED ({result.failure_reason})"
            print(f"   Status: {status}")
            print(f"   Items:  {len(result.data) if result.data else 0}")
            print(f"   Conf:   {result.confidence*100:.1f}%")
            print(f"   Time:   {duration:.1f}s")
            
            results.append({
                "site": site['name'],
                "success": result.success,
                "items": len(result.data) if result.data else 0,
                "confidence": result.confidence,
                "duration": duration,
                "reason": result.failure_reason
            })
            
        except Exception as e:
            print(f"   ❌ CRITICAL ERROR: {str(e)}")
            results.append({
                "site": site['name'],
                "success": False,
                "items": 0,
                "confidence": 0,
                "duration": (datetime.utcnow() - start_time).total_seconds(),
                "reason": "CRITICAL_EXCEPTION"
            })

    # Summary
    print("\n" + "="*60)
    print(" STRESS TEST SUMMARY")
    print("="*60)
    
    total = len(results)
    successes = sum(1 for r in results if r['success'])
    avg_conf = sum(r['confidence'] for r in results) / total if total else 0
    avg_time = sum(r['duration'] for r in results) / total if total else 0
    
    print(f"Total Sites: {total}")
    print(f"Successes:   {successes}/{total} ({successes/total*100:.1f}%)")
    print(f"Avg Conf:    {avg_conf*100:.1f}%")
    print(f"Avg Time:    {avg_time:.2f}s")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(run_stress_test())
