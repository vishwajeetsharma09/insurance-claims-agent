"""
LLM-based reasoning generator for claim routing decisions using Google Gemini API.
"""
import logging
from typing import List
import google.generativeai as genai
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.models import ClaimData

logger = logging.getLogger(__name__)


class ReasoningLLMSettings(BaseSettings):
    """Settings for reasoning LLM."""
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
    gemini_api_key: str
    model_name: str = "gemini-2.5-flash"
    temperature: float = 0.2
    max_retries: int = 3


class ReasoningLLM:
    """Generate reasoning explanations using Google Gemini LLM."""
    
    def __init__(self):
        """Initialize reasoning LLM with settings."""
        self.settings = ReasoningLLMSettings()
        genai.configure(api_key=self.settings.gemini_api_key)
        self.model = genai.GenerativeModel(
            model_name=self.settings.model_name,
            generation_config={
                "temperature": self.settings.temperature,
                "max_output_tokens": 200
            }
        )
    
    def generate_reasoning(
        self,
        claim_data: ClaimData,
        missing_fields: List[str],
        recommended_route: str
    ) -> str:
        """
        Generate a short reasoning explanation for the routing decision.
        
        Args:
            claim_data: ClaimData model instance
            missing_fields: List of missing mandatory fields
            recommended_route: Recommended routing decision
            
        Returns:
            Short reasoning explanation string
        """
        prompt = self._build_reasoning_prompt(claim_data, missing_fields, recommended_route)
        
        for attempt in range(self.settings.max_retries):
            try:
                response = self.model.generate_content(prompt)
                reasoning = response.text.strip()
                logger.info(f"Reasoning generated successfully on attempt {attempt + 1}")
                return reasoning
                
            except Exception as e:
                logger.error(f"Reasoning generation error on attempt {attempt + 1}: {str(e)}")
                if attempt == self.settings.max_retries - 1:
                    # Fallback to basic reasoning if LLM fails
                    return self._generate_fallback_reasoning(missing_fields, recommended_route)
        
        return self._generate_fallback_reasoning(missing_fields, recommended_route)
    
    def _build_reasoning_prompt(
        self,
        claim_data: ClaimData,
        missing_fields: List[str],
        recommended_route: str
    ) -> str:
        """
        Build the reasoning prompt for the LLM.
        
        Args:
            claim_data: ClaimData model instance
            missing_fields: List of missing mandatory fields
            recommended_route: Recommended routing decision
            
        Returns:
            Formatted prompt string
        """
        system_instruction = "You are an insurance claims processing expert. Provide concise, professional reasoning explanations for claim routing decisions."
        
        # Build summary of claim data
        claim_summary = {
            "policy_number": claim_data.policy_information.policy_number if claim_data.policy_information else None,
            "claim_type": claim_data.claim_type,
            "estimated_damage": claim_data.asset_details.estimated_damage if claim_data.asset_details else None,
            "incident_date": claim_data.incident_information.date if claim_data.incident_information else None,
            "description_preview": (claim_data.incident_information.description[:200] + "...") 
                if (claim_data.incident_information and claim_data.incident_information.description) else None
        }
        
        prompt = f"""{system_instruction}

Generate a short, professional reasoning explanation (2-3 sentences) for why this insurance claim was routed to "{recommended_route}".

Claim Summary:
{claim_summary}

Missing Fields: {missing_fields if missing_fields else "None"}

Provide a concise explanation that references the specific business rules or data points that led to this routing decision."""
        
        return prompt
    
    def _generate_fallback_reasoning(self, missing_fields: List[str], recommended_route: str) -> str:
        """
        Generate a fallback reasoning if LLM fails.
        
        Args:
            missing_fields: List of missing mandatory fields
            recommended_route: Recommended routing decision
            
        Returns:
            Basic reasoning string
        """
        if missing_fields:
            return f"Claim routed to {recommended_route} due to missing mandatory fields: {', '.join(missing_fields)}."
        
        if recommended_route == "Fast-track":
            return f"Claim routed to {recommended_route} due to estimated damage below threshold."
        elif recommended_route == "Investigation Flag":
            return f"Claim routed to {recommended_route} due to suspicious keywords detected in description."
        elif recommended_route == "Specialist Queue":
            return f"Claim routed to {recommended_route} due to injury claim type requiring specialist review."
        else:
            return f"Claim routed to {recommended_route} as standard processing workflow."
