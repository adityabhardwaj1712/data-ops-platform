"""
OCR Scraper - Image-to-text extraction

Extracts text from images and screenshots using Tesseract OCR.
"""
import logging
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
import tempfile
import httpx

from app.scraper.logic.base import BaseScraper
from app.schemas import ScrapeResult, ScrapeFailureReason, OCRConfig

logger = logging.getLogger(__name__)


class OCRScraper(BaseScraper):
    """
    Extract text from images using Optical Character Recognition.
    """
    
    def get_name(self) -> str:
        return "ocr"
    
    def can_handle(self, url: str) -> bool:
        """Check if URL points to an image"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        return any(url.lower().endswith(ext) for ext in image_extensions)
    
    async def scrape(
        self,
        url: str,
        schema: Dict[str, Any],
        job_id: str,
        **kwargs
    ) -> ScrapeResult:
        """
        Extract text from image
        
        Args:
            url: Image URL
            schema: Not used for OCR
            job_id: Job identifier
            **kwargs: ocr_config (OCRConfig)
        """
        logger.info(f"Starting OCR extraction for {url}")
        
        ocr_config: OCRConfig = kwargs.get('ocr_config', OCRConfig())
        
        try:
            # Check dependencies
            try:
                import pytesseract
                from PIL import Image
            except ImportError:
                return self.failure(
                    reason=ScrapeFailureReason.VALIDATION_FAILED,
                    message="OCR dependencies not installed. Run: pip install pytesseract Pillow"
                )
            
            # Download image
            image_path = await self._download_image(url)
            
            # Preprocess if enabled
            if ocr_config.preprocess:
                image_path = await self._preprocess_image(image_path)
            
            # Perform OCR
            image = Image.open(image_path)
            
            # Extract text with confidence
            ocr_data = pytesseract.image_to_data(
                image,
                lang=ocr_config.language,
                output_type=pytesseract.Output.DICT
            )
            
            # Filter by confidence threshold
            extracted_text = []
            for i, conf in enumerate(ocr_data['conf']):
                if conf != -1:  # -1 means no text detected
                    confidence = int(conf) / 100.0
                    if confidence >= ocr_config.confidence_threshold:
                        text = ocr_data['text'][i]
                        if text.strip():
                            extracted_text.append({
                                "text": text,
                                "confidence": confidence,
                                "position": {
                                    "x": ocr_data['left'][i],
                                    "y": ocr_data['top'][i],
                                    "width": ocr_data['width'][i],
                                    "height": ocr_data['height'][i]
                                }
                            })
            
            # Cleanup
            Path(image_path).unlink(missing_ok=True)
            
            # Combine text
            full_text = " ".join([item['text'] for item in extracted_text])
            
            return ScrapeResult(
                success=True,
                status="success",
                data={
                    "full_text": full_text,
                    "words": extracted_text,
                    "total_words": len(extracted_text)
                },
                strategy_used=self.get_name(),
                confidence=sum(item['confidence'] for item in extracted_text) / len(extracted_text) if extracted_text else 0.0,
                metadata={
                    "image_url": url,
                    "language": ocr_config.language,
                    "preprocessed": ocr_config.preprocess
                }
            )
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}", exc_info=True)
            return self.failure(
                reason=ScrapeFailureReason.UNKNOWN,
                message=f"OCR error: {str(e)}",
                errors=[str(e)]
            )
    
    async def _download_image(self, url: str) -> str:
        """Download image to temp file"""
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            
            # Save to temp file
            suffix = Path(url).suffix or '.png'
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(response.content)
                return tmp.name
    
    async def _preprocess_image(self, image_path: str) -> str:
        """
        Preprocess image for better OCR accuracy
        - Convert to grayscale
        - Denoise
        - Increase contrast
        """
        try:
            import cv2
            import numpy as np
        except ImportError:
            logger.warning("opencv-python not installed, skipping preprocessing")
            return image_path
        
        # Read image
        img = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Increase contrast (adaptive thresholding)
        processed = cv2.adaptiveThreshold(
            denoised, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Save processed image
        processed_path = image_path.replace('.', '_processed.')
        cv2.imwrite(processed_path, processed)
        
        # Delete original
        Path(image_path).unlink(missing_ok=True)
        
        return processed_path
