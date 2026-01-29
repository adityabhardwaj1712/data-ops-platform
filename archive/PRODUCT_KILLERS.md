# Product-Killers
*Why we cannot sell this as a SaaS (yet).*

## 1. Custom Configuration Dependency
- **Issue**: 60% of jobs require manual tweaking of selectors or `config.json`.
- **Product Killer**: Users expect "Enter URL -> Get Data". They cannot debug selectors.

## 2. Dynamic Anti-Bot Evasion
- **Issue**: Cloudflare/Akamai turnstiles often require manual cookie harvesting or specialized proxies.
- **Product Killer**: If we automate this blindly, we risk legal action OR massive proxy bills.

## 3. Data Quality Subjectivity
- **Issue**: "Extract Job Title" is subjective. Is "Senior Engineer" a title or a level?
- **Product Killer**: Users will refund if extraction isn't perfect. Humans handle this nuance; machines struggle.

## 4. Legal / ToS Variance
- **Issue**: Each site has a different `robots.txt` and ToS.
- **Product Killer**: A SaaS user might target `facebook.com` blindly. As a Service, we can say "No".

## 5. Cost Unpredictability
- **Issue**: Some sites are cheap (static HTML). Some are huge (infinite scroll + proxies).
- **Product Killer**: Hard to price a "Credits" system when costs vary by 100x.
