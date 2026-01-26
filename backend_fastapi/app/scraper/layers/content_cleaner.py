"""
LAYER 3 - CONTENT CLEANER (MOST IMPORTANT)

Raw HTML is garbage.
This layer cleans it to extract meaningful content.

What it does:
- Removes ads
- Removes navbars
- Removes scripts
- Keeps only meaningful content

Output:
Clean readable text (markdown / plain text)

Benefits:
- Reduces data size by ~80%
- Makes extraction reliable
- Avoids layout dependency
"""
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import re
import trafilatura
from bs4 import BeautifulSoup


@dataclass
class CleanedContent:
    """Result of content cleaning"""
    success: bool
    markdown: str = ""
    plain_text: str = ""
    title: str = ""
    metadata: Dict[str, Any] = None
    
    # Statistics
    original_size: int = 0
    cleaned_size: int = 0
    reduction_percent: float = 0.0
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ContentCleaner:
    """
    Layer 3 - Content Cleaner
    
    Transforms garbage HTML into clean, meaningful content.
    This is THE MOST IMPORTANT layer for reliable extraction.
    
    Tools used (all FREE):
    - trafilatura (best for main content)
    - BeautifulSoup (for targeted cleaning)
    """
    
    # Elements to remove (noise)
    NOISE_TAGS = [
        'script', 'style', 'noscript', 'iframe',
        'nav', 'header', 'footer', 'aside',
        'form', 'button', 'input', 'select',
        'svg', 'canvas', 'video', 'audio',
        'advertisement', 'ad', 'ads', 'banner',
        'cookie-banner', 'popup', 'modal',
        'social-share', 'comments', 'sidebar'
    ]
    
    # Classes to remove (common ad/noise patterns)
    NOISE_CLASSES = [
        'ad', 'ads', 'advert', 'advertisement', 'banner',
        'sidebar', 'widget', 'social', 'share', 'follow',
        'newsletter', 'subscribe', 'popup', 'modal', 'overlay',
        'cookie', 'gdpr', 'consent', 'footer', 'header',
        'nav', 'navigation', 'menu', 'breadcrumb', 'related',
        'recommended', 'trending', 'popular', 'sponsored'
    ]
    
    def clean(self, html: str) -> CleanedContent:
        """
        Clean raw HTML and extract meaningful content.
        
        Args:
            html: Raw HTML string
            
        Returns:
            CleanedContent with markdown and plain text
        """
        original_size = len(html)
        
        if not html:
            return CleanedContent(success=False, original_size=0)
        
        # Step 1: Pre-clean with BeautifulSoup (remove obvious noise)
        html = self._pre_clean(html)
        
        # Step 2: Extract main content with trafilatura (BEST tool)
        markdown = self._extract_with_trafilatura(html)
        
        # Step 3: If trafilatura fails, fallback to manual extraction
        if not markdown:
            markdown = self._fallback_extraction(html)
        
        # Step 4: Post-process markdown
        markdown = self._post_process(markdown)
        
        # Step 5: Generate plain text version
        plain_text = self._markdown_to_text(markdown)
        
        # Step 6: Extract title
        title = self._extract_title(html)
        
        cleaned_size = len(markdown)
        reduction = ((original_size - cleaned_size) / max(original_size, 1)) * 100
        
        return CleanedContent(
            success=bool(markdown),
            markdown=markdown,
            plain_text=plain_text,
            title=title,
            original_size=original_size,
            cleaned_size=cleaned_size,
            reduction_percent=round(reduction, 1),
            metadata={
                "method": "trafilatura" if markdown else "fallback"
            }
        )
    
    def _pre_clean(self, html: str) -> str:
        """Remove obvious noise before main extraction"""
        soup = BeautifulSoup(html, 'lxml')
        
        # Remove noise tags
        for tag in self.NOISE_TAGS:
            for element in soup.find_all(tag):
                element.decompose()
        
        # Remove elements with noise classes
        for class_name in self.NOISE_CLASSES:
            for element in soup.find_all(class_=re.compile(class_name, re.I)):
                element.decompose()
        
        # Remove hidden elements
        for element in soup.find_all(style=re.compile(r'display:\s*none', re.I)):
            element.decompose()
        
        # Remove empty elements
        for element in soup.find_all():
            if not element.get_text(strip=True) and not element.find_all(['img', 'video', 'audio']):
                if element.name not in ['br', 'hr']:
                    element.decompose()
        
        return str(soup)
    
    def _extract_with_trafilatura(self, html: str) -> str:
        """Use trafilatura for main content extraction (BEST tool)"""
        try:
            markdown = trafilatura.extract(
                html,
                output_format="markdown",
                include_links=True,
                include_tables=True,
                include_images=False,
                include_formatting=True,
                no_fallback=False
            )
            return markdown or ""
        except Exception:
            return ""
    
    def _fallback_extraction(self, html: str) -> str:
        """Fallback extraction if trafilatura fails"""
        soup = BeautifulSoup(html, 'lxml')
        
        # Try to find main content area
        main_content = (
            soup.find('main') or
            soup.find('article') or
            soup.find('div', class_=re.compile(r'content|main|body', re.I)) or
            soup.find('div', id=re.compile(r'content|main|body', re.I)) or
            soup.body
        )
        
        if not main_content:
            return ""
        
        # Extract text with structure
        lines = []
        for element in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'li', 'td', 'th']):
            text = element.get_text(strip=True)
            if text:
                if element.name.startswith('h'):
                    level = int(element.name[1])
                    lines.append(f"{'#' * level} {text}")
                elif element.name == 'li':
                    lines.append(f"- {text}")
                else:
                    lines.append(text)
        
        return "\n\n".join(lines)
    
    def _post_process(self, markdown: str) -> str:
        """Clean up the extracted markdown"""
        if not markdown:
            return ""
        
        # Remove excessive whitespace
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)
        markdown = re.sub(r' {2,}', ' ', markdown)
        
        # Remove very short lines (likely noise)
        lines = markdown.split('\n')
        lines = [l for l in lines if len(l.strip()) > 2 or l.strip() == '']
        markdown = '\n'.join(lines)
        
        # Remove common noise phrases
        noise_phrases = [
            r'Accept cookies?',
            r'We use cookies',
            r'Subscribe to our newsletter',
            r'Sign up for free',
            r'Follow us on',
            r'Share this',
            r'Read more',
            r'Loading...',
            r'Advertisement',
        ]
        for phrase in noise_phrases:
            markdown = re.sub(phrase, '', markdown, flags=re.I)
        
        return markdown.strip()
    
    def _markdown_to_text(self, markdown: str) -> str:
        """Convert markdown to plain text"""
        if not markdown:
            return ""
        
        # Remove markdown formatting
        text = re.sub(r'#+\s*', '', markdown)  # Headers
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)  # Italic
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Links
        text = re.sub(r'`([^`]+)`', r'\1', text)  # Code
        text = re.sub(r'^[-*]\s*', '', text, flags=re.M)  # List items
        
        return text.strip()
    
    def _extract_title(self, html: str) -> str:
        """Extract page title"""
        soup = BeautifulSoup(html, 'lxml')
        
        # Try various title sources
        title = (
            soup.find('h1') or
            soup.find('title') or
            soup.find('meta', property='og:title') or
            soup.find('meta', attrs={'name': 'title'})
        )
        
        if title:
            if title.name == 'meta':
                return title.get('content', '')
            return title.get_text(strip=True)
        
        return ""
    
    def extract_structured_sections(self, markdown: str) -> List[Dict[str, str]]:
        """
        Extract structured sections from markdown.
        Useful for job listings, product pages, etc.
        """
        sections = []
        current_section = {"heading": "", "content": ""}
        
        for line in markdown.split('\n'):
            if line.startswith('#'):
                if current_section["content"]:
                    sections.append(current_section)
                heading = re.sub(r'^#+\s*', '', line)
                current_section = {"heading": heading, "content": ""}
            else:
                current_section["content"] += line + "\n"
        
        if current_section["content"]:
            sections.append(current_section)
        
        return sections
