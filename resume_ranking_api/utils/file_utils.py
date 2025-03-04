import os
import tempfile
from typing import Tuple
from fastapi import UploadFile, HTTPException
import PyPDF2
from docx import Document

async def extract_text_from_file(file: UploadFile) -> str:
    """Extract text from uploaded PDF or DOCX file"""
    
    # Check file extension
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in ['.pdf', '.docx']:
        raise HTTPException(
            status_code=415, 
            detail="Unsupported file format. Please upload PDF or DOCX files only."
        )
    
    # Create a temporary file to store the uploaded file
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    try:
        # Write uploaded file to temporary file
        content = await file.read()
        temp_file.write(content)
        temp_file.close()
        
        # Extract text based on file type
        if file_extension == '.pdf':
            return extract_text_from_pdf(temp_file.name)
        elif file_extension == '.docx':
            return extract_text_from_docx(temp_file.name)
    
    finally:
        # Clean up the temporary file
        os.unlink(temp_file.name)

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file"""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text() + "\n"
        return text
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Failed to extract text from PDF: {str(e)}"
        )

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from a DOCX file"""
    text = ""
    try:
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Failed to extract text from DOCX: {str(e)}"
        )

def extract_candidate_name(text: str) -> str:
    """Attempt to extract candidate name from resume text"""
    # Very basic implementation - in real-world, would use more sophisticated NER
    lines = text.split('\n')
    for line in lines[:10]:  # Check first 10 lines
        # Remove extra whitespace and check if line is a potential name
        clean_line = line.strip()
        if clean_line and len(clean_line.split()) <= 4 and len(clean_line) < 40:
            return clean_line
    
    return "Unknown Candidate"  # Return default if name not found
