import httpx
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from app.config import get_settings

settings = get_settings()


# Pydantic models for structured output schema
class ContactInfo(BaseModel):
    """Contact information for sender or receiver"""
    name: Optional[str] = Field(None, description="Company or person name")
    address: Optional[str] = Field(None, description="Full address")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    tax_id: Optional[str] = Field(None, description="Tax ID, VAT number, or similar")


class InvoiceData(BaseModel):
    """Structured invoice information extracted from OCR text"""
    invoice_number: Optional[str] = Field(None, description="Invoice number or ID")
    invoice_date: Optional[str] = Field(None, description="Invoice date (ISO format if possible)")
    due_date: Optional[str] = Field(None, description="Payment due date (ISO format if possible)")

    sender: ContactInfo = Field(description="Sender/vendor/from information")
    receiver: ContactInfo = Field(description="Receiver/customer/bill-to information")

    total_amount: Optional[str] = Field(None, description="Total amount including currency symbol")
    currency: Optional[str] = Field(None, description="Currency code (USD, EUR, etc.)")
    subtotal: Optional[str] = Field(None, description="Subtotal before tax")
    tax_amount: Optional[str] = Field(None, description="Tax amount")

    payment_terms: Optional[str] = Field(None, description="Payment terms or conditions")
    notes: Optional[str] = Field(None, description="Additional notes or description")


class InvoiceExtractor:
    """
    Invoice data extractor using OpenAI Structured Outputs
    """
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.model = "gpt-4o-mini-2024-07-18"  # Supports structured outputs
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.timeout = 60.0

    def get_json_schema(self) -> Dict[str, Any]:
        """Generate JSON schema from Pydantic model"""
        return {
            "name": "invoice_data",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "invoice_number": {"type": ["string", "null"]},
                    "invoice_date": {"type": ["string", "null"]},
                    "due_date": {"type": ["string", "null"]},
                    "sender": {
                        "type": "object",
                        "properties": {
                            "name": {"type": ["string", "null"]},
                            "address": {"type": ["string", "null"]},
                            "email": {"type": ["string", "null"]},
                            "phone": {"type": ["string", "null"]},
                            "tax_id": {"type": ["string", "null"]}
                        },
                        "required": ["name", "address", "email", "phone", "tax_id"],
                        "additionalProperties": False
                    },
                    "receiver": {
                        "type": "object",
                        "properties": {
                            "name": {"type": ["string", "null"]},
                            "address": {"type": ["string", "null"]},
                            "email": {"type": ["string", "null"]},
                            "phone": {"type": ["string", "null"]},
                            "tax_id": {"type": ["string", "null"]}
                        },
                        "required": ["name", "address", "email", "phone", "tax_id"],
                        "additionalProperties": False
                    },
                    "total_amount": {"type": ["string", "null"]},
                    "currency": {"type": ["string", "null"]},
                    "subtotal": {"type": ["string", "null"]},
                    "tax_amount": {"type": ["string", "null"]},
                    "payment_terms": {"type": ["string", "null"]},
                    "notes": {"type": ["string", "null"]}
                },
                "required": [
                    "invoice_number", "invoice_date", "due_date",
                    "sender", "receiver",
                    "total_amount", "currency", "subtotal", "tax_amount",
                    "payment_terms", "notes"
                ],
                "additionalProperties": False
            }
        }

    async def extract_invoice_data(self, ocr_text: str) -> Dict[str, Any]:
        """
        Extract structured invoice data from OCR text using OpenAI Structured Outputs

        Args:
            ocr_text: Extracted text from invoice OCR

        Returns:
            Dictionary containing structured invoice data or error
        """
        try:
            system_prompt = """You are an expert invoice data extraction system.
Extract structured information from invoice text with high accuracy.

IMPORTANT:
- Extract ALL available information from the invoice
- For dates, use ISO format (YYYY-MM-DD) if possible
- For amounts, include currency symbols if present
- If a field is not found in the text, set it to null
- Be precise and accurate - do not guess or make up information"""

            user_prompt = f"Extract invoice data from this OCR text:\n\n{ocr_text}"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "response_format": {
                            "type": "json_schema",
                            "json_schema": self.get_json_schema()
                        },
                        "temperature": 0.0  # Deterministic for data extraction
                    }
                )

                response.raise_for_status()
                result = response.json()

                # Extract structured data from response
                invoice_data = result["choices"][0]["message"]["content"]

                # Parse JSON string to dict
                import json
                parsed_data = json.loads(invoice_data)

                return {
                    "success": True,
                    "invoice_data": parsed_data
                }

        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "OpenAI API timeout",
                "invoice_data": None
            }
        except httpx.HTTPStatusError as e:
            error_msg = f"OpenAI API error: {e.response.status_code}"
            try:
                error_detail = e.response.json()
                error_msg += f" - {error_detail.get('error', {}).get('message', '')}"
            except:
                pass
            return {
                "success": False,
                "error": error_msg,
                "invoice_data": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Invoice extraction failed: {str(e)}",
                "invoice_data": None
            }


# Singleton instance
invoice_extractor = InvoiceExtractor()
