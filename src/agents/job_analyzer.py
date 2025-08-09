"""
Job Description Analyzer Agent for ATS System
Extracts requirements and creates matching criteria from job descriptions
"""

import autogen
from typing import Dict, List, Any, Optional
import json
import re
from datetime import datetime


class JobDescriptionAnalyzer:
    """
    AutoGen agent for analyzing job descriptions and extracting requirements
    """
    
    def __init__(self, config_list: List[Dict[str, Any]]):
        self.config_list = config_list
        self.analysis_history = []
        
        # Create the AutoGen agent
        self.agent = autogen.AssistantAgent(
            name="Job_Description_Analyzer",
            llm_config={"config_list": config_list},
            system_message="""You are a specialized Job Description Analyzer with expertise in:
            
            1. REQUIREMENT EXTRACTION:
            - Identify must-have vs. nice-to-have skills
            - Extract years of experience requirements
            - Determine education requirements
            - Identify industry-specific keywords
            
            2. SKILL CATEGORIZATION:
            - Technical skills (programming, tools, technologies)
            - Soft skills (communication, leadership, teamwork)
            - Domain expertise (industry knowledge, certifications)
            - Experience levels (junior, mid-level, senior)
            
            3. MATCHING CRITERIA DEVELOPMENT:
            - Create weighted matching criteria
            - Define minimum qualification thresholds
            - Establish scoring priorities
            - Generate keyword lists for ATS optimization
            
            4. CONTEXT ANALYSIS:
            - Company culture indicators
            - Role responsibilities and expectations
            - Career growth opportunities
            - Compensation and benefits insights
            
            Provide structured, actionable analysis that can be used for precise
            resume matching and candidate evaluation."""
        )
    
    def analyze_job_description(self, job_description: str, industry: str = "general") -> Dict[str, Any]:
        """
        Analyze a job description and extract structured requirements
        
        Args:
            job_description: Raw job description text
            industry: Industry context for analysis
            
        Returns:
            Structured job requirements and matching criteria
        """
        
        analysis_prompt = f"""
        Analyze the following job description and extract structured requirements.
        Provide a comprehensive analysis in JSON format.
        
        JOB DESCRIPTION:
        {job_description}
        
        Please structure your analysis as follows:
        {{
            "job_title": "Extracted job title",
            "company_info": {{
                "company_name": "Company name if mentioned",
                "industry": "Industry/sector",
                "company_size": "Company size indicators"
            }},
            "required_skills": [
                "List of must-have technical skills"
            ],
            "preferred_skills": [
                "List of nice-to-have skills"
            ],
            "required_experience": {{
                "years_required": "Minimum years of experience",
                "experience_type": "Type of experience required",
                "specific_domains": ["Specific experience domains"]
            }},
            "education_requirements": {{
                "required_degree": "Minimum education requirement",
                "preferred_degree": "Preferred education level", 
                "relevant_fields": ["Relevant fields of study"],
                "certifications": ["Required or preferred certifications"]
            }},
            "technical_requirements": {{
                "programming_languages": ["Programming languages mentioned"],
                "frameworks_libraries": ["Frameworks and libraries"],
                "tools_technologies": ["Tools and technologies"],
                "databases": ["Database technologies"],
                "cloud_platforms": ["Cloud platforms"]
            }},
            "soft_skills": [
                "Communication, leadership, and other soft skills"
            ],
            "responsibilities": [
                "Key job responsibilities extracted"
            ],
            "qualifications": [
                "All qualification requirements"
            ],
            "keywords": [
                "Important keywords for ATS optimization"
            ],
            "experience_level": "Junior/Mid-level/Senior/Executive",
            "employment_type": "Full-time/Part-time/Contract/etc.",
            "location": "Job location information",
            "remote_options": "Remote work options",
            "salary_range": "Salary information if mentioned",
            "benefits": [
                "Benefits and perks mentioned"
            ],
            "company_culture": [
                "Company culture indicators"
            ],
            "scoring_weights": {{
                "technical_skills_weight": 0.4,
                "experience_weight": 0.3,
                "education_weight": 0.15,
                "soft_skills_weight": 0.15
            }},
            "matching_criteria": {{
                "minimum_skill_match": "Percentage of required skills needed",
                "experience_flexibility": "Flexibility in experience requirements",
                "education_flexibility": "Flexibility in education requirements"
            }}
        }}
        
        ANALYSIS GUIDELINES:
        1. Extract information exactly as stated in the job description
        2. Distinguish between required (must-have) and preferred (nice-to-have)
        3. Identify implicit requirements that may not be explicitly stated
        4. Consider industry context: {industry}
        5. Prioritize skills and requirements based on emphasis in the text
        6. Generate comprehensive keyword list for ATS optimization
        
        Return only the JSON object, no additional text.
        """
        
        # Use the AutoGen agent to process the analysis
        user_proxy = autogen.UserProxyAgent(
            name="User",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0,
            code_execution_config=False
        )
        
        # Initiate conversation for analysis
        try:
            response = user_proxy.initiate_chat(
                self.agent,
                message=analysis_prompt,
                silent=True
            )
            
            # Extract JSON from response
            last_message = response.chat_history[-1]['content']
            
            # Extract JSON from the response
            json_start = last_message.find('{')
            json_end = last_message.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = last_message[json_start:json_end]
                analysis_result = json.loads(json_str)
                
                # Add metadata
                analysis_result['analysis_metadata'] = {
                    'analysis_timestamp': datetime.now().isoformat(),
                    'analyzer_version': '1.0',
                    'industry_context': industry,
                    'text_length': len(job_description),
                    'extraction_method': 'llm_analysis'
                }
                
                # Log the analysis
                self._log_analysis(job_description, analysis_result)
                
                return analysis_result
            else:
                raise ValueError("No valid JSON found in response")
                
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback to basic parsing if LLM analysis fails
            return self._fallback_analysis(job_description, industry)
    
    def _fallback_analysis(self, job_description: str, industry: str) -> Dict[str, Any]:
        """
        Fallback analysis method using regex patterns
        Used when LLM analysis fails
        """
        
        text = job_description.lower()
        
        # Extract technical skills using common patterns
        tech_skills = []
        skill_patterns = [
            r'\b(python|java|javascript|react|angular|node\.js|sql|mongodb|aws|docker|kubernetes)\b',
            r'\b(machine learning|ai|data science|deep learning|nlp|computer vision)\b',
            r'\b(git|github|linux|windows|agile|scrum|devops|ci/cd)\b'
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, text)
            tech_skills.extend(matches)
        
        # Extract experience requirements
        experience_pattern = r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)'
        experience_matches = re.findall(experience_pattern, text)
        years_required = max([int(match) for match in experience_matches], default=0)
        
        # Extract education requirements
        education_keywords = ['bachelor', 'master', 'phd', 'degree', 'diploma', 'certification']
        education_found = [keyword for keyword in education_keywords if keyword in text]
        
        # Fallback structure
        fallback_result = {
            "job_title": "Not extracted",
            "company_info": {
                "company_name": "Not specified",
                "industry": industry,
                "company_size": "Not specified"
            },
            "required_skills": list(set(tech_skills)),
            "preferred_skills": [],
            "required_experience": {
                "years_required": str(years_required) if years_required > 0 else "Not specified",
                "experience_type": "Not specified",
                "specific_domains": []
            },
            "education_requirements": {
                "required_degree": education_found[0].title() if education_found else "Not specified",
                "preferred_degree": "Not specified",
                "relevant_fields": [],
                "certifications": []
            },
            "technical_requirements": {
                "programming_languages": [skill for skill in tech_skills 
                                        if skill in ['python', 'java', 'javascript']],
                "frameworks_libraries": [skill for skill in tech_skills 
                                       if skill in ['react', 'angular', 'node.js']],
                "tools_technologies": [skill for skill in tech_skills 
                                     if skill in ['docker', 'kubernetes', 'git']],
                "databases": [skill for skill in tech_skills if 'sql' in skill],
                "cloud_platforms": [skill for skill in tech_skills if skill in ['aws', 'azure', 'gcp']]
            },
            "soft_skills": [],
            "responsibilities": [],
            "qualifications": [],
            "keywords": list(set(tech_skills)),
            "experience_level": "Mid-level" if years_required >= 3 else "Junior",
            "employment_type": "Not specified",
            "location": "Not specified",
            "remote_options": "remote" in text,
            "salary_range": "Not specified",
            "benefits": [],
            "company_culture": [],
            "scoring_weights": {
                "technical_skills_weight": 0.4,
                "experience_weight": 0.3,
                "education_weight": 0.15,
                "soft_skills_weight": 0.15
            },
            "matching_criteria": {
                "minimum_skill_match": "70%",
                "experience_flexibility": "1-2 years",
                "education_flexibility": "Related field acceptable"
            },
            "analysis_metadata": {
                "analysis_timestamp": datetime.now().isoformat(),
                "analyzer_version": '1.0',
                "industry_context": industry,
                "text_length": len(job_description),
                "extraction_method": 'fallback_regex',
                "note": "Fallback analysis used due to LLM parsing failure"
            }
        }
        
        return fallback_result
    
    def create_matching_criteria(self, job_requirements: Dict[str, Any], 
                               strictness_level: str = "moderate") -> Dict[str, Any]:
        """
        Create detailed matching criteria based on job requirements
        
        Args:
            job_requirements: Analyzed job requirements
            strictness_level: "strict", "moderate", or "flexible"
            
        Returns:
            Detailed matching criteria for resume scoring
        """
        
        strictness_multipliers = {
            "strict": {"skill_threshold": 0.9, "experience_factor": 1.0, "education_weight": 1.0},
            "moderate": {"skill_threshold": 0.7, "experience_factor": 0.8, "education_weight": 0.8},
            "flexible": {"skill_threshold": 0.5, "experience_factor": 0.6, "education_weight": 0.6}
        }
        
        multiplier = strictness_multipliers.get(strictness_level, strictness_multipliers["moderate"])
        
        matching_criteria = {
            "strictness_level": strictness_level,
            "skill_matching": {
                "required_skills": job_requirements.get("required_skills", []),
                "preferred_skills": job_requirements.get("preferred_skills", []),
                "minimum_match_threshold": multiplier["skill_threshold"],
                "skill_weights": {
                    "required_skills_weight": 0.7,
                    "preferred_skills_weight": 0.3
                }
            },
            "experience_matching": {
                "required_years": job_requirements.get("required_experience", {}).get("years_required", "0"),
                "experience_domains": job_requirements.get("required_experience", {}).get("specific_domains", []),
                "flexibility_range": int(float(job_requirements.get("required_experience", {}).get("years_required", "0")) * (1 - multiplier["experience_factor"])),
                "experience_level": job_requirements.get("experience_level", "Mid-level")
            },
            "education_matching": {
                "required_degree": job_requirements.get("education_requirements", {}).get("required_degree", ""),
                "preferred_degree": job_requirements.get("education_requirements", {}).get("preferred_degree", ""),
                "relevant_fields": job_requirements.get("education_requirements", {}).get("relevant_fields", []),
                "weight_factor": multiplier["education_weight"]
            },
            "keyword_optimization": {
                "primary_keywords": job_requirements.get("keywords", [])[:10],  # Top 10 keywords
                "secondary_keywords": job_requirements.get("keywords", [])[10:20],  # Next 10
                "keyword_density_target": 0.02,  # 2% keyword density target
                "must_have_keywords": job_requirements.get("required_skills", [])[:5]  # Top 5 required skills
            },
            "scoring_formula": {
                "weights": job_requirements.get("scoring_weights", {
                    "technical_skills_weight": 0.4,
                    "experience_weight": 0.3,
                    "education_weight": 0.15,
                    "soft_skills_weight": 0.15
                }),
                "bonus_factors": {
                    "exact_title_match": 10,
                    "industry_experience": 15,
                    "certification_bonus": 5,
                    "leadership_experience": 10
                }
            },
            "disqualifiers": {
                "missing_critical_skills": job_requirements.get("required_skills", [])[:3],  # Top 3 critical
                "insufficient_experience": strictness_level == "strict",
                "education_mismatch": strictness_level == "strict"
            }
        }
        
        return matching_criteria
    
    def extract_company_insights(self, job_description: str) -> Dict[str, Any]:
        """
        Extract company culture and workplace insights from job description
        
        Args:
            job_description: Raw job description text
            
        Returns:
            Company insights and culture indicators
        """
        
        insights_prompt = f"""
        Analyze the following job description for company culture and workplace insights.
        Focus on understanding the work environment, company values, and candidate fit indicators.
        
        JOB DESCRIPTION:
        {job_description}
        
        Provide analysis in JSON format:
        {{
            "company_culture": {{
                "work_environment": "Description of work environment",
                "company_values": ["List of company values mentioned"],
                "team_structure": "Team organization insights",
                "management_style": "Leadership and management approach"
            }},
            "growth_opportunities": {{
                "career_development": ["Career development opportunities"],
                "learning_opportunities": ["Learning and training mentioned"],
                "advancement_path": "Career advancement indicators"
            }},
            "work_life_balance": {{
                "flexibility": "Work flexibility indicators",
                "benefits": ["Benefits and perks mentioned"],
                "work_schedule": "Work schedule expectations"
            }},
            "collaboration_style": {{
                "team_size": "Team size indicators",
                "cross_functional_work": "Cross-team collaboration",
                "communication_style": "Communication preferences"
            }},
            "innovation_focus": {{
                "technology_adoption": "Technology and innovation emphasis",
                "research_development": "R&D and innovation opportunities",
                "continuous_improvement": "Process improvement culture"
            }},
            "candidate_fit_indicators": [
                "Key personality and work style preferences"
            ]
        }}
        
        Return only the JSON object.
        """
        
        try:
            user_proxy = autogen.UserProxyAgent(
                name="User",
                human_input_mode="NEVER",
                max_consecutive_auto_reply=0,
                code_execution_config=False
            )
            
            response = user_proxy.initiate_chat(
                self.agent,
                message=insights_prompt,
                silent=True
            )
            
            last_message = response.chat_history[-1]['content']
            json_start = last_message.find('{')
            json_end = last_message.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = last_message[json_start:json_end]
                return json.loads(json_str)
                
        except Exception as e:
            pass
        
        # Fallback insights
        return {
            "company_culture": {
                "work_environment": "Not specified",
                "company_values": [],
                "team_structure": "Not specified",
                "management_style": "Not specified"
            },
            "growth_opportunities": {
                "career_development": [],
                "learning_opportunities": [],
                "advancement_path": "Not specified"
            },
            "work_life_balance": {
                "flexibility": "Not specified",
                "benefits": [],
                "work_schedule": "Not specified"
            },
            "collaboration_style": {
                "team_size": "Not specified",
                "cross_functional_work": "Not specified",
                "communication_style": "Not specified"
            },
            "innovation_focus": {
                "technology_adoption": "Not specified",
                "research_development": "Not specified",
                "continuous_improvement": "Not specified"
            },
            "candidate_fit_indicators": []
        }
    
    def _log_analysis(self, job_description: str, analysis_result: Dict[str, Any]):
        """Log analysis for tracking and improvement"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "job_description_length": len(job_description),
            "analysis_success": True,
            "extracted_skills_count": len(analysis_result.get("required_skills", [])),
            "extraction_method": analysis_result.get("analysis_metadata", {}).get("extraction_method", "unknown")
        }
        
        self.analysis_history.append(log_entry)
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """Get analysis statistics for monitoring"""
        
        if not self.analysis_history:
            return {"message": "No analysis history available"}
        
        total_analyses = len(self.analysis_history)
        successful_analyses = len([log for log in self.analysis_history if log["analysis_success"]])
        
        avg_skills_extracted = sum(log["extracted_skills_count"] for log in self.analysis_history) / total_analyses
        
        stats = {
            "total_analyses": total_analyses,
            "success_rate": (successful_analyses / total_analyses) * 100,
            "average_skills_extracted": avg_skills_extracted,
            "extraction_methods": {
                "llm_analysis": len([log for log in self.analysis_history 
                                   if log.get("extraction_method") == "llm_analysis"]),
                "fallback_regex": len([log for log in self.analysis_history 
                                     if log.get("extraction_method") == "fallback_regex"])
            }
        }
        
        return stats


# Example usage and testing
def test_job_analyzer():
    """Test function for the Job Description Analyzer"""
    
    config_list = [
        {
            "model": "gpt-4",
            "api_key": "your-api-key-here",
            "base_url": "https://api.openai.com/v1",
        }
    ]
    
    # Sample job description
    sample_jd = """
    Senior Software Engineer - Full Stack Development
    
    Company: TechCorp Inc.
    Location: San Francisco, CA (Remote options available)
    
    About the role:
    We are seeking a Senior Software Engineer to join our dynamic team. You will be responsible
    for developing scalable web applications using modern technologies.
    
    Required Skills:
    - 5+ years of software development experience
    - Proficiency in Python, JavaScript, React
    - Experience with SQL databases and MongoDB
    - Knowledge of AWS cloud services
    - Strong problem-solving skills
    
    Preferred Skills:
    - Experience with Docker and Kubernetes
    - Knowledge of machine learning concepts
    - Leadership experience
    
    Education:
    - Bachelor's degree in Computer Science or related field
    - Master's degree preferred
    
    What we offer:
    - Competitive salary ($120k - $160k)
    - Health insurance and 401k
    - Flexible work arrangements
    - Professional development opportunities
    """
    
    # Initialize analyzer
    analyzer = JobDescriptionAnalyzer(config_list)
    
    # Analyze job description
    print("Analyzing job description...")
    analysis = analyzer.analyze_job_description(sample_jd, "technology")
    
    print("Analysis Results:")
    print(json.dumps(analysis, indent=2))
    
    # Create matching criteria
    print("\nCreating matching criteria...")
    criteria = analyzer.create_matching_criteria(analysis, "moderate")
    
    print("Matching Criteria:")
    print(json.dumps(criteria, indent=2))
    
    # Extract company insights
    print("\nExtracting company insights...")
    insights = analyzer.extract_company_insights(sample_jd)
    
    print("Company Insights:")
    print(json.dumps(insights, indent=2))


if __name__ == "__main__":
    test_job_analyzer()
