from openai import OpenAI
import os
from typing import List, Dict, Any
import csv
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def analyze_resume_with_criteria(resume_text: str, criteria: List[str]) -> Dict[str, int]:
    """
    Analyze a resume against a list of criteria using OpenAI.
    Returns a dictionary with criteria as keys and scores (0-5) as values.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    scores = {}

    for criterion in criteria:
        prompt = f"""
You are an expert recruiter. Analyze the following resume text against the criterion: "{criterion}".
Provide a score from 0 to 5 based on how well the resume meets the criterion.
Include a brief justification for the score.

Resume Text:
{resume_text}
"""
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            content = response.choices[0].message.content.strip()
            # Extract score and justification from the response
            score, justification = parse_score_and_justification(content)
            scores[criterion] = score
        except Exception as e:
            scores[criterion] = 0  # Default to 0 if there's an error
            print(f"Error analyzing criterion '{criterion}': {e}")

    return scores

def generate_csv_report(results: List[Dict[str, Any]], criteria_list: List[str]) -> str:
    """
    Generate a CSV report from the scoring results.
    """
    csv_filename = "resume_scores.csv"
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write header
        header = ["Candidate Name"] + criteria_list + ["Total Score"]
        writer.writerow(header)
        
        # Write data rows
        for result in results:
            name = result["name"]
            scores = result["scores"]
            total_score = sum(scores.values())
            row = [name] + [scores.get(criterion, 0) for criterion in criteria_list] + [total_score]
            writer.writerow(row)
    
    return csv_filename

def parse_score_and_justification(content: str) -> (int, str):
    """
    Parse the score and justification from the OpenAI response content.
    """
    # Example parsing logic (this will need to be adjusted based on actual response format)
    lines = content.split('\n')
    score_line = next((line for line in lines if "Score:" in line), "Score: 0")
    justification_line = next((line for line in lines if "Justification:" in line), "Justification: N/A")
    
    score = int(score_line.split(":")[1].strip())
    justification = justification_line.split(":")[1].strip()
    
    return score, justification
