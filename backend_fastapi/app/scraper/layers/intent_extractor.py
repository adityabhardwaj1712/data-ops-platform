"""
LAYER 4 - INTENT-BASED EXTRACTOR (THE BRAIN)

Instead of: "Find div.price"
You do: "Extract DevOps fresher jobs with these fields"

TWO MODES:
1. Heuristic Mode (NO AI, FREE, SAFE)
   - Keyword matching
   - Link patterns
   - Headings + nearby text
   - Regex fallback

2. AI-Assisted Mode (OPTIONAL)
   - LLM-powered extraction
   - More flexible
   - Protected by quality layer
"""
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
from app.scraper.llm_client import LLMClient


class ExtractionMode(str, Enum):
    HEURISTIC = "heuristic"  # Free, no AI
    AI_ASSISTED = "ai"       # LLM-powered


@dataclass
class ExtractionResult:
    """Result of intent-based extraction"""
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    field_confidence: Dict[str, float] = field(default_factory=dict)  # Per-field confidence scores
    mode_used: ExtractionMode = ExtractionMode.HEURISTIC
    confidence: float = 0.0  # Overall confidence (average of field confidences)
    fields_extracted: int = 0
    fields_expected: int = 0
    errors: List[str] = field(default_factory=list)


class IntentExtractor:
    """
    Layer 4 - Intent-Based Extractor
    
    The magic layer that extracts data based on intent, not selectors.
    
    Input:
    {
        "intent": "DevOps fresher jobs in India",
        "schema": {
            "title": "str",
            "company": "str",
            "location": "str",
            "job_link": "str"
        },
        "content": "cleaned page text"
    }
    """
    
    def __init__(self):
        self.llm_client = LLMClient()
    
    async def extract(
        self,
        content: str,
        intent: str,
        schema: Dict[str, Any],
        mode: ExtractionMode = ExtractionMode.HEURISTIC
    ) -> ExtractionResult:
        """
        Extract data based on intent and schema.
        
        Args:
            content: Cleaned markdown/text content
            intent: Natural language description of what to extract
            schema: Expected data schema
            mode: Extraction mode (heuristic or AI)
            
        Returns:
            ExtractionResult with extracted data
        """
        fields_expected = len(schema)
        
        if mode == ExtractionMode.HEURISTIC:
            # FREE mode - no AI required
            data, field_confidence, confidence = self._extract_heuristic(content, intent, schema)
        else:
            # AI-assisted mode
            data, field_confidence, confidence = await self._extract_ai(content, intent, schema)
        
        fields_extracted = len([v for v in data.values() if v])
        
        return ExtractionResult(
            success=fields_extracted > 0,
            data=data,
            field_confidence=field_confidence,
            mode_used=mode,
            confidence=confidence,
            fields_extracted=fields_extracted,
            fields_expected=fields_expected
        )
    
    def _extract_heuristic(
        self,
        content: str,
        intent: str,
        schema: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, float], float]:
        """
        Heuristic extraction - NO AI, FREE, SAFE

        Techniques:
        1. Keyword matching
        2. Pattern recognition
        3. Heading + nearby text
        4. Link extraction
        5. Regex patterns

        Returns:
            Tuple of (data, field_confidence, overall_confidence)
        """
        data = {}
        field_confidence = {}

        for field_name, field_def in schema.items():
            value, confidence = self._extract_field_heuristic(content, field_name, intent)
            data[field_name] = value
            field_confidence[field_name] = confidence

        # Calculate overall confidence as weighted average
        valid_confidences = [c for c in field_confidence.values() if c > 0]
        overall_confidence = sum(valid_confidences) / max(len(valid_confidences), 1)

        return data, field_confidence, overall_confidence
    
    def _extract_field_heuristic(
        self,
        content: str,
        field_name: str,
        intent: str
    ) -> Tuple[Optional[str], float]:
        """Extract a single field using heuristics"""
        field_lower = field_name.lower()
        
        # Strategy 1: Look for labeled values
        # e.g., "Title: Software Engineer" or "**Title:** Software Engineer"
        patterns = [
            rf'{field_name}\s*[:：]\s*([^\n]+)',
            rf'\*\*{field_name}\*\*\s*[:：]?\s*([^\n]+)',
            rf'#{1,3}\s*{field_name}\s*\n([^\n#]+)',
            rf'{field_name}\s*[-–—]\s*([^\n]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return self._clean_value(match.group(1)), 0.9  # High confidence for labeled matches
        
        # Strategy 2: Field-specific patterns
        if field_lower in ['title', 'job_title', 'position']:
            return self._extract_job_title(content)

        elif field_lower in ['company', 'company_name', 'employer']:
            return self._extract_company(content)

        elif field_lower in ['location', 'place', 'city']:
            return self._extract_location(content)

        elif field_lower in ['salary', 'pay', 'compensation']:
            return self._extract_salary(content)

        elif field_lower in ['link', 'url', 'job_link', 'apply_link']:
            return self._extract_link(content)

        elif field_lower in ['date', 'posted', 'posted_date']:
            return self._extract_date(content)

        elif field_lower in ['price', 'cost', 'amount']:
            return self._extract_price(content)

        elif field_lower in ['description', 'desc', 'summary']:
            return self._extract_description(content)

        # Strategy 3: Generic keyword matching
        return self._extract_near_keyword(content, field_name)
    
    def _extract_job_title(self, content: str) -> Optional[str]:
        """Extract job title using common patterns"""
        patterns = [
            r'#\s*([^#\n]+(?:Engineer|Developer|Manager|Analyst|Designer|Architect|Lead|Specialist)[^\n]*)',
            r'Position\s*[:：]\s*([^\n]+)',
            r'Role\s*[:：]\s*([^\n]+)',
            r'Opening\s+for\s+([^\n]+)',
            r'^([A-Z][^\n]{10,60}(?:Engineer|Developer|Manager|Analyst|Designer))$',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                return self._clean_value(match.group(1)), 0.85  # Good confidence for job title patterns
        return None, 0.0
    
    def _extract_company(self, content: str) -> Optional[str]:
        """Extract company name"""
        patterns = [
            r'Company\s*[:：]\s*([^\n]+)',
            r'at\s+([A-Z][A-Za-z0-9\s&]+(?:Inc|LLC|Ltd|Corp|Company|Technologies|Solutions)?)',
            r'Employer\s*[:：]\s*([^\n]+)',
            r'\|\s*([A-Z][A-Za-z0-9\s]+)\s*\|',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return self._clean_value(match.group(1)), 0.8  # Good confidence for company patterns
        return None, 0.0
    
    def _extract_location(self, content: str) -> Optional[str]:
        """Extract location"""
        patterns = [
            r'Location\s*[:：]\s*([^\n]+)',
            r'(?:in|at)\s+([A-Z][a-z]+(?:,\s*[A-Z]{2})?)',
            r'((?:Remote|Hybrid|On-?site)(?:\s*[-–]\s*[^\n]+)?)',
            r'([A-Z][a-z]+,\s*(?:India|USA|UK|Canada|Germany|Australia)[^\n]*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return self._clean_value(match.group(1)), 0.8  # Good confidence for company patterns
        return None, 0.0
    
    def _extract_salary(self, content: str) -> Optional[str]:
        """Extract salary information"""
        patterns = [
            r'Salary\s*[:：]\s*([^\n]+)',
            r'(?:₹|Rs\.?|INR|\$|USD|EUR|€)\s*[\d,]+(?:\s*[-–]\s*[\d,]+)?(?:\s*(?:LPA|PA|per\s+(?:year|month|annum))?)?',
            r'[\d,]+\s*(?:LPA|lakh|lakhs?)\s*(?:per\s*(?:annum|year))?',
            r'Compensation\s*[:：]\s*([^\n]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                if match.lastindex:
                    return self._clean_value(match.group(1)), 0.75  # Medium confidence for salary patterns
                return self._clean_value(match.group(0)), 0.75
        return None, 0.0
    
    def _extract_link(self, content: str) -> Optional[str]:
        """Extract URL/link"""
        patterns = [
            r'\[(?:Apply|Link|View|More)\]\((https?://[^\)]+)\)',
            r'(https?://[^\s\)\]]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1), 0.9  # High confidence for URL patterns
        return None, 0.0
    
    def _extract_date(self, content: str) -> Optional[str]:
        """Extract date"""
        patterns = [
            r'Posted\s*[:：]?\s*([^\n]+ago|[^\n]+\d{4})',
            r'Date\s*[:：]\s*([^\n]+)',
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return self._clean_value(match.group(1)), 0.8  # Good confidence for company patterns
        return None, 0.0
    
    def _extract_price(self, content: str) -> Optional[str]:
        """Extract price"""
        patterns = [
            r'Price\s*[:：]\s*([^\n]+)',
            r'(?:₹|Rs\.?|\$|€|£)\s*[\d,]+(?:\.\d{2})?',
            r'[\d,]+(?:\.\d{2})?\s*(?:USD|INR|EUR|GBP)',
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                if match.lastindex:
                    return self._clean_value(match.group(1)), 0.8  # Good confidence for price patterns
                return self._clean_value(match.group(0)), 0.8
        return None, 0.0
    
    def _extract_description(self, content: str) -> Optional[str]:
        """Extract description (first paragraph)"""
        # Get first substantial paragraph
        paragraphs = content.split('\n\n')
        for p in paragraphs:
            p = p.strip()
            if len(p) > 50 and not p.startswith('#'):
                return p[:500], 0.6  # Medium confidence for description extraction
        return None, 0.0
    
    def _extract_near_keyword(
        self,
        content: str,
        keyword: str
    ) -> Optional[str]:
        """Extract text near a keyword"""
        pattern = rf'{keyword}[:\s]+([^\n]+)'
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return self._clean_value(match.group(1)), 0.5  # Lower confidence for generic keyword matching
        return None, 0.0
    
    def _clean_value(self, value: str) -> str:
        """Clean extracted value"""
        if not value:
            return ""
        
        # Remove markdown formatting
        value = re.sub(r'\*\*([^*]+)\*\*', r'\1', value)
        value = re.sub(r'\*([^*]+)\*', r'\1', value)
        value = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', value)
        
        # Remove extra whitespace
        value = re.sub(r'\s+', ' ', value)
        
        return value.strip()
    
    async def _extract_ai(
        self,
        content: str,
        intent: str,
        schema: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, float], float]:
        """
        AI-assisted extraction using LLM.
        Protected by quality layer, so AI errors are safe.
        """
        data, field_confidence, overall_confidence = await self.llm_client.extract_with_field_confidence(
            content=content,
            prompt=intent,
            schema=schema
        )

        return data or {}, field_confidence or {}, overall_confidence
    
    async def extract_multiple(
        self,
        content: str,
        intent: str,
        schema: Dict[str, Any],
        mode: ExtractionMode = ExtractionMode.HEURISTIC
    ) -> List[Dict[str, Any]]:
        """
        Extract multiple items (e.g., list of jobs, products).
        """
        # Split content into potential items
        items = self._split_into_items(content)
        
        results = []
        for item in items:
            result = await self.extract(item, intent, schema, mode)
            if result.success and result.confidence > 0.3:
                results.append(result.data)
        
        return results
    
    def _split_into_items(self, content: str) -> List[str]:
        """Split content into individual items"""
        # Try to split by horizontal rules
        if '---' in content:
            return [s.strip() for s in content.split('---') if s.strip()]
        
        # Try to split by numbered items
        items = re.split(r'\n\d+\.\s+', content)
        if len(items) > 1:
            return [s.strip() for s in items if s.strip()]
        
        # Try to split by headers
        items = re.split(r'\n##?\s+', content)
        if len(items) > 1:
            return [s.strip() for s in items if s.strip()]
        
        # Return as single item
        return [content]
