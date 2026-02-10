"""
Pydantic models for insurance claims processing.
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class PolicyInformation(BaseModel):
    """Policy information fields."""
    policy_number: Optional[str] = Field(None, description="Policy number")
    policyholder_name: Optional[str] = Field(None, description="Policyholder name")
    effective_dates: Optional[str] = Field(None, description="Policy effective dates")


class IncidentInformation(BaseModel):
    """Incident information fields."""
    date: Optional[str] = Field(None, description="Incident date")
    time: Optional[str] = Field(None, description="Incident time")
    location: Optional[str] = Field(None, description="Incident location")
    description: Optional[str] = Field(None, description="Incident description")


class InvolvedParties(BaseModel):
    """Involved parties information."""
    claimant: Optional[str] = Field(None, description="Claimant name")
    third_parties: Optional[List[str]] = Field(None, description="List of third parties")
    contact_details: Optional[str] = Field(None, description="Contact details")


class AssetDetails(BaseModel):
    """Asset details information."""
    asset_type: Optional[str] = Field(None, description="Type of asset")
    asset_id: Optional[str] = Field(None, description="Asset identifier")
    estimated_damage: Optional[float] = Field(None, description="Estimated damage amount")


class ClaimData(BaseModel):
    """Complete claim data structure."""
    policy_information: Optional[PolicyInformation] = Field(None, description="Policy information")
    incident_information: Optional[IncidentInformation] = Field(None, description="Incident information")
    involved_parties: Optional[InvolvedParties] = Field(None, description="Involved parties")
    asset_details: Optional[AssetDetails] = Field(None, description="Asset details")
    claim_type: Optional[str] = Field(None, description="Type of claim")
    attachments: Optional[List[str]] = Field(None, description="List of attachments")
    initial_estimate: Optional[float] = Field(None, description="Initial estimate amount")


class ProcessedClaimResponse(BaseModel):
    """Response model for processed claim."""
    extractedFields: dict = Field(..., description="Extracted fields from the claim")
    missingFields: List[str] = Field(..., description="List of missing mandatory fields")
    recommendedRoute: str = Field(..., description="Recommended routing for the claim")
    reasoning: str = Field(..., description="Reasoning explanation for the routing decision")

