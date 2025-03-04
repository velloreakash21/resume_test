import os
import json
import sys
sys.path.insert(0, os.path.dirname(__file__))
from typing import List, Optional
from fastapi import FastAPI, File, Form, UploadFile, Header, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import logging
import time
from starlette.requests import Request
from starlette.responses import Response

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.DEBUG)

# Initialize FastAPI
app = FastAPI(
    title="Resume Ranking API",
    description="An API to extract job criteria and score resumes based on job descriptions",
    version="1.0.0"
)

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger = logging.getLogger("uvicorn.access")
    logger.debug(f"New request: {request.method} {request.url}")
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    logger.debug(f"Completed {request.method} {request.url} in {process_time:.2f}ms with status {response.status_code}")
    return response

# Import utilities after app initialization to avoid circular import issues
from resume_ranking_api.utils.file_utils import extract_text_from_file, extract_candidate_name
from resume_ranking_api.utils.openai_utils import extract_criteria
from resume_ranking_api.utils.scoring import analyze_resume_with_criteria, generate_csv_report

# Define response models
class CriteriaResponse(BaseModel):
    criteria: List[str]

# Get the API password from environment variables
API_PASSWORD = os.getenv("API_PASSWORD")
if not API_PASSWORD:
    print("WARNING: API_PASSWORD is not set in .env file. Using default password.")
    API_PASSWORD = "default_password"

@app.post(
    "/extract-criteria",
    response_model=CriteriaResponse,
    summary="Extract ranking criteria from job description",
    description="Upload a job description (PDF or DOCX) and extract key ranking criteria using GPT-4o."
)
async def extract_criteria_endpoint(
    file: UploadFile = File(...),
    openai_key: Optional[str] = Form(None, description="OpenAI API key provided from frontend")
):
    """
    Extract ranking criteria from a job description file.
    - **file**: Upload a job description in PDF or DOCX format.
    Returns a JSON object with extracted criteria as a list of strings.
    """
    # Extract text from the uploaded file
    job_description_text = await extract_text_from_file(file)
    # Extract criteria using OpenAI
    criteria_list = extract_criteria(job_description_text)
    return CriteriaResponse(criteria=criteria_list)

@app.post(
    "/score-resumes",
    summary="Score resumes against criteria",
    description="Upload multiple resumes and score them against the provided criteria. Returns a CSV file with scores."
)
async def score_resumes_endpoint(
    background_tasks: BackgroundTasks,
    criteria: str = Form(..., description="JSON array of criteria strings"),
    files: List[UploadFile] = File(..., description="Multiple resume files (PDF or DOCX)"),
    x_api_key: Optional[str] = Header(None, description="API password for authentication")
):
    """
    Score multiple resumes against the provided criteria.
    - **criteria**: JSON array of criteria strings (e.g., ["Python", "FastAPI"])
    - **files**: Upload multiple resume files in PDF or DOCX format.
    - **x_api_key**: API password in header for authentication.
    Returns a CSV file with candidate names, individual scores, and total scores.
    """
    # Check authentication
    if x_api_key != API_PASSWORD:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized. Invalid or missing API key."
        )
    
    logger = logging.getLogger(__name__)
    logger.debug(f"Raw criteria received: {criteria}")
    try:
        parsed = json.loads(criteria)
        if isinstance(parsed, list):
            criteria_list = parsed
        elif isinstance(parsed, dict) and "criteria" in parsed:
            criteria_list = parsed["criteria"]
        else:
            raise ValueError("Criteria must be a list or an object containing a 'criteria' key")
        logger.debug(f"Parsed criteria: {criteria_list}")
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON format for criteria. Please provide a valid JSON array or object."
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
    if not files:
        raise HTTPException(
            status_code=400,
            detail="No resume files uploaded."
        )
    
    results = []
    for file in files:
        resume_text = await extract_text_from_file(file)
        candidate_name = extract_candidate_name(resume_text)
        if candidate_name == "Unknown Candidate":
            candidate_name = os.path.splitext(file.filename)[0]
        
        # Analyze resume with criteria using OpenAI
        scores = analyze_resume_with_criteria(resume_text, criteria_list)
        
        # Store the results
        results.append({
            "name": candidate_name,
            "scores": scores
        })
    
    # Generate CSV report
    csv_path = generate_csv_report(results, criteria_list)
    background_tasks.add_task(lambda: os.unlink(csv_path))
    return FileResponse(
        path=csv_path,
        filename="resume_scores.csv",
        media_type="text/csv",
        background=background_tasks
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
