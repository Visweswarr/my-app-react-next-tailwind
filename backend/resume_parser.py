import sys
import json
import re
from typing import Dict, List
import random  # For demo purposes
import PyPDF2

def extract_text_from_file(file_path: str) -> str:
    """Extract text from PDF or TXT file."""
    if file_path.endswith('.pdf'):
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(json.dumps({"error": f"Failed to read PDF file: {str(e)}"}))
            sys.exit(1)
    else:
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except Exception as e:
            print(json.dumps({"error": f"Failed to read file: {str(e)}"}))
            sys.exit(1)

def extract_information(text: str) -> Dict:
    """Extract relevant information from resume text."""
    # Basic regex-based extraction for demo purposes
    name_match = re.search(r"Name[:\s]+([A-Za-z ]+)", text, re.IGNORECASE)
    email_match = re.search(r"([\w\.-]+@[\w\.-]+)", text)
    education_match = re.search(r"(Bachelor|Master|PhD|Diploma|Degree)[^\n]*", text, re.IGNORECASE)
    experience_match = re.search(r"(\d+)\s+years?", text, re.IGNORECASE)
    skills_match = re.findall(r"Skills?[:\s]+([A-Za-z, ]+)", text, re.IGNORECASE)

    name = name_match.group(1).strip() if name_match else "John Doe"
    email = email_match.group(1).strip() if email_match else "john.doe@example.com"
    education = education_match.group(0).strip() if education_match else "Bachelor's in Computer Science"
    experience = int(experience_match.group(1)) if experience_match else 5
    skills = []
    if skills_match:
        skills = [skill.strip() for skill in skills_match[0].split(',')]
    else:
        skills = ["Python", "JavaScript", "React", "Node.js", "Machine Learning"]

    return {
        "id": f"resume_{random.randint(1000, 9999)}",
        "name": name,
        "email": email,
        "education": education,
        "experience": experience,
        "skills": skills
    }

def calculate_score(resume_info: Dict, criteria: Dict) -> float:
    """Calculate match score based on job criteria."""
    score = 0
    max_score = 0
    
    # Skills matching
    if 'requiredSkills' in criteria and criteria['requiredSkills']:
        required_skills = [s.strip().lower() for s in criteria['requiredSkills'].split(',')]
        resume_skills = [s.lower() for s in resume_info['skills']]
        
        if required_skills:
            max_score += 50
            matched_skills = sum(1 for skill in required_skills if skill in resume_skills)
            score += (matched_skills / len(required_skills)) * 50
    
    # Experience matching
    if 'minExperience' in criteria and criteria['minExperience']:
        try:
            required_exp = float(criteria['minExperience'])
            max_score += 30
            if resume_info['experience'] >= required_exp:
                score += 30
            else:
                score += (resume_info['experience'] / required_exp) * 30
        except ValueError:
            pass
    
    # Education matching
    if 'educationLevel' in criteria and criteria['educationLevel']:
        max_score += 20
        if criteria['educationLevel'].lower() in resume_info['education'].lower():
            score += 20
    
    # Return percentage score
    return round((score / max_score * 100) if max_score > 0 else 100)

def main():
    if len(sys.argv) != 3:
        print(json.dumps({"error": "Invalid arguments"}))
        sys.exit(1)
    
    file_path = sys.argv[1]
    criteria = json.loads(sys.argv[2])
    
    try:
        # Extract text from file
        text = extract_text_from_file(file_path)
        
        # Extract information from text
        resume_info = extract_information(text)
        
        # Calculate match score
        score = calculate_score(resume_info, criteria)
        
        # Add score to resume info
        resume_info['score'] = score
        
        # Return JSON result
        print(json.dumps(resume_info))
        
    except Exception as e:
        print(json.dumps({"error": f"Failed to process resume: {str(e)}"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
