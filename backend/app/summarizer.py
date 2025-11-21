import httpx
from typing import Dict, Any
from app.config import get_settings

settings = get_settings()


class DocumentSummarizer:
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.model = "gpt-4o-mini"  # Latest OpenAI mini model
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.timeout = 60.0  # 1 minute timeout for summarization

    async def summarize_document(self, text: str) -> Dict[str, Any]:
        """
        Generate a concise summary of document text using OpenAI GPT-4o-mini

        Args:
            text: Extracted text from document

        Returns:
            Dictionary containing summary results
        """
        try:
            # Prepare the prompt for summarization
            system_prompt = """You are a document summarization expert. Create a concise, informative summary of the given document text.

Your summary should:
- Be 2-4 sentences long
- Capture the main points and key information
- Be clear and easy to understand
- Focus on what's important

Respond with ONLY the summary text, no additional formatting or explanation."""

            user_prompt = f"Summarize this document:\n\n{text}"

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
                        "temperature": 0.3,
                        "max_tokens": 500
                    }
                )

                response.raise_for_status()
                result = response.json()

                # Extract the summary from OpenAI response
                summary = result["choices"][0]["message"]["content"].strip()

                return {
                    "success": True,
                    "summary": summary
                }

        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "OpenAI API timeout",
                "summary": ""
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
                "summary": ""
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Summarization failed: {str(e)}",
                "summary": ""
            }


# Singleton instance
summarizer = DocumentSummarizer()
