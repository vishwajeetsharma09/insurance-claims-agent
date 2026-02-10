"""
Validator for checking mandatory fields in extracted claim data.
"""
import logging
from typing import List, Dict, Any, Tuple
from app.models import ClaimData

logger = logging.getLogger(__name__)


class ClaimValidator:
    """Validate extracted claim data and identify missing mandatory fields."""
    
    # Mandatory fields that must be present
    MANDATORY_FIELDS = [
        "policy_information.policy_number",
        "policy_information.policyholder_name",
        "incident_information.date",
        "incident_information.location",
        "incident_information.description",
        "involved_parties.claimant",
        "asset_details.estimated_damage",
        "claim_type"
    ]
    
    @staticmethod
    def validate(extracted_data: Dict[str, Any]) -> Tuple[ClaimData, List[str]]:
        """
        Validate extracted data and return structured model with missing fields.
        
        Args:
            extracted_data: Dictionary containing extracted fields from LLM
            
        Returns:
            Tuple of (ClaimData model, list of missing mandatory field paths)
        """
        try:
            # Convert extracted data to ClaimData model
            claim_data = ClaimData(**extracted_data)
        except Exception as e:
            logger.warning(f"Error parsing extracted data to model: {str(e)}")
            # Create empty model if parsing fails
            claim_data = ClaimData()
        
        missing_fields = ClaimValidator._check_mandatory_fields(claim_data)
        
        logger.info(f"Validation complete. Missing fields: {len(missing_fields)}")
        return claim_data, missing_fields
    
    @staticmethod
    def _check_mandatory_fields(claim_data: ClaimData) -> List[str]:
        """
        Check which mandatory fields are missing.
        
        Args:
            claim_data: ClaimData model instance
            
        Returns:
            List of missing mandatory field paths
        """
        missing = []
        
        # Check policy information
        if not claim_data.policy_information or not claim_data.policy_information.policy_number:
            missing.append("policy_information.policy_number")
        if not claim_data.policy_information or not claim_data.policy_information.policyholder_name:
            missing.append("policy_information.policyholder_name")
        
        # Check incident information
        if not claim_data.incident_information or not claim_data.incident_information.date:
            missing.append("incident_information.date")
        if not claim_data.incident_information or not claim_data.incident_information.location:
            missing.append("incident_information.location")
        if not claim_data.incident_information or not claim_data.incident_information.description:
            missing.append("incident_information.description")
        
        # Check involved parties
        if not claim_data.involved_parties or not claim_data.involved_parties.claimant:
            missing.append("involved_parties.claimant")
        
        # Check asset details
        if not claim_data.asset_details or claim_data.asset_details.estimated_damage is None:
            missing.append("asset_details.estimated_damage")
        
        # Check claim type
        if not claim_data.claim_type:
            missing.append("claim_type")
        
        return missing

