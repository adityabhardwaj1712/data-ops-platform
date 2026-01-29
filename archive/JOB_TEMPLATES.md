# Hardened Job Templates

These templates provide "production-ready" configurations for our primary use cases. They include selector assumptions and documentation for each field.

## 1. Directory Listing (e.g., Doctors, Lawyers, Stores)
Use this for pages that list multiple entities with contact info.

```json
{
  "description": "NYC Dental Clinics Extraction",
  "schema": {
    "container": ".clinic-card", 
    "fields": {
      "name": "h3.title", 
      "phone": ".phone-number",
      "address": ".address-line-1",
      "rating": ".rating-value"
    },
    "assumptions": {
      "phone": "Expects format (XXX) XXX-XXXX",
      "address": "Must contain a Zip Code",
      "name": "Must be non-empty"
    }
  },
  "config": {
    "strategy": "browser",
    "wait_for_selector": ".clinic-card",
    "timeout": 30
  }
}
```

## 2. E-commerce Product Search
Use this for competitor price tracking.

```json
{
  "description": "Electronics Competitor Monitoring",
  "schema": {
    "container": "[data-component-type='s-search-result']",
    "fields": {
      "product_name": "h2 span",
      "price": ".a-price-whole",
      "sku": "data-asin",
      "is_prime": ".s-prime-label"
    },
    "assumptions": {
      "price": "Numerical value only",
      "product_name": "Minimum 10 characters"
    }
  },
  "config": {
    "strategy": "stealth",
    "use_proxy": true,
    "wait_for_selector": ".s-result-list",
    "timeout": 45
  }
}
```

## 3. Article / News Feed
Use this for industry news aggregation.

```json
{
  "description": "Tech News Aggregator",
  "schema": {
    "container": "article.post",
    "fields": {
      "title": "h2.entry-title",
      "author": ".author-name",
      "date": "time.entry-date",
      "summary": ".entry-summary"
    },
    "assumptions": {
      "date": "ISO8601 format preferred",
      "title": "Unique per scrape session"
    }
  },
  "config": {
    "strategy": "static",
    "timeout": 15
  }
}
```

---
> [!TIP]
> **Selector Hardening**: Avoid using `div > div > span`. Use semantic classes (`.title`, `.price`) or data attributes (`[data-test-id='price']`) whenever possible.
