import os
import json
import re
from typing import List
from fastapi import HTTPException
import openai
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from the .env file located in the parent directory of utils
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

def extract_criteria(job_description: str) -> List[str]:
    """
    Use OpenAI GPT-4o to extract key criteria from a job description.
    Reads the OpenAI API key from the .env file.
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured in .env file."
        )
    try:
        prompt = f"""
You are an expert recruiter analyzing job descriptions. 
Extract the key ranking criteria from the following job description.
These should include required skills, certifications, experience levels, and qualifications.

Format your response as a JSON list of strings, with each string representing one criterion.
Be specific and concise. Do not include explanations, only the JSON list.

Job Description:
{job_description}
"""
        # Instantiate a new OpenAI client using the key from .env
        client = OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        
        if not response.choices or not hasattr(response.choices[0].message, "content"):
            raise HTTPException(
                status_code=500,
                detail="No valid response received from OpenAI API."
            )
        
        content = response.choices[0].message.content.strip()
        try:
            criteria_list = json.loads(content)
            if isinstance(criteria_list, list):
                return criteria_list
            else:
                raise ValueError("Response is not a valid list")
        except json.JSONDecodeError:
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                try:
                    criteria_list = json.loads(match.group(0))
                    if isinstance(criteria_list, list):
                        return criteria_list
                except Exception:
                    pass
            # Fallback: split by newlines and clean up
            criteria = []
            for line in content.split('\n'):
                line = line.strip()
                if line and not (line.startswith('[') or line.startswith(']')):
                    cleaned = re.sub(r'^[0-9]+[\.\)]\s*|^[-*•]\s*|^"+', '', line).strip()
                    if cleaned and cleaned not in criteria:
                        criteria.append(cleaned)
            if criteria:
                return criteria
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to extract criteria from the OpenAI API response."
                )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calling OpenAI API: {str(e)}"
        )
