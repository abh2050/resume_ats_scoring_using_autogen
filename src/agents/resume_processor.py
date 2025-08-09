"""
Resume Processing Agent for ATS System
Handles multi-format resume parsing and standardization
"""

import autogen
from typing import Dict, List, Any, Optional, Union
import json
import PyPDF2
import docx
import re
from datetime import datetime
import hashlib
import os
from pathlib import Path


class ResumeProcessingAgent:
    """
    AutoGen agent for processing resumes in multiple formats
    Converts resumes to standardized JSON format for scoring
    """
    
    def __init__(self, config_list: List[Dict[str, Any]], work_dir: str = "resume_workspace"):
        self.config_list = config_list
        self.work_dir = work_dir
        self.supported_formats = ['.pdf', '.docx', '.txt']
        self.processing_log = []
        
        # Create the AutoGen agent
        self.agent = autogen.AssistantAgent(
            name="Resume_Processor",
            llm_config={"config_list": config_list},
            system_message="""You are a specialized Resume Processing Agent with expertise in:
            
            1. MULTI-FORMAT PARSING:
            - Extract text from PDF, DOCX, and TXT files
            - Handle various resume layouts and formats
            - Preserve important formatting information
            
            2. INFORMATION EXTRACTION:
            - Personal information (name, contact details)
            - Professional experience with dates and responsibilities
            - Education background and certifications
            - Skills (technical and soft skills)
            - Achievements and quantifiable results
            
            3. STANDARDIZATION:
            - Convert extracted information to structured JSON format
            - Normalize date formats and skill categories
            - Clean and validate extracted data
            - Ensure consistency across different resume formats
            
            4. QUALITY ASSURANCE:
            - Verify extraction accuracy
            - Flag missing critical information
            - Identify potential parsing errors
            - Provide extraction confidence scores
            
            Always maintain high accuracy in text extraction and provide detailed
            feedback on processing quality and any limitations encountered."""
        )
    
    def process_resume(self, file_path: str, file_type: str = None) -> Dict[str, Any]:
        """
        Process a resume file and convert to standardized JSON format
        
        Args:
            file_path: Path to the resume file
            file_type: Optional file type override
            
        Returns:
            Standardized resume data in JSON format
        """
        try:
            # Detect file type if not provided
            if not file_type:
                file_type = Path(file_path).suffix.lower()
            
            # Validate file format
            if file_type not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {file_type}")
            
            # Extract raw text based on file type
            raw_text = self._extract_text(file_path, file_type)
            
            # Parse and structure the resume data
            structured_data = self._parse_resume_content(raw_text)
            
            # Add metadata
            structured_data['metadata'] = self._generate_metadata(file_path, raw_text)
            
            # Log processing
            self._log_processing(file_path, True, len(raw_text))
            
            return structured_data
            
        except Exception as e:
            self._log_processing(file_path, False, 0, str(e))
            raise e
    
    def _extract_text(self, file_path: str, file_type: str) -> str:
        """Extract raw text from resume file based on format"""
        
        if file_type == '.pdf':
            return self._extract_from_pdf(file_path)
        elif file_type == '.docx':
            return self._extract_from_docx(file_path)
        elif file_type == '.txt':
            return self._extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            raise Exception(f"PDF extraction failed: {str(e)}")
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"DOCX extraction failed: {str(e)}")
    
    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            raise Exception(f"TXT extraction failed: {str(e)}")
    
    def _parse_resume_content(self, raw_text: str) -> Dict[str, Any]:
        """
        Parse raw resume text into structured format using LLM
        """
        parsing_prompt = f"""
        Parse the following resume text into a structured JSON format. Extract all relevant information
        accurately and organize it according to the schema below.
        
        RESUME TEXT:
        {raw_text}
        
        Please structure the output as a JSON object with the following schema:
        {{
            "personal_info": {{
                "name": "Full name",
                "email": "Email address",
                "phone": "Phone number",
                "location": "City, State/Country",
                "linkedin": "LinkedIn URL if present",
                "website": "Personal website if present"
            }},
            "professional_summary": "Brief professional summary or objective",
            "experience": [
                {{
                    "title": "Job title",
                    "company": "Company name",
                    "location": "Job location",
                    "start_date": "Start date (MM/YYYY format)",
                    "end_date": "End date (MM/YYYY format) or 'Present'",
                    "duration": "Calculated duration",
                    "responsibilities": ["List of key responsibilities"],
                    "achievements": ["Quantifiable achievements"]
                }}
            ],
            "education": [
                {{
                    "degree": "Degree type and field",
                    "institution": "School/University name",
                    "location": "Institution location",
                    "graduation_date": "Graduation date (MM/YYYY)",
                    "gpa": "GPA if mentioned",
                    "honors": "Any honors or distinctions"
                }}
            ],
            "skills": {{
                "technical_skills": ["List of technical skills"],
                "soft_skills": ["List of soft skills"],
                "programming_languages": ["Programming languages if applicable"],
                "tools_technologies": ["Tools and technologies"],
                "certifications": ["Professional certifications"]
            }},
            "projects": [
                {{
                    "name": "Project name",
                    "description": "Project description",
                    "technologies": ["Technologies used"],
                    "duration": "Project duration",
                    "link": "Project link if available"
                }}
            ],
            "additional_sections": {{
                "languages": ["Spoken languages"],
                "volunteer_work": ["Volunteer experiences"],
                "awards": ["Awards and recognition"],
                "publications": ["Publications if any"],
                "interests": ["Personal interests"]
            }}
        }}
        
        IMPORTANT PARSING GUIDELINES:
        1. Extract information exactly as written, do not infer or add information
        2. Use "Not specified" for missing information
        3. Maintain consistent date formats (MM/YYYY)
        4. Separate technical and soft skills appropriately
        5. Include all quantifiable achievements with numbers
        6. Preserve the original formatting context where relevant
        
        Return only the JSON object, no additional text or explanation.
        """
        
        # Use the AutoGen agent to process the parsing
        user_proxy = autogen.UserProxyAgent(
            name="User",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0,
            code_execution_config=False
        )
        
        # Initiate conversation for parsing
        response = user_proxy.initiate_chat(
            self.agent,
            message=parsing_prompt,
            silent=True
        )
        
        # Extract JSON from response
        try:
            # Get the last message from the agent
            last_message = response.chat_history[-1]['content']
            
            # Extract JSON from the response
            json_start = last_message.find('{')
            json_end = last_message.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = last_message[json_start:json_end]
                structured_data = json.loads(json_str)
                return structured_data
            else:
                raise ValueError("No valid JSON found in response")
                
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback to basic parsing if LLM parsing fails
            return self._fallback_parsing(raw_text)
    
    def _fallback_parsing(self, raw_text: str) -> Dict[str, Any]:
        """
        Fallback parsing method using regex patterns
        Used when LLM parsing fails
        """
        
        # Basic email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, raw_text)
        
        # Basic phone extraction
        phone_pattern = r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})'
        phones = re.findall(phone_pattern, raw_text)
        
        # Basic skills extraction (common technical skills)
        tech_skills_patterns = [
            r'\b(Python|Java|JavaScript|React|Angular|Node\.js|SQL|MongoDB|AWS|Docker)\b',
            r'\b(Machine Learning|Data Science|AI|Deep Learning|NLP)\b',
            r'\b(Git|GitHub|Linux|Windows|MacOS)\b'
        ]
        
        skills = []
        for pattern in tech_skills_patterns:
            skills.extend(re.findall(pattern, raw_text, re.IGNORECASE))
        
        # Basic structure with extracted information
        fallback_data = {
            "personal_info": {
                "name": "Not extracted",
                "email": emails[0] if emails else "Not specified",
                "phone": phones[0] if phones else "Not specified",
                "location": "Not specified",
                "linkedin": "Not specified",
                "website": "Not specified"
            },
            "professional_summary": "Not extracted - fallback parsing used",
            "experience": [],
            "education": [],
            "skills": {
                "technical_skills": list(set(skills)),
                "soft_skills": [],
                "programming_languages": [],
                "tools_technologies": [],
                "certifications": []
            },
            "projects": [],
            "additional_sections": {
                "languages": [],
                "volunteer_work": [],
                "awards": [],
                "publications": [],
                "interests": []
            },
            "parsing_note": "Fallback parsing used due to LLM parsing failure"
        }
        
        return fallback_data
    
    def _generate_metadata(self, file_path: str, raw_text: str) -> Dict[str, Any]:
        """Generate metadata for the processed resume"""
        
        # Calculate file hash for consistency checking
        file_hash = hashlib.md5(raw_text.encode()).hexdigest()
        
        metadata = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_size": len(raw_text),
            "word_count": len(raw_text.split()),
            "character_count": len(raw_text),
            "processing_timestamp": datetime.now().isoformat(),
            "file_hash": file_hash,
            "extraction_method": "automated",
            "format_detected": Path(file_path).suffix.lower()
        }
        
        return metadata
    
    def _log_processing(self, file_path: str, success: bool, text_length: int, error: str = None):
        """Log processing results for tracking and debugging"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "file_path": file_path,
            "success": success,
            "text_length": text_length,
            "error": error
        }
        
        self.processing_log.append(log_entry)
    
    def batch_process_resumes(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Process multiple resumes in batch
        
        Args:
            file_paths: List of resume file paths
            
        Returns:
            List of processed resume data
        """
        results = []
        
        for file_path in file_paths:
            try:
                result = self.process_resume(file_path)
                result['batch_processing'] = True
                results.append(result)
            except Exception as e:
                # Add error result for failed processing
                error_result = {
                    "error": True,
                    "file_path": file_path,
                    "error_message": str(e),
                    "batch_processing": True,
                    "metadata": {
                        "processing_timestamp": datetime.now().isoformat(),
                        "file_name": os.path.basename(file_path)
                    }
                }
                results.append(error_result)
        
        return results
    
    def validate_extraction(self, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the quality of extracted resume data
        
        Args:
            structured_data: Processed resume data
            
        Returns:
            Validation report with quality scores and recommendations
        """
        validation_report = {
            "overall_quality": 0,
            "validation_timestamp": datetime.now().isoformat(),
            "issues": [],
            "recommendations": [],
            "completeness_score": 0,
            "data_quality_score": 0
        }
        
        # Check completeness of key sections
        completeness_checks = {
            "personal_info": ["name", "email"],
            "experience": "at least one job",
            "education": "at least one degree",
            "skills": "at least one skill category"
        }
        
        completeness_score = 0
        total_checks = len(completeness_checks)
        
        # Validate personal info
        personal_info = structured_data.get("personal_info", {})
        if personal_info.get("name") and personal_info.get("name") != "Not specified":
            if personal_info.get("email") and personal_info.get("email") != "Not specified":
                completeness_score += 1
            else:
                validation_report["issues"].append("Missing or invalid email address")
        else:
            validation_report["issues"].append("Missing or invalid name")
        
        # Validate experience
        experience = structured_data.get("experience", [])
        if experience and len(experience) > 0:
            completeness_score += 1
        else:
            validation_report["issues"].append("No work experience found")
        
        # Validate education
        education = structured_data.get("education", [])
        if education and len(education) > 0:
            completeness_score += 1
        else:
            validation_report["issues"].append("No education information found")
        
        # Validate skills
        skills = structured_data.get("skills", {})
        has_skills = any(skills.get(category, []) for category in skills.keys())
        if has_skills:
            completeness_score += 1
        else:
            validation_report["issues"].append("No skills information found")
        
        validation_report["completeness_score"] = (completeness_score / total_checks) * 100
        validation_report["overall_quality"] = validation_report["completeness_score"]
        
        # Generate recommendations
        if validation_report["completeness_score"] < 75:
            validation_report["recommendations"].append("Consider manual review and enhancement of extracted data")
        
        if len(validation_report["issues"]) > 2:
            validation_report["recommendations"].append("Resume may need better formatting for optimal extraction")
        
        return validation_report
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get processing statistics for monitoring and optimization"""
        
        if not self.processing_log:
            return {"message": "No processing history available"}
        
        total_processed = len(self.processing_log)
        successful = len([log for log in self.processing_log if log["success"]])
        failed = total_processed - successful
        
        avg_text_length = sum(log["text_length"] for log in self.processing_log if log["success"]) / max(successful, 1)
        
        stats = {
            "total_processed": total_processed,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total_processed) * 100,
            "average_text_length": avg_text_length,
            "recent_errors": [log["error"] for log in self.processing_log[-5:] if not log["success"]]
        }
        
        return stats


# Example usage and testing functions
def test_resume_processor():
    """Test function for the Resume Processing Agent"""
    
    # Sample configuration
    config_list = [
        {
            "model": "gpt-4",
            "api_key": "your-api-key-here",
            "base_url": "https://api.openai.com/v1",
        }
    ]
    
    # Initialize processor
    processor = ResumeProcessingAgent(config_list)
    
    # Test with sample resume (you would provide actual file paths)
    sample_text = """
    John Doe
    john.doe@email.com
    (555) 123-4567
    New York, NY
    
    Software Engineer with 5 years of experience in Python and JavaScript development.
    
    Experience:
    Senior Software Engineer | Tech Company | Jan 2020 - Present
    - Developed web applications using React and Node.js
    - Led team of 3 developers on major product features
    - Improved application performance by 40%
    
    Education:
    Bachelor of Science in Computer Science | University XYZ | 2018
    
    Skills: Python, JavaScript, React, Node.js, SQL, Git
    """
    
    # Create a temporary file for testing
    test_file = "test_resume.txt"
    with open(test_file, 'w') as f:
        f.write(sample_text)
    
    try:
        # Process the resume
        result = processor.process_resume(test_file)
        
        print("Processing successful!")
        print(json.dumps(result, indent=2))
        
        # Validate extraction
        validation = processor.validate_extraction(result)
        print("\nValidation Report:")
        print(json.dumps(validation, indent=2))
        
    except Exception as e:
        print(f"Processing failed: {str(e)}")
    
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)


if __name__ == "__main__":
    test_resume_processor()
