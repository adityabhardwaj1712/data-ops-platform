import sys
import os
import asyncio

# Fix Path: Add 'backend' directory to sys.path so 'app' is top-level
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
backend_dir = os.path.join(project_root, "backend")
sys.path.append(backend_dir)

try:
    from app.scraper.logic.product import ProductScraper
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

async def test():
    print("--- Starting Scraper Logic Smoke Test ---")
    scraper = ProductScraper()
    
    # Test 1: Flipkart
    flipkart_url = "https://www.flipkart.com/apple-iphone-13-starlight-128-gb/p/itm..."
    if await scraper.can_handle(flipkart_url):
        print("✅ Flipkart URL detected correctly.")
    else:
        print("❌ Flipkart URL detection FAILED.")

    # Test 2: Amazon
    amazon_url = "https://www.amazon.com/dp/B08"
    if await scraper.can_handle(amazon_url):
        print("✅ Amazon URL detected correctly.")
    else:
        print("❌ Amazon URL detection FAILED.")

    # Test 3: Generic
    google_url = "https://google.com"
    if not await scraper.can_handle(google_url):
        print("✅ Non-product URL correctly ignored.")
    else:
        print("❌ Non-product URL incorrectly accepted.")

    print("--- Smoke Test Complete ---")

if __name__ == "__main__":
    asyncio.run(test())
