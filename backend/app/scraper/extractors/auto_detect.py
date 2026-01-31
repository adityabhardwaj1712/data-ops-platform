import logging
from bs4 import BeautifulSoup
from typing import Dict, Any, Tuple
import json

logger = logging.getLogger(__name__)

class AutoDetector:
    """
    Heuristic-based extraction engine that detects fields without a schema.
    Uses Meta tags, JSON-LD, and structural patterns.
    """

    def detect(self, html: str, soup: BeautifulSoup) -> Tuple[Dict[str, Any], float]:
        data = {}
        confidence_points = 0
        total_checks = 6

        # 1. Detect Meta/OG Data
        title = self._get_meta(soup, ["og:title", "twitter:title"]) or soup.title.string if soup.title else None
        if title:
            data["title"] = title.strip()
            confidence_points += 1
            
        desc = self._get_meta(soup, ["og:description", "description", "twitter:description"])
        if desc:
            data["description"] = desc.strip()
            confidence_points += 1

        # 2. Detect JSON-LD (Schema.org)
        json_ld = self._get_json_ld(soup)
        if json_ld:
            # Smart merge: prioritize product/article info
            if "@type" in json_ld:
                data["type"] = json_ld["@type"]
            
            if "name" in json_ld and not data.get("title"):
                data["title"] = json_ld["name"]
            
            if "offers" in json_ld:
                offers = json_ld["offers"]
                if isinstance(offers, dict):
                    data["price"] = offers.get("price")
                    data["currency"] = offers.get("priceCurrency")
                elif isinstance(offers, list) and len(offers) > 0:
                    data["price"] = offers[0].get("price")
                    data["currency"] = offers[0].get("priceCurrency")
            
            confidence_points += 2

        # 3. Structural Heuristics (Price detection fallback)
        if not data.get("price"):
            price = self._find_price_patterns(soup)
            if price:
                data["price"] = price
                confidence_points += 1

        # 4. Image Detection
        image = self._get_meta(soup, ["og:image", "twitter:image"])
        if image:
            data["image_url"] = image
            confidence_points += 1

        # Calculate confidence
        confidence = (confidence_points / total_checks) * 100
        return data, min(confidence, 100.0)

    def _get_meta(self, soup: BeautifulSoup, properties: list) -> str:
        for prop in properties:
            tag = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
            if tag and tag.get("content"):
                return tag.get("content")
        return None

    def _get_json_ld(self, soup: BeautifulSoup) -> Dict:
        try:
            scripts = soup.find_all("script", type="application/ld+json")
            for script in scripts:
                content = json.loads(script.string)
                if isinstance(content, dict):
                    # Prefer Product or Article types
                    if content.get("@type") in ["Product", "NewsArticle", "Article", "Recipe"]:
                        return content
            return None
        except Exception:
            return None

    def _find_price_patterns(self, soup: BeautifulSoup) -> str:
        # Look for common price containers
        price_tags = soup.find_all(["span", "div", "p"], class_=lambda x: x and ("price" in x.lower() or "amount" in x.lower()))
        for tag in price_tags:
            text = tag.get_text().strip()
            if any(c in text for c in ["$", "€", "£", "₹"]):
                return text
        return None
