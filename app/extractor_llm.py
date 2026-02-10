"""
LLM-based field extractor using Google Gemini API.
"""
import json
import logging
from typing import Dict, Any
import google.generativeai as genai
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class LLMExtractorSettings(BaseSettings):
    """Settings for LLM extractor."""
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
    gemini_api_key: str
    model_name: str = "gemini-2.5-flash"
    temperature: float = 0.0
    max_retries: int = 3


class LLMExtractor:
    """Extract claim fields using Google Gemini LLM."""
    
    def __init__(self):
        """Initialize LLM extractor with settings."""
        self.settings = LLMExtractorSettings()
        genai.configure(api_key=self.settings.gemini_api_key)
        self.model = genai.GenerativeModel(
            model_name=self.settings.model_name,
            generation_config={
                "temperature": self.settings.temperature
            }
        )
    
    def extract_fields(self, document_text: str) -> Dict[str, Any]:
        """
        Extract claim fields from document text using LLM.
        
        Args:
            document_text: Text content from the document
            
        Returns:
            Dictionary containing extracted fields
            
        Raises:
            Exception: If extraction fails after retries
        """
        prompt = self._build_extraction_prompt(document_text)
        
        for attempt in range(self.settings.max_retries):
            try:
                response = self.model.generate_content(prompt)
                content = response.text
                logger.info(f"LLM extraction attempt {attempt + 1} successful")
                
                # Parse JSON response
                # Remove markdown code blocks if present
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                
                extracted_data = json.loads(content)
                return extracted_data
                
            except json.JSONDecodeError as e:
                logger.warning(f"LLM returned non-JSON on attempt {attempt + 1}: {str(e)}")
                if attempt == self.settings.max_retries - 1:
                    # Last attempt - try to extract JSON from response
                    try:
                        # Try to find JSON in the response
                        json_start = content.find('{')
                        json_end = content.rfind('}') + 1
                        if json_start >= 0 and json_end > json_start:
                            json_str = content[json_start:json_end]
                            extracted_data = json.loads(json_str)
                            logger.info("Successfully extracted JSON from response after cleanup")
                            return extracted_data
                    except Exception:
                        pass
                    raise Exception(f"LLM returned invalid JSON after {self.settings.max_retries} attempts")
            except Exception as e:
                logger.error(f"LLM extraction error on attempt {attempt + 1}: {str(e)}")
                if attempt == self.settings.max_retries - 1:
                    raise Exception(f"Failed to extract fields after {self.settings.max_retries} attempts: {str(e)}")
        
        raise Exception("Failed to extract fields")
    
    def _build_extraction_prompt(self, document_text: str) -> str:
        """
        Build the extraction prompt for the LLM.
        
        Args:
            document_text: Document text to extract from
            
        Returns:
            Formatted prompt string
        """
        system_instruction = "You are an expert insurance claims processor. Extract information from claim documents and return ONLY valid JSON. Do not include any explanatory text outside the JSON structure."
        
        prompt = f"""{system_instruction}

Extract the following insurance claim information from the document below. Return ONLY a JSON object with the structure shown.

Required JSON structure:
{{
  "policy_information": {{
    "policy_number": "string or null",
    "policyholder_name": "string or null",
    "effective_dates": "string or null"
  }},
  "incident_information": {{
    "date": "string or null",
    "time": "string or null",
    "location": "string or null",
    "description": "string or null"
  }},
  "involved_parties": {{
    "claimant": "string or null",
    "third_parties": ["string"] or null,
    "contact_details": "string or null"
  }},
  "asset_details": {{
    "asset_type": "string or null",
    "asset_id": "string or null",
    "estimated_damage": number or null
  }},
  "claim_type": "string or null",
  "attachments": ["string"] or null,
  "initial_estimate": number or null
}}

Document text:
{document_text}

Return ONLY the JSON object, no additional text."""
        
        return prompt
