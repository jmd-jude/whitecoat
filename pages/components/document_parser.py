from typing import Dict, Any, Tuple
import json
from openai import OpenAI
import PyPDF2
from io import BytesIO
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client globally
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Document-specific prompts
CV_REASONING_PROMPT = """You are an expert at analyzing CVs for medical school applications.
Analyze this CV and provide your observations, uncertainties, and reasoning.
Focus on:
- Research experience and depth
- Clinical experience and patient contact hours
- Leadership roles and impact
- Skills and technical competencies
- Notable achievements or recognition
- Publication or presentation experience
- Extracurricular activities and community involvement

Provide your analysis as valid JSON with these fields:
{
    "key_observations": ["string"],
    "research_analysis": ["string"],
    "clinical_experience_notes": ["string"],
    "leadership_assessment": ["string"],
    "technical_skills_evaluation": ["string"],
    "areas_of_uncertainty": ["string"],
    "suggested_focus_areas": ["string"]
}"""

CV_STRUCTURE_PROMPT = """Create a strictly-formatted JSON object from this CV.
IMPORTANT: Do NOT include any comments or explanations in the JSON.
Use null for missing values, empty arrays [] for missing lists.

The JSON must follow this exact structure:
{
    "basic_info": {
        "name": "string",
        "contact": {
            "email": "string",
            "phone": "string",
            "location": "string"
        },
        "education": [{
            "school": "string",
            "degree": "string",
            "gpa": number or null,
            "dates": "string",
            "honors": ["string"]
        }]
    },
    "research_experience": [{
        "position": "string",
        "organization": "string",
        "duration": "string",
        "description": "string",
        "skills_used": ["string"],
        "publications": ["string"],
        "presentations": ["string"]
    }],
    "clinical_experience": [{
        "position": "string",
        "organization": "string",
        "total_hours": number or null,
        "duration": "string",
        "description": "string",
        "patient_interaction": true or false,
        "skills_demonstrated": ["string"]
    }],
    "leadership": [{
        "position": "string",
        "organization": "string",
        "duration": "string",
        "impact": "string",
        "team_size": number or null
    }],
    "skills_and_certifications": {
        "technical_skills": ["string"],
        "certifications": ["string"],
        "languages": ["string"]
    },
    "awards_and_honors": [{
        "name": "string",
        "organization": "string",
        "date": "string",
        "description": "string"
    }],
    "additional_info": {
        "volunteer_work": ["string"],
        "extracurricular": ["string"],
        "other_achievements": ["string"]
    }
}"""

TRANSCRIPT_REASONING_PROMPT = """You are an expert at analyzing academic transcripts for medical school applications.
Analyze this transcript and provide your observations, uncertainties, and reasoning.
Focus on:
- Academic performance and trends
- Course load and difficulty
- Science/math preparation
- Performance in key pre-med courses
- Notable strengths or patterns
- Any potential concerns or gaps

Provide your analysis as valid JSON with these fields:
{
    "key_observations": ["string"],
    "academic_trends": ["string"],
    "science_preparation": ["string"],
    "course_load_analysis": ["string"],
    "strengths_identified": ["string"],
    "potential_concerns": ["string"],
    "suggested_coursework": ["string"]
}"""

TRANSCRIPT_STRUCTURE_PROMPT = """Create a strictly-formatted JSON object from this transcript.
IMPORTANT: Do NOT include any comments or explanations in the JSON.
Use null for missing values, empty arrays [] for missing lists.

The JSON must follow this exact structure:
{
    "student_info": {
        "name": "string",
        "id": "string",
        "major": "string",
        "minor": "string or null"
    },
    "academic_summary": {
        "overall_gpa": number,
        "total_credits": number,
        "science_gpa": number or null,
        "academic_standing": "string",
        "expected_graduation": "string"
    },
    "terms": [{
        "term": "string",
        "gpa": number,
        "credits_attempted": number,
        "credits_earned": number,
        "courses": [{
            "course_code": "string",
            "title": "string",
            "credits": number,
            "grade": "string",
            "category": "string"
        }],
        "term_honors": ["string"],
        "academic_status": "string"
    }],
    "pre_med_courses": {
        "biology": [{
            "course_code": "string",
            "title": "string",
            "grade": "string",
            "term": "string"
        }],
        "chemistry": [{
            "course_code": "string",
            "title": "string",
            "grade": "string",
            "term": "string"
        }],
        "physics": [{
            "course_code": "string",
            "title": "string",
            "grade": "string",
            "term": "string"
        }],
        "math": [{
            "course_code": "string",
            "title": "string",
            "grade": "string",
            "term": "string"
        }]
    },
    "additional_info": {
        "academic_honors": ["string"],
        "study_abroad": ["string"],
        "notes": ["string"]
    }
}"""

def clean_json_response(response: str) -> str:
    """Remove markdown code blocks and get just the JSON content."""
    # Print full response for debugging
    print("Raw response to clean:", response[:100], "...")
    
    # If response is wrapped in ```json ... ```
    if response.startswith('```'):
        # Find the first and last curly brace
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > 0:
            cleaned = response[start:end]
            print(f"Cleaned response (first 100 chars): {cleaned[:100]}...")
            return cleaned
    
    # If response isn't markdown-wrapped, look for JSON content
    start = response.find('{')
    end = response.rfind('}') + 1
    if start >= 0 and end > 0:
        cleaned = response[start:end]
        print(f"Extracted JSON (first 100 chars): {cleaned[:100]}...")
        return cleaned
        
    # If we can't find JSON markers, return the original
    print("No JSON markers found, returning original")
    return response

def extract_text(file_data: bytes) -> str:
    """Extract text from PDF bytes."""
    try:
        print(f"extract_text received: {type(file_data)}, length: {len(file_data)}")
        pdf_file = BytesIO(file_data)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        print(f"Extracted text length: {len(text)}")
        return text
    except Exception as e:
        print(f"Error extracting text: {str(e)}")
        raise e

def parse_document(file_data: bytes, file_type: str, doc_type: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Parse document using GPT-4, returning both structured data and reasoning."""
    try:
        print(f"parse_document received:")
        print(f"- file_data type: {type(file_data)}")
        print(f"- file_type: {file_type}")
        print(f"- doc_type: {doc_type}")
        
        # Extract text
        text_content = extract_text(file_data)
        print(f"\nDocument Preview (first 500 chars):")
        print("-" * 50)
        print(text_content[:500])
        print("-" * 50)
        
        # Select appropriate prompts based on document type
        if doc_type == "cv":
            structure_prompt = CV_STRUCTURE_PROMPT
            reasoning_prompt = CV_REASONING_PROMPT
        elif doc_type == "transcript":
            structure_prompt = TRANSCRIPT_STRUCTURE_PROMPT
            reasoning_prompt = TRANSCRIPT_REASONING_PROMPT
        else:
            raise ValueError(f"Unsupported document type: {doc_type}")
        
        # First pass: Get AI reasoning and analysis
        print(f"Getting {doc_type} analysis with reasoning...")
        reasoning_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": reasoning_prompt},
                {"role": "user", "content": f"Here is the {doc_type} content:\n\n{text_content}"}
            ]
        )
        print("Got reasoning response")
        
        # Second pass: Get structured data
        print(f"Getting structured {doc_type} data...")
        structure_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": structure_prompt},
                {"role": "user", "content": f"Here is the {doc_type} content:\n\n{text_content}"}
            ]
        )
        print("Got structured response")
        
        try:
            # Clean and parse both responses
            structure_text = clean_json_response(structure_response.choices[0].message.content)
            reasoning_text = clean_json_response(reasoning_response.choices[0].message.content)
            
            # Parse the cleaned JSON
            try:
                structured_data = json.loads(structure_text)
            except json.JSONDecodeError as e:
                print("Error parsing structured data:")
                print(f"Cleaned text: {structure_text[:500]}...")
                raise Exception(f"Error parsing structured data: {str(e)}")
                
            try:
                reasoning_data = json.loads(reasoning_text)
            except json.JSONDecodeError as e:
                print("Error parsing reasoning data:")
                print(f"Cleaned text: {reasoning_text[:500]}...")
                raise Exception(f"Error parsing reasoning data: {str(e)}")
            
            return structured_data, reasoning_data
            
        except Exception as e:
            print("\nRaw Structure Response:")
            print(structure_response.choices[0].message.content)
            print("\nRaw Reasoning Response:")
            print(reasoning_response.choices[0].message.content)
            raise Exception(f"Error parsing responses: {str(e)}")
            
    except Exception as e:
        print(f"Error in parse_document: {str(e)}")
        raise Exception(f"Error processing document: {str(e)}")

def parse_uploaded_file(file, file_type: str, doc_type: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Parse an uploaded file."""
    try:
        print(f"parse_uploaded_file received file of type: {type(file)}")
        
        # Handle different input types
        if isinstance(file, (bytes, bytearray)):
            file_data = file
        elif hasattr(file, 'getvalue'):
            file_data = file.getvalue()
        elif hasattr(file, 'read'):
            if hasattr(file, 'seek'):
                file.seek(0)
            file_data = file.read()
        else:
            raise ValueError(f"Unsupported file type: {type(file)}")
            
        print(f"File data length: {len(file_data)}")
        return parse_document(file_data, file_type, doc_type)
    except Exception as e:
        print(f"Error parsing uploaded file: {str(e)}")
        raise e
