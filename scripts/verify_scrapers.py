import asyncio
import sys
import os

# Add backend to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(os.path.join(project_root, "backend"))

async def test_registry():
    print("Testing Scraper Registry...")
    from app.scraper.logic.registry import scraper_registry, initialize_scrapers
    initialize_scrapers()
    
    # Helper to find scraper
    def get_scraper_for_url(url):
        for scraper in scraper_registry._scrapers:
            if scraper.can_handle(url):
                return scraper
        return scraper_registry._default_scraper

    # Test Amazon URL (ProductScraper)
    amazon_url = "https://www.amazon.in/dp/B0CXF6Z862"
    scraper = get_scraper_for_url(amazon_url)
    print(f"Scraper for Amazon: {scraper.__class__.__name__}")
    assert scraper.__class__.__name__ == "ProductScraper"
    
    # Test Generic URL
    generic_url = "https://example.com"
    scraper = get_scraper_for_url(generic_url)
    print(f"Scraper for Generic: {scraper.__class__.__name__}")
    assert scraper.__class__.__name__ in ["GenericScraper", "StaticStrategy", "BrowserStrategy"]
    
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
