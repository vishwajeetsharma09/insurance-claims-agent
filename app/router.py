"""
Business rules router for claim routing decisions.
"""
import logging
from typing import List
from app.models import ClaimData

logger = logging.getLogger(__name__)


class ClaimRouter:
    """Route claims based on business rules."""
    
    # Keywords that trigger investigation flag
    INVESTIGATION_KEYWORDS = ["fraud", "inconsistent", "staged"]
    
    # Damage threshold for fast-track
    FAST_TRACK_THRESHOLD = 25000
    
    @staticmethod
    def route_claim(claim_data: ClaimData, missing_fields: List[str]) -> str:
        """
        Determine claim routing based on business rules.
        
        Business Rules:
        1. If estimated damage < 25000 → Fast-track
        2. If any mandatory field is missing → Manual review
        3. If description contains keywords (fraud, inconsistent, staged) → Investigation Flag
        4. If claim type = injury → Specialist Queue
        5. Otherwise → Standard Processing
        
        Args:
            claim_data: ClaimData model instance
            missing_fields: List of missing mandatory field paths
            
        Returns:
            Recommended route string
        """
        # Rule 2: Check for missing mandatory fields
        if missing_fields:
            logger.info(f"Routing to Manual review due to missing fields: {missing_fields}")
            return "Manual review"
        
        # Rule 3: Check for investigation keywords in description
        description = ""
        if claim_data.incident_information and claim_data.incident_information.description:
            description = claim_data.incident_information.description.lower()
        
        for keyword in ClaimRouter.INVESTIGATION_KEYWORDS:
            if keyword in description:
                logger.info(f"Routing to Investigation Flag due to keyword: {keyword}")
                return "Investigation Flag"
        
        # Rule 4: Check for injury claim type
        if claim_data.claim_type and claim_data.claim_type.lower() == "injury":
            logger.info("Routing to Specialist Queue due to injury claim type")
            return "Specialist Queue"
        
        # Rule 1: Check estimated damage for fast-track
        estimated_damage = None
        if claim_data.asset_details and claim_data.asset_details.estimated_damage is not None:
            estimated_damage = claim_data.asset_details.estimated_damage
        
        if estimated_damage is not None and estimated_damage < ClaimRouter.FAST_TRACK_THRESHOLD:
            logger.info(f"Routing to Fast-track due to damage < {ClaimRouter.FAST_TRACK_THRESHOLD}")
            return "Fast-track"
        
        # Rule 5: Default to standard processing
        logger.info("Routing to Standard Processing")
        return "Standard Processing"

