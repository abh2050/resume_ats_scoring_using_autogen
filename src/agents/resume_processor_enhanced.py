"""
Enhanced Resume Processing Agent
Supports both Pure Python and AutoGen LLM modes
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path
import re

# Import AutoGen conditionally
try:
    import autogen
    from autogen import AssistantAgent, UserProxyAgent
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False
    logging.warning("AutoGen not available - using pure Python mode")

# Local imports
from ..utils.config import get_config, get_autogen_config, is_llm_enabled

# Document processing imports
try:
    import PyPDF2
    import docx
    import pdfplumber
except ImportError as e:
    logging.warning(f"Document processing library not available: {e}")


class ResumeProcessingAgent:
    """
    Enhanced Resume Processing Agent that can operate in two modes:
    1. Pure Python mode (deterministic, fast, no API costs)
    2. AutoGen LLM mode (intelligent, context-aware, requires API key)
    """
    
    def __init__(self, use_llm: bool = None):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        
        # Determine processing mode
        if use_llm is None:
            self.use_llm = is_llm_enabled()
        else:
            self.use_llm = use_llm and is_llm_enabled()
        
        # Initialize appropriate processor
        if self.use_llm and AUTOGEN_AVAILABLE:
            self._init_llm_agent()
        else:
            self._init_python_processor()
        
        self.logger.info(f"ResumeProcessingAgent initialized in {'LLM' if self.use_llm else 'Python'} mode")
    
    def _init_llm_agent(self):
        """Initialize AutoGen LLM-based agent"""
        
        autogen_config = get_autogen_config()
        if not autogen_config:
            self.logger.warning("No AutoGen config available, falling back to Python mode")
            self.use_llm = False
            self._init_python_processor()
            return
        
        # Create AutoGen assistant agent
        self.llm_agent = AssistantAgent(
            name="resume_processor",
            system_message="""You are an expert resume processing agent. Your task is to:
            1. Extract and structure resume information
            2. Standardize the data into JSON format
            3. Identify key sections: personal info, skills, experience, education
            4. Clean and normalize the extracted data
            5. Handle various resume formats and layouts
            
            Always respond with valid JSON containing the structured resume data.""",
            llm_config=autogen_config
        )
        
        # Create user proxy for interaction
        self.user_proxy = UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            code_execution_config=False
        )
    
    def _init_python_processor(self):
        """Initialize pure Python processor"""
        self.use_llm = False
        
        # Define regex patterns for data extraction
        self.patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            "linkedin": r'linkedin\.com/in/[\w-]+',
            "github": r'github\.com/[\w-]+',
            "url": r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
        }
        
        # Common section headers
        self.section_headers = {
            "experience": ["experience", "work experience", "employment", "professional experience", "work history"],
            "education": ["education", "academic background", "qualifications", "degrees"],
            "skills": ["skills", "technical skills", "core competencies", "expertise", "technologies"],
            "projects": ["projects", "key projects", "notable projects", "personal projects"],
            "certifications": ["certifications", "certificates", "professional certifications"],
            "achievements": ["achievements", "accomplishments", "awards", "honors"]
        }
    
    def process_resume(self, file_path: str, content: str = None) -> Dict[str, Any]:
        """
        Process resume and extract structured data
        
        Args:
            file_path: Path to resume file
            content: Optional pre-extracted text content
            
        Returns:
            Structured resume data as dictionary
        """
        
        try:
            # Extract text if not provided
            if content is None:
                content = self._extract_text_from_file(file_path)
            
            if not content.strip():
                raise ValueError("No text content could be extracted from the file")
            
            # Process using appropriate method
            if self.use_llm:
                return self._process_with_llm(content, file_path)
            else:
                return self._process_with_python(content, file_path)
        
        except Exception as e:
            self.logger.error(f"Error processing resume {file_path}: {e}")
            return self._create_error_result(str(e), file_path)
    
    def _process_with_llm(self, content: str, file_path: str) -> Dict[str, Any]:
        """Process resume using AutoGen LLM agent"""
        
        try:
            # Prepare prompt for LLM
            prompt = f"""
            Please extract and structure the following resume content into JSON format.
            
            Required JSON structure:
            {{
                "personal_info": {{
                    "name": "string",
                    "email": "string",
                    "phone": "string",
                    "location": "string",
                    "linkedin": "string",
                    "github": "string"
                }},
                "summary": "string",
                "skills": {{
                    "technical": ["list of technical skills"],
                    "soft": ["list of soft skills"],
                    "languages": ["programming languages"],
                    "tools": ["tools and technologies"]
                }},
                "experience": [
                    {{
                        "title": "string",
                        "company": "string",
                        "location": "string",
                        "start_date": "string",
                        "end_date": "string",
                        "description": "string",
                        "achievements": ["list of achievements"]
                    }}
                ],
                "education": [
                    {{
                        "degree": "string",
                        "institution": "string",
                        "location": "string",
                        "graduation_date": "string",
                        "gpa": "string"
                    }}
                ],
                "projects": [
                    {{
                        "name": "string",
                        "description": "string",
                        "technologies": ["list"],
                        "url": "string"
                    }}
                ],
                "certifications": ["list of certifications"]
            }}
            
            Resume content:
            {content[:4000]}  # Limit content to avoid token limits
            """
            
            # Get response from LLM
            response = self.user_proxy.initiate_chat(
                self.llm_agent,
                message=prompt
            )
            
            # Extract JSON from response
            response_text = response.last_message["content"] if hasattr(response, 'last_message') else str(response)
            
            # Try to parse JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                result["processing_method"] = "llm"
                result["file_path"] = file_path
                result["processed_at"] = datetime.now().isoformat()
                return result
            else:
                self.logger.warning("LLM did not return valid JSON, falling back to Python processing")
                return self._process_with_python(content, file_path)
        
        except Exception as e:
            self.logger.error(f"LLM processing failed: {e}, falling back to Python processing")
            return self._process_with_python(content, file_path)
    
    def _process_with_python(self, content: str, file_path: str) -> Dict[str, Any]:
        """Process resume using pure Python extraction"""
        
        # Clean and prepare content
        lines = content.split('\n')
        clean_lines = [line.strip() for line in lines if line.strip()]
        
        result = {
            "personal_info": self._extract_personal_info(content),
            "summary": self._extract_summary(clean_lines),
            "skills": self._extract_skills(clean_lines),
            "experience": self._extract_experience(clean_lines),
            "education": self._extract_education(clean_lines),
            "projects": self._extract_projects(clean_lines),
            "certifications": self._extract_certifications(clean_lines),
            "processing_method": "python",
            "file_path": file_path,
            "processed_at": datetime.now().isoformat(),
            "metadata": {
                "total_lines": len(lines),
                "non_empty_lines": len(clean_lines),
                "character_count": len(content),
                "estimated_reading_time": len(content.split()) / 200  # words per minute
            }
        }
        
        return result
    
    def _extract_personal_info(self, content: str) -> Dict[str, str]:
        """Extract personal information using regex patterns"""
        
        personal_info = {}
        
        # Extract email
        email_match = re.search(self.patterns["email"], content)
        personal_info["email"] = email_match.group() if email_match else ""
        
        # Extract phone
        phone_match = re.search(self.patterns["phone"], content)
        personal_info["phone"] = phone_match.group() if phone_match else ""
        
        # Extract LinkedIn
        linkedin_match = re.search(self.patterns["linkedin"], content)
        personal_info["linkedin"] = linkedin_match.group() if linkedin_match else ""
        
        # Extract GitHub
        github_match = re.search(self.patterns["github"], content)
        personal_info["github"] = github_match.group() if github_match else ""
        
        # Extract name (heuristic: first non-empty line that's not an email/phone)
        lines = content.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and not re.search(self.patterns["email"], line) and not re.search(self.patterns["phone"], line):
                if len(line.split()) >= 2 and len(line.split()) <= 4:  # Reasonable name length
                    personal_info["name"] = line
                    break
        
        # Extract location (heuristic: look for city, state patterns)
        location_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2}|[A-Z][a-z]+)'
        location_match = re.search(location_pattern, content)
        personal_info["location"] = location_match.group() if location_match else ""
        
        return personal_info
    
    def _extract_summary(self, lines: List[str]) -> str:
        """Extract professional summary or objective"""
        
        summary_keywords = ["summary", "objective", "profile", "about", "overview"]
        
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in summary_keywords):
                # Look for content in next few lines
                summary_lines = []
                for j in range(i + 1, min(i + 6, len(lines))):
                    if lines[j] and not self._is_section_header(lines[j]):
                        summary_lines.append(lines[j])
                    else:
                        break
                
                if summary_lines:
                    return " ".join(summary_lines)
        
        return ""
    
    def _extract_skills(self, lines: List[str]) -> Dict[str, List[str]]:
        """Extract skills categorized by type"""
        
        skills = {"technical": [], "soft": [], "languages": [], "tools": []}
        
        # Find skills section
        skills_start = None
        for i, line in enumerate(lines):
            if any(header in line.lower() for header in self.section_headers["skills"]):
                skills_start = i
                break
        
        if skills_start is None:
            return skills
        
        # Extract skills from section
        for i in range(skills_start + 1, len(lines)):
            line = lines[i]
            
            if self._is_section_header(line):
                break
            
            # Parse skill line
            if ',' in line or '•' in line or '|' in line:
                # Split by common delimiters
                delimiters = [',', '•', '|', ';']
                skill_items = [line]
                
                for delimiter in delimiters:
                    new_items = []
                    for item in skill_items:
                        new_items.extend([s.strip() for s in item.split(delimiter)])
                    skill_items = new_items
                
                # Categorize skills (simplified heuristics)
                for skill in skill_items:
                    skill = skill.strip()
                    if skill and len(skill) > 1:
                        skill_lower = skill.lower()
                        
                        # Programming languages
                        if any(lang in skill_lower for lang in ['python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'go', 'rust']):
                            skills["languages"].append(skill)
                        # Tools and technologies
                        elif any(tool in skill_lower for tool in ['aws', 'docker', 'kubernetes', 'git', 'jenkins', 'sql']):
                            skills["tools"].append(skill)
                        # Soft skills
                        elif any(soft in skill_lower for soft in ['leadership', 'communication', 'management', 'teamwork']):
                            skills["soft"].append(skill)
                        else:
                            skills["technical"].append(skill)
        
        return skills
    
    def _extract_experience(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract work experience entries"""
        
        experience = []
        
        # Find experience section
        exp_start = None
        for i, line in enumerate(lines):
            if any(header in line.lower() for header in self.section_headers["experience"]):
                exp_start = i
                break
        
        if exp_start is None:
            return experience
        
        # Extract experience entries (simplified)
        current_entry = None
        
        for i in range(exp_start + 1, len(lines)):
            line = lines[i]
            
            if self._is_section_header(line):
                if current_entry:
                    experience.append(current_entry)
                break
            
            # Try to identify job title/company line
            if self._looks_like_job_title(line):
                if current_entry:
                    experience.append(current_entry)
                
                current_entry = {
                    "title": "",
                    "company": "",
                    "location": "",
                    "start_date": "",
                    "end_date": "",
                    "description": "",
                    "achievements": []
                }
                
                # Parse title and company from line
                parts = line.split(' at ')
                if len(parts) == 2:
                    current_entry["title"] = parts[0].strip()
                    current_entry["company"] = parts[1].strip()
                else:
                    current_entry["title"] = line.strip()
            
            elif current_entry and line.strip():
                # Add to description or achievements
                if line.startswith('•') or line.startswith('-'):
                    current_entry["achievements"].append(line.strip('•- '))
                else:
                    current_entry["description"] += " " + line.strip()
        
        if current_entry:
            experience.append(current_entry)
        
        return experience
    
    def _extract_education(self, lines: List[str]) -> List[Dict[str, str]]:
        """Extract education entries"""
        
        education = []
        
        # Find education section
        edu_start = None
        for i, line in enumerate(lines):
            if any(header in line.lower() for header in self.section_headers["education"]):
                edu_start = i
                break
        
        if edu_start is None:
            return education
        
        # Extract education entries (simplified)
        for i in range(edu_start + 1, len(lines)):
            line = lines[i]
            
            if self._is_section_header(line):
                break
            
            if line.strip() and ('degree' in line.lower() or 'university' in line.lower() or 'college' in line.lower()):
                education.append({
                    "degree": line.strip(),
                    "institution": "",
                    "location": "",
                    "graduation_date": "",
                    "gpa": ""
                })
        
        return education
    
    def _extract_projects(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract project entries"""
        
        projects = []
        
        # Find projects section
        proj_start = None
        for i, line in enumerate(lines):
            if any(header in line.lower() for header in self.section_headers["projects"]):
                proj_start = i
                break
        
        if proj_start is None:
            return projects
        
        # Extract project entries (simplified)
        for i in range(proj_start + 1, len(lines)):
            line = lines[i]
            
            if self._is_section_header(line):
                break
            
            if line.strip() and not line.startswith(' '):
                projects.append({
                    "name": line.strip(),
                    "description": "",
                    "technologies": [],
                    "url": ""
                })
        
        return projects
    
    def _extract_certifications(self, lines: List[str]) -> List[str]:
        """Extract certifications"""
        
        certifications = []
        
        # Find certifications section
        cert_start = None
        for i, line in enumerate(lines):
            if any(header in line.lower() for header in self.section_headers["certifications"]):
                cert_start = i
                break
        
        if cert_start is None:
            return certifications
        
        # Extract certification entries
        for i in range(cert_start + 1, len(lines)):
            line = lines[i]
            
            if self._is_section_header(line):
                break
            
            if line.strip():
                certifications.append(line.strip())
        
        return certifications
    
    def _is_section_header(self, line: str) -> bool:
        """Check if line is likely a section header"""
        
        line_lower = line.lower().strip()
        
        # Check against known section headers
        all_headers = []
        for headers in self.section_headers.values():
            all_headers.extend(headers)
        
        return any(header in line_lower for header in all_headers)
    
    def _looks_like_job_title(self, line: str) -> bool:
        """Heuristic to identify job title lines"""
        
        line = line.strip()
        
        # Check for common job title patterns
        job_indicators = ['engineer', 'developer', 'manager', 'analyst', 'specialist', 'coordinator', 'director']
        company_indicators = [' at ', ' | ', ' - ']
        
        has_job_indicator = any(indicator in line.lower() for indicator in job_indicators)
        has_company_indicator = any(indicator in line for indicator in company_indicators)
        
        return has_job_indicator or has_company_indicator
    
    def _extract_text_from_file(self, file_path: str) -> str:
        """Extract text content from various file formats"""
        
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            if file_path.suffix.lower() == '.pdf':
                return self._extract_from_pdf(file_path)
            elif file_path.suffix.lower() in ['.docx', '.doc']:
                return self._extract_from_docx(file_path)
            elif file_path.suffix.lower() == '.txt':
                return self._extract_from_txt(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        except Exception as e:
            self.logger.error(f"Error extracting text from {file_path}: {e}")
            raise
    
    def _extract_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file with fallback methods"""
        
        text = ""
        
        # Try pdfplumber first (better for complex layouts)
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            if text.strip():
                return text
        except Exception as e:
            self.logger.warning(f"pdfplumber failed: {e}, trying PyPDF2")
        
        # Fallback to PyPDF2
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            self.logger.error(f"PyPDF2 also failed: {e}")
            raise ValueError("Could not extract text from PDF file")
        
        return text
    
    def _extract_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file"""
        
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            self.logger.error(f"Error extracting from DOCX: {e}")
            raise ValueError("Could not extract text from DOCX file")
    
    def _extract_from_txt(self, file_path: Path) -> str:
        """Extract text from TXT file"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try different encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        return file.read()
                except UnicodeDecodeError:
                    continue
            
            raise ValueError("Could not decode text file with any supported encoding")
    
    def _create_error_result(self, error_message: str, file_path: str) -> Dict[str, Any]:
        """Create error result structure"""
        
        return {
            "error": True,
            "error_message": error_message,
            "file_path": file_path,
            "processed_at": datetime.now().isoformat(),
            "processing_method": "error",
            "personal_info": {},
            "summary": "",
            "skills": {"technical": [], "soft": [], "languages": [], "tools": []},
            "experience": [],
            "education": [],
            "projects": [],
            "certifications": []
        }


# Example usage and testing
def test_resume_processing():
    """Test resume processing in both modes"""
    
    # Test with Python mode
    print("=== Testing Python Mode ===")
    python_agent = ResumeProcessingAgent(use_llm=False)
    
    # Create sample resume content
    sample_content = """
    John Doe
    john.doe@email.com | (555) 123-4567 | LinkedIn: linkedin.com/in/johndoe
    New York, NY
    
    Professional Summary
    Experienced software engineer with 5+ years in web development and cloud technologies.
    
    Technical Skills
    Programming Languages: Python, JavaScript, Java, TypeScript
    Frameworks: React, Node.js, Django, FastAPI
    Tools: AWS, Docker, Kubernetes, Git, Jenkins
    
    Professional Experience
    Senior Software Engineer at Tech Corp
    • Developed scalable web applications serving 100K+ users
    • Led team of 4 developers on microservices architecture
    • Improved system performance by 40% through optimization
    
    Software Engineer at StartupXYZ
    • Built REST APIs using Python and FastAPI
    • Implemented CI/CD pipelines with Jenkins and Docker
    
    Education
    Bachelor of Science in Computer Science
    University of Technology, 2018
    
    Projects
    E-commerce Platform
    Built full-stack e-commerce solution using React and Node.js
    
    Certifications
    AWS Solutions Architect Associate
    """
    
    result = python_agent.process_resume("sample_resume.txt", sample_content)
    print(f"Processing method: {result['processing_method']}")
    print(f"Name extracted: {result['personal_info'].get('name', 'Not found')}")
    print(f"Email extracted: {result['personal_info'].get('email', 'Not found')}")
    print(f"Technical skills: {result['skills']['technical'][:3]}...")
    
    # Test with LLM mode if available
    if is_llm_enabled():
        print("\n=== Testing LLM Mode ===")
        llm_agent = ResumeProcessingAgent(use_llm=True)
        llm_result = llm_agent.process_resume("sample_resume.txt", sample_content)
        print(f"Processing method: {llm_result['processing_method']}")
        print(f"Name extracted: {llm_result['personal_info'].get('name', 'Not found')}")
    else:
        print("\n=== LLM Mode Not Available ===")
        print("No API key configured or AutoGen not installed")


if __name__ == "__main__":
    test_resume_processing()
