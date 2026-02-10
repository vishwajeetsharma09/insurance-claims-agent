"""
FastAPI main application for insurance claims processing.
"""
import logging
import tempfile
from pathlib import Path
from typing import Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from app.parser import DocumentParser
from app.extractor_llm import LLMExtractor
from app.validator import ClaimValidator
from app.router import ClaimRouter
from app.reasoning_llm import ReasoningLLM
from app.models import ProcessedClaimResponse
from app.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format=settings.log_format
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.api_title,
    description="Autonomous agent for processing FNOL (First Notice of Loss) documents",
    version=settings.api_version
)

# Initialize components
parser = DocumentParser()
extractor = LLMExtractor()
validator = ClaimValidator()
router = ClaimRouter()
reasoning_llm = ReasoningLLM()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Insurance Claims Processing Agent API",
        "version": "1.0.0",
        "endpoints": {
            "POST /process-claim": "Process a claim document (PDF or TXT)"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/process-claim", response_model=ProcessedClaimResponse)
async def process_claim(file: UploadFile = File(...)):
    """
    Process an insurance claim document.
    
    Accepts PDF or TXT files, extracts fields using LLM, validates,
    routes based on business rules, and returns structured JSON response.
    
    Args:
        file: Uploaded document file (PDF or TXT)
        
    Returns:
        ProcessedClaimResponse with extracted fields, missing fields,
        recommended route, and reasoning
        
    Raises:
        HTTPException: For file processing errors
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ['.pdf', '.txt']:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_extension}. Supported types: .pdf, .txt"
        )
    
    # Save uploaded file temporarily
    temp_file = None
    try:
        # Create temporary file
        suffix = file_extension
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            temp_file = Path(tmp.name)
        
        logger.info(f"Processing file: {file.filename} ({len(content)} bytes)")
        
        # Step 1: Parse document
        try:
            document_text = parser.parse(temp_file)
            if not document_text or len(document_text.strip()) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="Document appears to be empty or could not extract text"
                )
        except Exception as e:
            logger.error(f"Document parsing error: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to parse document: {str(e)}")
        
        # Step 2: Extract fields using LLM
        try:
            extracted_data = extractor.extract_fields(document_text)
            logger.info("Field extraction completed")
        except Exception as e:
            logger.error(f"LLM extraction error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to extract fields from document: {str(e)}"
            )
        
        # Step 3: Validate and check for missing fields
        try:
            claim_data, missing_fields = validator.validate(extracted_data)
            logger.info(f"Validation completed. Missing fields: {len(missing_fields)}")
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to validate extracted data: {str(e)}"
            )
        
        # Step 4: Route claim based on business rules
        try:
            recommended_route = router.route_claim(claim_data, missing_fields)
            logger.info(f"Routing decision: {recommended_route}")
        except Exception as e:
            logger.error(f"Routing error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to route claim: {str(e)}"
            )
        
        # Step 5: Generate reasoning using LLM
        try:
            reasoning = reasoning_llm.generate_reasoning(
                claim_data,
                missing_fields,
                recommended_route
            )
            logger.info("Reasoning generated")
        except Exception as e:
            logger.error(f"Reasoning generation error: {str(e)}")
            # Use fallback reasoning if LLM fails
            reasoning = f"Claim processed and routed to {recommended_route}."
        
        # Step 6: Format response
        # Convert ClaimData to dictionary for JSON response
        extracted_fields_dict = claim_data.model_dump(exclude_none=True)
        
        response = ProcessedClaimResponse(
            extractedFields=extracted_fields_dict,
            missingFields=missing_fields,
            recommendedRoute=recommended_route,
            reasoning=reasoning
        )
        
        logger.info(f"Claim processing completed successfully. Route: {recommended_route}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing claim: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if temp_file and temp_file.exists():
            try:
                temp_file.unlink()
                logger.debug(f"Cleaned up temporary file: {temp_file}")
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {temp_file}: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)

