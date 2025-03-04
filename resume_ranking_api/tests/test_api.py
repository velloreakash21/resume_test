import json
import os
import pytest
from fastapi.testclient import TestClient
from main import app, API_PASSWORD

client = TestClient(app)

# Sample test files paths - update these to point to actual test files
JOB_DESCRIPTION_FILE = "tests/data/sample_job_description.pdf"
RESUME_FILE_1 = "tests/data/sample_resume_1.pdf"
RESUME_FILE_2 = "tests/data/sample_resume_2.docx"

@pytest.mark.skipif(not os.path.exists(JOB_DESCRIPTION_FILE), reason="Test files not found")
def test_extract_criteria():
    """Test the criteria extraction endpoint"""
    with open(JOB_DESCRIPTION_FILE, "rb") as f:
        response = client.post(
            "/extract-criteria",
            files={"file": ("job_description.pdf", f, "application/pdf")}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "criteria" in data
    assert isinstance(data["criteria"], list)
    assert len(data["criteria"]) > 0

@pytest.mark.skipif(not os.path.exists(RESUME_FILE_1) or not os.path.exists(RESUME_FILE_2), 
                   reason="Test files not found")
def test_score_resumes():
    """Test the resume scoring endpoint"""
    criteria = ["Python", "Machine Learning", "AWS"]
    
    with open(RESUME_FILE_1, "rb") as f1, open(RESUME_FILE_2, "rb") as f2:
        response = client.post(
            "/score-resumes",
            headers={"X-API-Key": API_PASSWORD},
            data={"criteria": json.dumps(criteria)},
            files=[
                ("files", ("resume1.pdf", f1, "application/pdf")),
                ("files", ("resume2.docx", f2, "application/vnd.openxmlformats-officedocument.wordprocessingml.document"))
            ]
        )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment" in response.headers["content-disposition"]

def test_score_resumes_unauthorized():
    """Test authentication for resume scoring endpoint"""
    criteria = ["Python", "Machine Learning"]
    
    response = client.post(
        "/score-resumes",
        headers={"X-API-Key": "wrong_password"},
        data={"criteria": json.dumps(criteria)},
        files=[("files", ("dummy.pdf", b"dummy content", "application/pdf"))]
    )
    
    assert response.status_code == 401
