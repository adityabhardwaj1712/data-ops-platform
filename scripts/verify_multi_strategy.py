"""
Comprehensive verification script for multi-strategy scraping system

Tests all backend scrapers, schemas, and API endpoints.
"""
import sys
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

async def test_imports():
    """Test all critical imports"""
    print("🔍 Testing Backend Imports...")
    
    try:
        # Test scraper engines
        from app.scraper.engines.api_scraper import APIScraper
        from app.scraper.engines.crawler import CrawlerScraper
        from app.scraper.engines.document_scraper import DocumentScraper
        from app.scraper.engines.authenticated import AuthenticatedScraper
        from app.scraper.engines.ocr_scraper import OCRScraper
        from app.scraper.engines.streaming_scraper import StreamingScraper
        print("  ✅ All scraper engines import successfully")
        
        # Test schemas
        from app.schemas import (
            ScrapeStrategy, ScrapeRequest, AuthConfig, 
            CrawlConfig, StreamingConfig, DocumentConfig, OCRConfig
        )
        print("  ✅ All schemas import successfully")
        
        # Test registry
        from app.scraper.logic.registry import scraper_registry
        print(f"  ✅ Registry initialized with {len(scraper_registry._scrapers)} scrapers")
        
        # Test API routes
        from app.api.scrape import router
        print("  ✅ API routes import successfully")
        
        # Test utilities
        from app.scraper.utils.headers import get_random_headers
        from app.scraper.utils.robots_checker import robots_checker
        print("  ✅ Utility modules import successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_scraper_initialization():
    """Test scraper initialization"""
    print("\n🔧 Testing Scraper Initialization...")
    
    try:
        from app.scraper.engines.api_scraper import APIScraper
        from app.scraper.engines.crawler import CrawlerScraper
        
        api_scraper = APIScraper()
        print(f"  ✅ APIScraper: {api_scraper.get_name()}")
        
        crawler = CrawlerScraper()
        print(f"  ✅ CrawlerScraper: {crawler.get_name()}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Initialization failed: {e}")
        return False


async def test_schema_validation():
    """Test schema validation"""
    print("\n📋 Testing Schema Validation...")
    
    try:
        from app.schemas import ScrapeRequest, CrawlConfig, AuthConfig
        
        # Test basic scrape request
        request = ScrapeRequest(
            url="https://example.com",
            schema={"title": "h1"},
            strategy="auto"
        )
        print(f"  ✅ Basic ScrapeRequest validated")
        
        # Test with crawl config
        crawl_config = CrawlConfig(
            max_depth=2,
            max_pages=50,
            follow_external_links=False
        )
        request_with_crawl = ScrapeRequest(
            url="https://example.com",
            schema={"title": "h1"},
            strategy="crawler",
            crawl_config=crawl_config
        )
        print(f"  ✅ ScrapeRequest with CrawlConfig validated")
        
        # Test with auth config
        auth_config = AuthConfig(
            method="cookies",
            cookies=[{"name": "session", "value": "abc123", "domain": ".example.com"}]
        )
        request_with_auth = ScrapeRequest(
            url="https://example.com",
            schema={"title": "h1"},
            strategy="auth",
            auth_config=auth_config
        )
        print(f"  ✅ ScrapeRequest with AuthConfig validated")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Schema validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_utility_functions():
    """Test utility functions"""
    print("\n🛠️ Testing Utility Functions...")
    
    try:
        from app.scraper.utils.headers import get_random_headers
        from app.scraper.utils.robots_checker import robots_checker
        
        # Test headers
        headers = get_random_headers()
        assert "User-Agent" in headers
        assert "Accept" in headers
        print(f"  ✅ get_random_headers() works")
        
        # Test robots checker
        allowed = await robots_checker.check_url_allowed("https://example.com")
        assert allowed == True
        print(f"  ✅ robots_checker.check_url_allowed() works")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Utility test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 Multi-Strategy Scraping System Verification")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(await test_imports())
    results.append(await test_scraper_initialization())
    results.append(await test_schema_validation())
    results.append(await test_utility_functions())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
