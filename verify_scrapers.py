import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

async def test_registry():
    print("Testing Scraper Registry...")
    from app.scraper.logic.registry import scraper_registry, initialize_scrapers
    initialize_scrapers()
    
    # Test Amazon URL (ProductScraper)
    amazon_url = "https://www.amazon.in/dp/B0CXF6Z862"
    scraper = await scraper_registry.get_scraper(amazon_url)
    print(f"Scraper for Amazon: {scraper.__class__.__name__}")
    assert scraper.__class__.__name__ == "ProductScraper"
    
    # Test Generic URL
    generic_url = "https://example.com"
    scraper = await scraper_registry.get_scraper(generic_url)
    print(f"Scraper for Generic: {scraper.__class__.__name__}")
    assert scraper.__class__.__name__ == "GenericScraper"
    
    print("Registry test PASSED!")

async def main():
    try:
        await test_registry()
    except Exception as e:
        print(f"Test FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
