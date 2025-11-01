"""
Gemini LLM integration for OCR text processing
"""

import os
import google.generativeai as genai
from typing import Optional, Dict, Any
import json


class GeminiProcessor:
    """Handle text processing with Google's Gemini LLM"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model_type = os.getenv('GEMINI_MODEL_TYPE', 'gemini-2.5-flash')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_type)
    
    def process_text(
        self,
        text: str,
        prompt: Optional[str] = None,
        task: str = "analyze",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process OCR text with Gemini
        
        Args:
            text: The extracted OCR text
            prompt: Custom prompt for processing
            task: Predefined task type
            temperature: Response creativity (0.0-1.0)
            max_tokens: Maximum tokens in response
        """
        
        try:
            # Build the prompt based on task or custom prompt
            if prompt:
                full_prompt = f"{prompt}\n\nText to process:\n{text}"
            else:
                full_prompt = self._build_task_prompt(text, task)
            
            # Configure generation parameters
            generation_config = {
                "temperature": temperature,
                "top_p": 0.95,
                "top_k": 64,
            }
            
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            
            # Generate response
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            return {
                "success": True,
                "response": response.text,
                "task": task,
                "prompt_used": full_prompt,
                "usage": {
                    "prompt_tokens": len(full_prompt.split()),
                    "completion_tokens": len(response.text.split()) if response.text else 0
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "task": task,
                "response": None
            }
    
    def _build_task_prompt(self, text: str, task: str) -> str:
        """Build prompts for predefined tasks"""
        
        prompts = {
            "analyze": f"""
Analyze the following OCR-extracted text and provide insights:

1. Document type and structure
2. Key information extracted
3. Data quality assessment
4. Potential improvements needed
5. Summary of content

Text to analyze:
{text}
""",
            
            "summarize": f"""
Create a concise summary of the following OCR-extracted text. Focus on the main points and key information:

Text to summarize:
{text}
""",
            
            "structure": f"""
Structure and organize the following OCR-extracted text into a clean, readable format. Fix any OCR errors and improve formatting:

Text to structure:
{text}
""",
            
            "extract": f"""
Extract and organize key information from the following OCR text. Identify:
- Names, dates, addresses
- Important numbers, amounts, IDs
- Key facts and data points
- Contact information

Present the information in a structured format (JSON or organized list):

Text to extract from:
{text}
""",
            
            "translate": f"""
First, detect the language of the following OCR-extracted text, then translate it to English. If it's already in English, just clean up any OCR errors:

Text to translate:
{text}
""",
            
            "validate": f"""
Validate and fact-check the information in the following OCR-extracted text. Look for:
- Inconsistencies or errors
- Missing information
- Data that seems incorrect
- Suggestions for verification

Text to validate:
{text}
""",
            
            "format": f"""
Format the following OCR-extracted text into a professional document format. Clean up OCR errors, improve structure, and make it presentation-ready:

Text to format:
{text}
"""
        }
        
        return prompts.get(task, prompts["analyze"])
    
    def get_available_tasks(self) -> Dict[str, str]:
        """Get list of available predefined tasks"""
        return {
            "analyze": "Analyze document structure and content",
            "summarize": "Create a concise summary",
            "structure": "Clean and organize the text",
            "extract": "Extract key information and data",
            "translate": "Detect language and translate to English",
            "validate": "Validate and fact-check information",
            "format": "Format into professional document"
        }
    
    def test_connection(self) -> bool:
        """Test if Gemini API is working"""
        try:
            response = self.model.generate_content("Hello, this is a test.")
            return response.text is not None
        except Exception:
            return False