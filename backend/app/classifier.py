import httpx
from typing import Dict, Any
from app.config import get_settings
from app.models import DocumentType
import json

settings = get_settings()


class DocumentClassifier:
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.model = "gpt-4o-mini"  # Latest OpenAI mini model
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.timeout = 30.0

        # Label mapping
        self.label_to_type = {
            "invoice": DocumentType.INVOICE,
            "contract": DocumentType.CONTRACT,
            "meeting_minutes": DocumentType.MEETING_MINUTES,
            "email": DocumentType.EMAIL
        }

    async def classify_document(self, text: str) -> Dict[str, Any]:
        """
        Classify document text into categories using OpenAI GPT-4o-mini

        Args:
            text: Extracted text from document

        Returns:
            Dictionary containing classification results
        """
        try:
            # Prepare the prompt for classification
            system_prompt = """You are a document classification expert. Classify the given document text into one of these categories:
1. invoice - Billing documents, receipts, invoices
2. contract - Legal agreements, terms and conditions, contracts
3. meeting_minutes - Meeting notes, minutes, summaries
4. email - Electronic correspondence, email messages

Analyze the document and respond with a JSON object containing:
- category: The document type (invoice, contract, meeting_minutes, or email)
- confidence: A confidence score between 0 and 1
- reasoning: Brief explanation for the classification

Example response:
{
  "category": "invoice",
  "confidence": 0.95,
  "reasoning": "Contains invoice number, billing details, and payment terms"
}"""

            user_prompt = f"Classify this document:\n\n{text[:2000]}"  # Limit to first 2000 chars

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
                        "response_format": {"type": "json_object"},
                        "temperature": 0.1,
                        "max_tokens": 500
                    }
                )

                response.raise_for_status()
                result = response.json()

                # Extract the classification from OpenAI response
                content = result["choices"][0]["message"]["content"]
                classification = json.loads(content)

                category = classification.get("category", "unknown")
                confidence = classification.get("confidence", 0.0)
                reasoning = classification.get("reasoning", "")

                # Map category to document type
                document_type = self.label_to_type.get(
                    category,
                    DocumentType.UNKNOWN
                )

                # Create confidence scores for all categories
                confidence_scores = {
                    "invoice": 0.0,
                    "contract": 0.0,
                    "meeting_minutes": 0.0,
                    "email": 0.0
                }
                if category in confidence_scores:
                    confidence_scores[category] = confidence
                    # Distribute remaining confidence among other categories
                    remaining = (1.0 - confidence) / 3
                    for key in confidence_scores:
                        if key != category:
                            confidence_scores[key] = remaining

                return {
                    "success": True,
                    "document_type": document_type,
                    "confidence": confidence_scores,
                    "reasoning": reasoning,
                    "predicted_label": category
                }

        except httpx.TimeoutException:
            return {~
                "success": False,
                "error": "OpenAI API timeout",
                "document_type": DocumentType.UNKNOWN,
                "confidence": {}
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
                "document_type": DocumentType.UNKNOWN,
                "confidence": {}
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Failed to parse OpenAI response: {str(e)}",
                "document_type": DocumentType.UNKNOWN,
                "confidence": {}
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Classification failed: {str(e)}",
                "document_type": DocumentType.UNKNOWN,
                "confidence": {}
            }


# Singleton instance
classifier = DocumentClassifier()
