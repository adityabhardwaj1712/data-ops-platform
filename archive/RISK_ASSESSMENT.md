# Risk & Liability Review
*Internal assessment of legal and ethical risks.*

## 1. Legal Risks
- **ToS Violation**: Scraping sites with "No Scraping" in ToS is a civil contract violation (Computer Fraud and Abuse Act vs. hiQ Labs).
  - *Mitigation*: We only scrape Public Data. No logins. No PII.
- **Copyright**: Storing copyrighted content (images/articles) is risky.
  - *Mitigation*: We extract "Facts" (Prices, Titles, Counts), which are generally not copyrightable (Feist Publications v. Rural Telephone).

## 2. Ethical Risks
- **Server Load**: Aggressive scraping can DDOS a small site.
  - *Mitigation*: `CAPACITY_LIMITS.md` enforces polite throttling (max 2 req/sec).
- **Competitor Intelligence**: Clients may ask for competitor pricing.
  - *Mitigation*: Standard business practice, but we do not engage in "Corporate Espionage" (stealing trade secrets).

## 3. Liability Shield
- **Client Agreement**: Clients must indemnify us against claims arising from *their* requested targets.
- **Output Disclaimer**: "Data provided AS IS. No guarantee of accuracy."

## 4. Red Lines (We refuse these jobs)
- Personal Identifiable Information (PII) for marketing spam.
- Behind-login content (Facebook, LinkedIn, Instagram).
- Government/Military infrastructure.
