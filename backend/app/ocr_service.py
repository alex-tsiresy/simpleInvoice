import httpx
from typing import Dict, Any, Optional
from app.config import get_settings
from io import BytesIO

settings = get_settings()


class OCRService:
    """
    OCR Service - supports both RapidOCR and PaddleOCR-VL
    """
    def __init__(self):
        self.base_url = settings.paddleocr_vl_url
        self.timeout = 300.0  # 5 minutes timeout for OCR processing

    async def process_document(self, file_content: bytes, file_type: str, filename: str = "document") -> Dict[str, Any]:
        """
        Process document using OCR microservice (RapidOCR or PaddleOCR-VL)

        Args:
            file_content: Document content as bytes
            file_type: File MIME type
            filename: Original filename

        Returns:
            Dictionary containing OCR results
        """
        try:
            # Send file to OCR microservice
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                files = {
                    'file': (filename, file_content, file_type)
                }

                response = await client.post(
                    f"{self.base_url}/ocr",
                    files=files
                )

                response.raise_for_status()
                result = response.json()

                # Handle both RapidOCR and PaddleOCR-VL response formats
                # RapidOCR returns: elements, total_elements, processing_time
                # PaddleOCR-VL returns: pages, total_pages, markdown

                if "elements" in result:
                    # RapidOCR format
                    return {
                        "success": result.get("success", True),
                        "text": result.get("text", ""),
                        "markdown": "",  # RapidOCR doesn't provide markdown
                        "pages": [{"elements": result.get("elements", [])}],  # Wrap elements as single page
                        "total_pages": 1,
                        "elements": result.get("elements", []),
                        "total_elements": result.get("total_elements", 0),
                        "processing_time": result.get("processing_time", 0)
                    }
                else:
                    # PaddleOCR-VL format (backward compatibility)
                    return {
                        "success": result.get("success", True),
                        "text": result.get("text", ""),
                        "markdown": result.get("markdown", ""),
                        "pages": result.get("pages", []),
                        "total_pages": result.get("total_pages", 0)
                    }

        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "OCR service timeout",
                "text": "",
                "pages": []
            }
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"OCR service error: {e.response.status_code}",
                "text": "",
                "pages": []
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "pages": []
            }


# Singleton instance
ocr_service = OCRService()

# Backward compatibility alias
PaddleOCRService = OCRService
