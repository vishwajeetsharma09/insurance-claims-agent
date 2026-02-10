# Insurance Claims Processing Agent

An autonomous AI-powered system for processing First Notice of Loss (FNOL) insurance claim documents. This system uses Large Language Models (LLMs) to extract claim information, validate mandatory fields, route claims based on business rules, and generate reasoning explanations.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
│                      (app/main.py)                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Document Parser                            │
│                  (app/parser.py)                             │
│  • PDF parsing (pdfplumber)                                 │
│  • TXT parsing (native)                                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              LLM Field Extractor                             │
│              (app/extractor_llm.py)                          │
│  • Google Gemini 2.5 Flash                                  │
│  • Structured JSON extraction                                │
│  • Temperature: 0.0                                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Validator                                   │
│                  (app/validator.py)                          │
│  • Pydantic model validation                                 │
│  • Mandatory field checking                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Router                                      │
│                  (app/router.py)                              │
│  • Business rules engine                                     │
│  • Route determination                                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Reasoning LLM                                   │
│              (app/reasoning_llm.py)                          │
│  • Google Gemini 2.5 Flash                                  │
│  • Explanation generation                                    │
│  • Temperature: 0.2                                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  JSON Response                               │
│  • Extracted fields                                          │
│  • Missing fields                                            │
│  • Recommended route                                         │
│  • Reasoning                                                 │
└─────────────────────────────────────────────────────────────┘
```

## Features

- **LLM-Based Extraction**: Uses Google Gemini 2.5 Flash for intelligent field extraction from unstructured documents
- **Multi-Format Support**: Processes both PDF and TXT documents
- **Business Rules Engine**: Implements routing logic based on claim characteristics
- **Validation**: Pydantic-based validation with mandatory field checking
- **Reasoning Generation**: AI-generated explanations for routing decisions
- **Production-Ready**: Error handling, logging, retry logic, and type hints

## Business Rules

The system routes claims based on the following rules (evaluated in order):

1. **Fast-track**: If estimated damage < $25,000
2. **Manual review**: If any mandatory field is missing
3. **Investigation Flag**: If description contains keywords: "fraud", "inconsistent", or "staged"
4. **Specialist Queue**: If claim type = "injury"
5. **Standard Processing**: Default route for all other claims

## Mandatory Fields

The following fields are required for claim processing:

- `policy_information.policy_number`
- `policy_information.policyholder_name`
- `incident_information.date`
- `incident_information.location`
- `incident_information.description`
- `involved_parties.claimant`
- `asset_details.estimated_damage`
- `claim_type`

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- Google Gemini API key

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd insurance-claims-agent
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your Google Gemini API key
   # GEMINI_API_KEY=your-actual-api-key-here
   ```

## Running the Application

### Development Server

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Production Server

For production, use:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Usage

### Endpoint: `POST /process-claim`

Process an insurance claim document.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: File upload (PDF or TXT)

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/process-claim" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_docs/claim_example.pdf"
```

**Example using Python requests:**
```python
import requests

url = "http://localhost:8000/process-claim"
with open("sample_docs/claim_example.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files)
    print(response.json())
```

**Response Format:**
```json
{
  "extractedFields": {
    "policy_information": {
      "policy_number": "POL-123456",
      "policyholder_name": "John Doe",
      "effective_dates": "2024-01-01 to 2025-01-01"
    },
    "incident_information": {
      "date": "2024-03-15",
      "time": "14:30",
      "location": "123 Main St, City, State",
      "description": "Vehicle collision at intersection"
    },
    "involved_parties": {
      "claimant": "John Doe",
      "third_parties": ["Jane Smith"],
      "contact_details": "john.doe@email.com, 555-1234"
    },
    "asset_details": {
      "asset_type": "Vehicle",
      "asset_id": "VIN-ABC123",
      "estimated_damage": 15000.0
    },
    "claim_type": "auto",
    "attachments": ["photo1.jpg", "photo2.jpg"],
    "initial_estimate": 15000.0
  },
  "missingFields": [],
  "recommendedRoute": "Fast-track",
  "reasoning": "Claim routed to Fast-track due to estimated damage of $15,000 being below the $25,000 threshold. All mandatory fields are present and no suspicious indicators were detected."
}
```

## Project Structure

```
insurance-claims-agent/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── parser.py             # Document parsing (PDF/TXT)
│   ├── extractor_llm.py      # LLM-based field extraction
│   ├── validator.py          # Field validation
│   ├── router.py             # Business rules routing
│   ├── reasoning_llm.py      # Reasoning generation
│   └── models.py             # Pydantic models
├── sample_docs/              # Sample claim documents
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── .env.example              # Environment variables template
```

## Design Decisions

### LLM-Based Extraction
- **Why**: Insurance claim documents are highly unstructured and variable in format. LLMs excel at understanding context and extracting information from natural language, making them superior to regex-based approaches.
- **Model Choice**: Google Gemini 2.5 Flash provides excellent performance at a lower cost compared to larger models, suitable for production use.

### Temperature Settings
- **Extraction (0.0)**: Deterministic extraction ensures consistent field extraction results.
- **Reasoning (0.2)**: Slight creativity allows for natural-sounding explanations while maintaining consistency.

### Pydantic Models
- **Why**: Provides automatic validation, type safety, and clear data structures. Ensures data integrity throughout the processing pipeline.

### Business Rules Order
- **Why**: Rules are evaluated in priority order. Missing fields and fraud indicators take precedence over damage thresholds to ensure proper handling of critical cases.

### Retry Logic
- **Why**: LLM API calls can occasionally fail. Retry logic with exponential backoff ensures robustness in production environments.

## Future Improvements

1. **Multi-Document Support**: Process multiple related documents in a single claim
2. **Caching**: Cache LLM responses for similar documents to reduce API costs
3. **Database Integration**: Store processed claims in a database for tracking and analytics
4. **Webhook Support**: Send notifications when claims are processed
5. **Batch Processing**: Process multiple claims in parallel
6. **Custom Model Fine-tuning**: Fine-tune models on domain-specific claim data
7. **Enhanced Validation**: Add more sophisticated validation rules (date formats, policy number patterns)
8. **Monitoring & Metrics**: Add Prometheus metrics and distributed tracing
9. **Rate Limiting**: Implement rate limiting for API endpoints
10. **Authentication**: Add API key or OAuth authentication
11. **Document OCR**: Support for scanned PDFs using OCR
12. **Multi-language Support**: Process claims in multiple languages

## Error Handling

The system handles various error scenarios:

- **Invalid file types**: Returns 400 error with clear message
- **Empty documents**: Validates document content before processing
- **LLM API failures**: Retries up to 3 times with fallback reasoning
- **Parsing errors**: Provides detailed error messages
- **Validation errors**: Returns missing fields in response

## Logging

The application uses Python's standard logging module with INFO level by default. Logs include:
- Document processing steps
- LLM API calls and responses
- Routing decisions
- Error conditions

## License

This project is provided as-is for demonstration purposes.

## Support

For issues or questions, please check the logs for detailed error messages and ensure:
1. Google Gemini API key is correctly configured
2. Python version is 3.11+
3. All dependencies are installed
4. File format is supported (PDF or TXT)

