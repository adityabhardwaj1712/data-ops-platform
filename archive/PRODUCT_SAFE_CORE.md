# Product-Safe Core
*The narrow subset of features that COULD be self-serve.*

If we were to launch a "Lite" product, it would ONLY support:

## 1. Supported Site Types
- **Static Listings**: e.g., Simple job boards, directories (No JS, No Auth).
- **RSS Feeds**: Structured xml feeds.
- **Sitemaps**: Extracting URLs from `sitemap.xml`.

## 2. Allowed Features
- **Strategy**: `STATIC` only (Requests/HTTPX). No Browsers.
- **Extraction**: "Text only" or pre-defined schemas (e.g., Schema.org metadata).
- **Output**: CSV / JSON download.

## 3. Hard Exclusions
- ❌ **No Login Support**: Too risky for SaaS.
- ❌ **No Browser Rendering**: Too expensive/slow for self-serve margins.
- ❌ **No Custom Selectors**: Users must rely on AI/Heuristic extraction only.
- ❌ **No CAPTCHA Solving**: We do not offer bypass as a service.

## Summary
The "Product-Safe Core" is basically a **Smart Curl** tool. 
Anything more complex remains a **Managed Service**.
