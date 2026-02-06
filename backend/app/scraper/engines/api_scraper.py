"""
API Scraper - Direct JSON endpoint scraping

Reverse-engineers and scrapes JSON APIs for fast, structured data extraction.
"""
import logging
import asyncio
from typing import Dict, Any, Optional, List
import httpx
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import json

from app.scraper.logic.base import BaseScraper
from app.schemas import ScrapeResult, ScrapeFailureReason
from app.scraper.utils.headers import get_random_headers

logger = logging.getLogger(__name__)


class APIScraper(BaseScraper):
    """
    Specialized scraper for JSON API endpoints.
    10x faster than browser-based scraping.
    """
    
    def get_name(self) -> str:
        return "api"
    
    def can_handle(self, url: str) -> bool:
        """Detect if URL is likely an API endpoint"""
        api_patterns = [
            '/api/', '/v1/', '/v2/', '/v3/',
            '/graphql', '.json', '/rest/',
            '/data/', '/feed/'
        ]
        return any(pattern in url.lower() for pattern in api_patterns)
    
    async def scrape(
        self,
        url: str,
        schema: Dict[str, Any],
        job_id: str,
        **kwargs
    ) -> ScrapeResult:
        """
        Scrape JSON API endpoint
        
        Args:
            url: API endpoint URL
            schema: Data extraction schema (field mappings)
            job_id: Job identifier
            **kwargs: Additional options (headers, params, api_endpoint)
        """
        logger.info(f"Starting API scrape for {url}")
        
        try:
            await self.throttle(url, min_delay=0.5)  # Faster for APIs
            
            # Use custom API endpoint if provided
            api_url = kwargs.get('api_endpoint', url)
            
            # Extract pagination parameters if present
            parsed_url = urlparse(api_url)
            query_params = parse_qs(parsed_url.query)
            
            # Fetch data
            data = await self._fetch_json(
                api_url,
                headers=kwargs.get('headers'),
                params=kwargs.get('params'),
                timeout=kwargs.get('timeout', 30)
            )
            
            if not data:
                return self.failure(
                    reason=ScrapeFailureReason.EMPTY_DATA,
                    message="API returned empty response"
                )
            
            # Extract fields according to schema
            extracted = self._extract_fields(data, schema)
            
            # Handle pagination if max_pages > 1
            max_pages = kwargs.get('max_pages', 1)
            all_results = [extracted] if extracted else []
            
            if max_pages > 1:
                all_results.extend(
                    await self._handle_pagination(
                        api_url, schema, max_pages, query_params
                    )
                )
            
            return ScrapeResult(
                success=True,
                status="success",
                data=all_results if len(all_results) > 1 else extracted,
                strategy_used=self.get_name(),
                pages_scraped=len(all_results),
                confidence=0.95,  # APIs are highly reliable
                metadata={
                    "api_endpoint": api_url,
                    "response_type": "json",
                    "total_records": len(all_results)
                }
            )
            
        except httpx.HTTPStatusError as e:
            return self.failure(
                reason=ScrapeFailureReason.FETCH_FAILED,
                message=f"API request failed: {e.response.status_code}",
                errors=[str(e)]
            )
        except json.JSONDecodeError as e:
            return self.failure(
                reason=ScrapeFailureReason.VALIDATION_FAILED,
                message="Response is not valid JSON",
                errors=[str(e)]
            )
        except Exception as e:
            logger.error(f"API scraping failed: {e}", exc_info=True)
            return self.failure(
                reason=ScrapeFailureReason.UNKNOWN,
                message=f"Unexpected error: {str(e)}",
                errors=[str(e)]
            )
    
    async def _fetch_json(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30
    ) -> Any:
        """Fetch JSON data from API endpoint"""
        request_headers = headers or get_random_headers()
        request_headers['Accept'] = 'application/json'
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(
                url,
                headers=request_headers,
                params=params,
                follow_redirects=True
            )
            response.raise_for_status()
            return response.json()
    
    def _extract_fields(
        self,
        data: Any,
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract fields from JSON response according to schema
        
        Schema format:
        {
            "title": "data.product.name",  # JSON path
            "price": "data.product.price.amount"
        }
        """
        extracted = {}
        
        for field_name, json_path in schema.items():
            value = self._get_nested_value(data, json_path)
            extracted[field_name] = value
        
        return extracted
    
    def _get_nested_value(self, data: Any, path: str) -> Any:
        """
        Get value from nested JSON using dot notation
        
        Example: "data.items[0].name" -> data['items'][0]['name']
        """
        if not path:
            return data
        
        parts = path.split('.')
        current = data
        
        for part in parts:
            if current is None:
                return None
            
            # Handle array indexing: items[0]
            if '[' in part and ']' in part:
                key = part[:part.index('[')]
                index = int(part[part.index('[')+1:part.index(']')])
                
                if isinstance(current, dict) and key in current:
                    current = current[key]
                    if isinstance(current, list) and len(current) > index:
                        current = current[index]
                    else:
                        return None
                else:
                    return None
            else:
                # Regular dict access
                if isinstance(current, dict) and part in current:
                    current = current[part]
                elif isinstance(current, list):
                    # If current is a list, try to extract from all items
                    return [self._get_nested_value(item, '.'.join(parts[parts.index(part):])) 
                            for item in current]
                else:
                    return None
        
        return current
    
    async def _handle_pagination(
        self,
        base_url: str,
        schema: Dict[str, Any],
        max_pages: int,
        initial_params: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """Handle API pagination"""
        results = []
        
        # Common pagination patterns
        page_param_names = ['page', 'p', 'offset', 'start', 'pageNumber']
        
        # Find which parameter is used for pagination
        page_param = None
        for param in page_param_names:
            if param in initial_params:
                page_param = param
                break
        
        if not page_param:
            # Try adding 'page' parameter
            page_param = 'page'
        
        # Fetch additional pages
        for page_num in range(2, max_pages + 1):
            try:
                # Update pagination parameter
                params = initial_params.copy()
                params[page_param] = [str(page_num)]
                
                # Construct URL with new params
                parsed = urlparse(base_url)
                new_query = urlencode(params, doseq=True)
                paginated_url = urlunparse((
                    parsed.scheme, parsed.netloc, parsed.path,
                    parsed.params, new_query, parsed.fragment
                ))
                
                # Fetch page
                data = await self._fetch_json(paginated_url)
                
                if not data:
                    break  # No more data
                
                extracted = self._extract_fields(data, schema)
                if extracted:
                    results.append(extracted)
                
                # Respectful delay between requests
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.warning(f"Pagination failed at page {page_num}: {e}")
                break
        
        return results
