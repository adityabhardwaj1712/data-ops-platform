# Paid Use-Cases — DataOps Platform

These are the primary sellable offerings enabled by the platform's current capabilities.

## 1. B2B Lead List Generation
Targeted lists of companies or professionals for sales teams.

- **Input**: Industry keywords (e.g., "SaaS startups in Bangalore"), target role (e.g., "CTO"), and source URL (e.g., directory listing).
- **Output**: CSV/Excel with Company Name, Website, Location, and Key Person (if available).
- **Typical Size**: 500 - 2,000 rows.
- **Selling Point**: Clean, validated data with confidence scores; no "junk" rows.

## 2. E-commerce Competitor Price Tracking
Daily/Weekly snapshots of competitor pricing for dynamic pricing strategies.

- **Input**: Competitor product URLs or category pages.
- **Output**: CSV with Product Name, Current Price, Sku/ID, and Stock Status.
- **Typical Size**: 1,000 - 10,000 rows per crawl.
- **Selling Point**: Handles JS-heavy sites (Browser Strategy) and avoids blocks (Stealth Mode).

## 3. Local Business Directory Extraction
Building niche datasets for service aggregators or marketing agencies.

- **Input**: Google Maps, Yelp, or industry-specific directories (e.g., "Dentists in NYC").
- **Output**: CSV with Business Name, Phone, Address, Rating, and Category.
- **Typical Size**: 2,000 - 5,000 rows.
- **Selling Point**: High accuracy via HITL review for contact info consistency.

---
> [!TIP]
> **Internal Rule**: If a client request falls outside these 3, treat it as "Experimental" and double the estimated cost baseline.
