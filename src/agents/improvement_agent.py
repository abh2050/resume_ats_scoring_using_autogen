"""
Improvement Recommendation Agent for ATS System
Provides actionable feedback and enhancement suggestions
"""

import autogen
from typing import Dict, List, Any, Optional, Tuple
import json
from datetime import datetime
import re


class ImprovementRecommendationAgent:
    """
    AutoGen agent for generating specific improvement recommendations
    """
    
    def __init__(self, config_list: List[Dict[str, Any]]):
        self.config_list = config_list
        self.recommendation_history = []
        
        # Create the AutoGen agent
        self.agent = autogen.AssistantAgent(
            name="Improvement_Recommendation_Agent",
            llm_config={"config_list": config_list},
            system_message="""You are an expert Improvement Recommendation Agent specializing in:
            
            1. ACTIONABLE FEEDBACK:
            - Provide specific, implementable suggestions
            - Prioritize recommendations by impact
            - Offer concrete examples and alternatives
            - Include before/after comparisons where relevant
            
            2. CONTENT OPTIMIZATION:
            - Keyword enhancement strategies
            - Skill presentation improvements
            - Achievement quantification techniques
            - Format and structure refinements
            
            3. ATS OPTIMIZATION:
            - Keyword density improvements
            - Section organization recommendations
            - Format compatibility suggestions
            - Parsing-friendly formatting tips
            
            4. CAREER DEVELOPMENT:
            - Skill gap identification and closure strategies
            - Professional development recommendations
            - Industry trend alignment suggestions
            - Certification and training recommendations
            
            Focus on practical, immediately actionable advice that candidates
            can implement to improve their ATS scores and overall resume effectiveness."""
        )
    
    def generate_improvements(self, resume_data: Dict[str, Any], 
                            scoring_result: Any,
                            job_requirements: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate comprehensive improvement recommendations
        
        Args:
            resume_data: Processed resume data
            scoring_result: ATS scoring results
            job_requirements: Job requirements for targeted recommendations
            
        Returns:
            Comprehensive improvement recommendations
        """
        
        # Prepare context for recommendation generation
        improvement_context = {
            "overall_score": scoring_result.overall_score,
            "category_scores": scoring_result.category_scores,
            "weakest_areas": self._identify_weakest_areas(scoring_result.category_scores),
            "missing_elements": scoring_result.detailed_breakdown.get("missing_elements", []),
            "job_targeted": job_requirements is not None
        }
        
        # Generate different types of recommendations
        recommendations = {
            "priority_actions": self._generate_priority_actions(
                resume_data, scoring_result, job_requirements
            ),
            "content_improvements": self._generate_content_improvements(
                resume_data, scoring_result, job_requirements
            ),
            "format_enhancements": self._generate_format_enhancements(
                resume_data, scoring_result
            ),
            "keyword_optimization": self._generate_keyword_recommendations(
                resume_data, job_requirements
            ),
            "skill_development": self._generate_skill_development_recommendations(
                resume_data, job_requirements
            ),
            "section_specific": self._generate_section_specific_recommendations(
                resume_data, scoring_result
            ),
            "before_after_examples": self._generate_before_after_examples(
                resume_data, scoring_result
            ),
            "quick_wins": self._generate_quick_wins(resume_data, scoring_result),
            "long_term_strategy": self._generate_long_term_strategy(
                resume_data, job_requirements
            )
        }
        
        # Add metadata
        recommendations["metadata"] = {
            "generation_timestamp": datetime.now().isoformat(),
            "recommendation_count": sum(len(v) if isinstance(v, list) else 1 
                                      for v in recommendations.values() if v),
            "improvement_context": improvement_context,
            "score_improvement_potential": self._estimate_improvement_potential(
                scoring_result.category_scores
            )
        }
        
        # Log recommendation generation
        self._log_recommendation_generation(resume_data, scoring_result, recommendations)
        
        return recommendations
    
    def _identify_weakest_areas(self, category_scores: Dict[str, float]) -> List[str]:
        """Identify the weakest scoring areas for prioritization"""
        
        sorted_scores = sorted(category_scores.items(), key=lambda x: x[1])
        return [category for category, score in sorted_scores if score < 70]
    
    def _generate_priority_actions(self, resume_data: Dict[str, Any], 
                                 scoring_result: Any,
                                 job_requirements: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Generate top priority actions for immediate improvement"""
        
        priority_actions = []
        category_scores = scoring_result.category_scores
        
        # Priority 1: Address lowest scoring category
        lowest_category = min(category_scores.items(), key=lambda x: x[1])
        
        if lowest_category[1] < 60:
            if lowest_category[0] == "skills_match":
                priority_actions.append({
                    "priority": 1,
                    "category": "Skills Enhancement",
                    "action": "Add missing technical skills",
                    "description": "Your skills section needs immediate attention. Add 3-5 relevant technical skills that match job requirements.",
                    "impact": "High",
                    "effort": "Low",
                    "timeline": "1-2 hours"
                })
            
            elif lowest_category[0] == "experience_relevance":
                priority_actions.append({
                    "priority": 1,
                    "category": "Experience Enhancement", 
                    "action": "Quantify achievements",
                    "description": "Add numbers, percentages, or metrics to your accomplishments. Use action verbs and specific results.",
                    "impact": "High",
                    "effort": "Medium",
                    "timeline": "3-4 hours"
                })
            
            elif lowest_category[0] == "format_structure":
                priority_actions.append({
                    "priority": 1,
                    "category": "Format Improvement",
                    "action": "Restructure resume sections",
                    "description": "Improve resume organization with clear headers, consistent formatting, and proper section order.",
                    "impact": "Medium",
                    "effort": "Medium", 
                    "timeline": "2-3 hours"
                })
        
        # Priority 2: Address missing critical elements
        missing_elements = scoring_result.detailed_breakdown.get("missing_elements", [])
        if "LinkedIn profile URL" in missing_elements:
            priority_actions.append({
                "priority": 2,
                "category": "Contact Information",
                "action": "Add LinkedIn profile",
                "description": "Include your LinkedIn profile URL in the contact section.",
                "impact": "Medium",
                "effort": "Low",
                "timeline": "15 minutes"
            })
        
        # Priority 3: Job-specific improvements
        if job_requirements:
            missing_skills = self._identify_missing_job_skills(resume_data, job_requirements)
            if missing_skills:
                priority_actions.append({
                    "priority": 3,
                    "category": "Job Targeting",
                    "action": f"Add job-specific skills: {', '.join(missing_skills[:3])}",
                    "description": "Include skills specifically mentioned in the job description to improve match rate.",
                    "impact": "High",
                    "effort": "Low",
                    "timeline": "30 minutes"
                })
        
        return priority_actions
    
    def _generate_content_improvements(self, resume_data: Dict[str, Any],
                                     scoring_result: Any,
                                     job_requirements: Dict[str, Any] = None) -> Dict[str, List[str]]:
        """Generate content-specific improvement recommendations"""
        
        improvements = {
            "professional_summary": [],
            "experience_section": [],
            "skills_section": [],
            "education_section": [],
            "achievements": []
        }
        
        # Professional summary improvements
        summary = resume_data.get("professional_summary", "")
        if not summary or summary == "Not extracted":
            improvements["professional_summary"].append(
                "Add a compelling professional summary (2-3 sentences) highlighting your key qualifications"
            )
        elif len(summary.split()) < 20:
            improvements["professional_summary"].append(
                "Expand your professional summary to 20-30 words with specific value propositions"
            )
        
        # Experience improvements
        experience = resume_data.get("experience", [])
        if experience:
            for exp in experience:
                responsibilities = exp.get("responsibilities", [])
                achievements = exp.get("achievements", [])
                
                if len(responsibilities) < 3:
                    improvements["experience_section"].append(
                        f"Add more responsibilities for {exp.get('title', 'position')} role (aim for 3-5 bullet points)"
                    )
                
                if not achievements:
                    improvements["experience_section"].append(
                        f"Add quantified achievements for {exp.get('title', 'position')} with specific metrics"
                    )
                
                # Check for weak action verbs
                weak_verbs = ["responsible for", "helped", "worked on", "assisted"]
                for resp in responsibilities:
                    if any(weak_verb in resp.lower() for weak_verb in weak_verbs):
                        improvements["experience_section"].append(
                            "Replace weak phrases like 'responsible for' with strong action verbs like 'led', 'developed', 'implemented'"
                        )
                        break
        
        # Skills improvements
        skills = resume_data.get("skills", {})
        if not any(skills.values()):
            improvements["skills_section"].append(
                "Add a comprehensive skills section with technical and soft skills"
            )
        else:
            tech_skills = skills.get("technical_skills", [])
            if len(tech_skills) < 5:
                improvements["skills_section"].append(
                    "Expand technical skills section (aim for 8-12 relevant skills)"
                )
            
            if not skills.get("certifications"):
                improvements["skills_section"].append(
                    "Add relevant certifications or professional qualifications"
                )
        
        return improvements
    
    def _generate_format_enhancements(self, resume_data: Dict[str, Any],
                                    scoring_result: Any) -> List[Dict[str, str]]:
        """Generate format and structure enhancement recommendations"""
        
        enhancements = []
        
        # Check section completeness
        required_sections = ["personal_info", "experience", "education", "skills"]
        missing_sections = [section for section in required_sections 
                          if not resume_data.get(section)]
        
        if missing_sections:
            enhancements.append({
                "type": "Section Structure",
                "recommendation": f"Add missing sections: {', '.join(missing_sections)}",
                "importance": "High"
            })
        
        # Contact information completeness
        personal_info = resume_data.get("personal_info", {})
        missing_contact = []
        
        if not personal_info.get("email") or personal_info.get("email") == "Not specified":
            missing_contact.append("email address")
        if not personal_info.get("phone") or personal_info.get("phone") == "Not specified":
            missing_contact.append("phone number")
        
        if missing_contact:
            enhancements.append({
                "type": "Contact Information",
                "recommendation": f"Complete contact information: add {', '.join(missing_contact)}",
                "importance": "High"
            })
        
        # Date formatting
        experience = resume_data.get("experience", [])
        inconsistent_dates = False
        for exp in experience:
            start_date = exp.get("start_date", "")
            end_date = exp.get("end_date", "")
            
            if start_date and not re.match(r'\d{2}/\d{4}', start_date):
                inconsistent_dates = True
                break
        
        if inconsistent_dates:
            enhancements.append({
                "type": "Date Formatting",
                "recommendation": "Use consistent date format (MM/YYYY) throughout the resume",
                "importance": "Medium"
            })
        
        # ATS-friendly formatting
        enhancements.append({
            "type": "ATS Optimization",
            "recommendation": "Use standard section headers: 'Experience', 'Education', 'Skills', 'Contact Information'",
            "importance": "Medium"
        })
        
        enhancements.append({
            "type": "File Format",
            "recommendation": "Save resume as both PDF and Word formats for different ATS systems",
            "importance": "Medium"
        })
        
        return enhancements
    
    def _generate_keyword_recommendations(self, resume_data: Dict[str, Any],
                                        job_requirements: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate keyword optimization recommendations"""
        
        recommendations = {
            "missing_keywords": [],
            "keyword_placement": [],
            "density_optimization": [],
            "industry_keywords": []
        }
        
        if job_requirements:
            # Extract current resume text
            resume_text = self._extract_resume_text(resume_data).lower()
            
            # Identify missing job keywords
            job_keywords = job_requirements.get("keywords", [])
            required_skills = job_requirements.get("required_skills", [])
            
            all_target_keywords = list(set(job_keywords + required_skills))
            
            missing_keywords = []
            for keyword in all_target_keywords:
                if keyword.lower() not in resume_text:
                    missing_keywords.append(keyword)
            
            if missing_keywords:
                recommendations["missing_keywords"] = missing_keywords[:10]  # Top 10 missing
                
                recommendations["keyword_placement"].append(
                    "Integrate missing keywords naturally into your experience descriptions"
                )
                recommendations["keyword_placement"].append(
                    "Add relevant keywords to your skills section"
                )
                recommendations["keyword_placement"].append(
                    "Include keywords in your professional summary"
                )
        
        # General keyword optimization
        recommendations["density_optimization"] = [
            "Aim for 2-3% keyword density (not too high to avoid keyword stuffing)",
            "Use keyword variations and synonyms",
            "Include both acronyms and full forms (e.g., 'AI' and 'Artificial Intelligence')"
        ]
        
        # Industry-specific keywords
        recommendations["industry_keywords"] = [
            "Research industry-specific terminology and include relevant terms",
            "Add emerging technology keywords relevant to your field",
            "Include soft skills keywords like 'leadership', 'collaboration', 'problem-solving'"
        ]
        
        return recommendations
    
    def _generate_skill_development_recommendations(self, resume_data: Dict[str, Any],
                                                  job_requirements: Dict[str, Any] = None) -> Dict[str, List[str]]:
        """Generate skill development and career growth recommendations"""
        
        recommendations = {
            "immediate_skills": [],
            "certifications": [],
            "long_term_development": [],
            "learning_resources": []
        }
        
        current_skills = self._extract_all_skills(resume_data)
        
        if job_requirements:
            # Skills gap analysis
            required_skills = job_requirements.get("required_skills", [])
            preferred_skills = job_requirements.get("preferred_skills", [])
            
            missing_required = [skill for skill in required_skills 
                              if skill.lower() not in [s.lower() for s in current_skills]]
            missing_preferred = [skill for skill in preferred_skills
                               if skill.lower() not in [s.lower() for s in current_skills]]
            
            if missing_required:
                recommendations["immediate_skills"] = [
                    f"Priority skill to develop: {skill}" for skill in missing_required[:3]
                ]
            
            if missing_preferred:
                recommendations["long_term_development"] = [
                    f"Consider learning: {skill} for competitive advantage" 
                    for skill in missing_preferred[:5]
                ]
            
            # Certification recommendations
            certifications = job_requirements.get("education_requirements", {}).get("certifications", [])
            if certifications:
                recommendations["certifications"] = [
                    f"Consider pursuing: {cert}" for cert in certifications[:3]
                ]
        
        # General skill development
        if "python" in [s.lower() for s in current_skills]:
            recommendations["learning_resources"].append(
                "Advance Python skills with frameworks like Django, Flask, or FastAPI"
            )
        
        if "javascript" in [s.lower() for s in current_skills]:
            recommendations["learning_resources"].append(
                "Expand JavaScript knowledge with modern frameworks like React, Vue, or Angular"
            )
        
        # Emerging skills recommendations
        recommendations["long_term_development"].extend([
            "Consider cloud computing skills (AWS, Azure, GCP)",
            "Explore AI/ML fundamentals if relevant to your field",
            "Develop data analysis skills (SQL, Excel, Python)"
        ])
        
        return recommendations
    
    def _generate_section_specific_recommendations(self, resume_data: Dict[str, Any],
                                                 scoring_result: Any) -> Dict[str, List[str]]:
        """Generate section-specific improvement recommendations"""
        
        recommendations = {
            "contact_section": [],
            "summary_section": [],
            "experience_section": [],
            "education_section": [],
            "skills_section": [],
            "additional_sections": []
        }
        
        # Contact section
        personal_info = resume_data.get("personal_info", {})
        if not personal_info.get("linkedin"):
            recommendations["contact_section"].append("Add LinkedIn profile URL")
        if not personal_info.get("location"):
            recommendations["contact_section"].append("Include city and state/country")
        
        # Experience section
        experience = resume_data.get("experience", [])
        if len(experience) < 2:
            recommendations["experience_section"].append(
                "Include more work experience entries (even internships or projects)"
            )
        
        for exp in experience:
            if not exp.get("achievements"):
                recommendations["experience_section"].append(
                    "Add quantified achievements for each role"
                )
                break
        
        # Education section
        education = resume_data.get("education", [])
        if not education:
            recommendations["education_section"].append(
                "Add education information (degree, institution, graduation year)"
            )
        
        # Skills section organization
        skills = resume_data.get("skills", {})
        if not skills.get("technical_skills"):
            recommendations["skills_section"].append("Add technical skills category")
        if not skills.get("soft_skills"):
            recommendations["skills_section"].append("Add soft skills category")
        
        # Additional sections
        if not resume_data.get("projects"):
            recommendations["additional_sections"].append(
                "Consider adding a Projects section to showcase relevant work"
            )
        
        additional = resume_data.get("additional_sections", {})
        if not additional.get("certifications") and not skills.get("certifications"):
            recommendations["additional_sections"].append(
                "Add relevant certifications or professional qualifications"
            )
        
        return recommendations
    
    def _generate_before_after_examples(self, resume_data: Dict[str, Any],
                                      scoring_result: Any) -> List[Dict[str, str]]:
        """Generate before/after examples for improvements"""
        
        examples = []
        
        # Experience bullet point examples
        experience = resume_data.get("experience", [])
        if experience:
            for exp in experience:
                responsibilities = exp.get("responsibilities", [])
                if responsibilities:
                    weak_bullet = next((resp for resp in responsibilities 
                                      if any(weak in resp.lower() for weak in ["responsible for", "helped", "worked on"])), None)
                    
                    if weak_bullet:
                        examples.append({
                            "section": "Experience",
                            "before": weak_bullet,
                            "after": "Led development of web application features, resulting in 25% increase in user engagement",
                            "improvement": "Use strong action verbs and quantify results"
                        })
                        break
        
        # Skills section example
        skills = resume_data.get("skills", {})
        tech_skills = skills.get("technical_skills", [])
        if len(tech_skills) < 5:
            examples.append({
                "section": "Skills", 
                "before": "Programming: Python, JavaScript",
                "after": "Programming Languages: Python, JavaScript, SQL, HTML/CSS\nFrameworks: React, Django, Flask\nTools: Git, Docker, AWS",
                "improvement": "Organize skills by category and include more specific technologies"
            })
        
        # Professional summary example
        summary = resume_data.get("professional_summary", "")
        if not summary or len(summary.split()) < 15:
            examples.append({
                "section": "Professional Summary",
                "before": "Software engineer with experience in web development.",
                "after": "Results-driven Software Engineer with 5+ years developing scalable web applications. Proven track record of improving system performance by 40% and leading cross-functional teams of 5+ developers.",
                "improvement": "Include specific years of experience, quantified achievements, and key strengths"
            })
        
        return examples
    
    def _generate_quick_wins(self, resume_data: Dict[str, Any],
                           scoring_result: Any) -> List[Dict[str, str]]:
        """Generate quick wins that can be implemented immediately"""
        
        quick_wins = []
        
        # Missing contact information
        personal_info = resume_data.get("personal_info", {})
        if not personal_info.get("linkedin"):
            quick_wins.append({
                "action": "Add LinkedIn Profile",
                "description": "Include your LinkedIn URL in the contact section",
                "time_required": "2 minutes",
                "impact": "Medium"
            })
        
        # Skills formatting
        skills = resume_data.get("skills", {})
        if skills.get("technical_skills") and len(skills["technical_skills"]) > 0:
            # Check if skills are properly capitalized
            if any(skill.islower() for skill in skills["technical_skills"]):
                quick_wins.append({
                    "action": "Capitalize Skill Names",
                    "description": "Ensure all skill names are properly capitalized (e.g., 'Python' not 'python')",
                    "time_required": "5 minutes",
                    "impact": "Low"
                })
        
        # Date consistency
        experience = resume_data.get("experience", [])
        if experience:
            inconsistent_dates = any(
                exp.get("start_date") and not re.match(r'\d{1,2}/\d{4}', exp.get("start_date", ""))
                for exp in experience
            )
            if inconsistent_dates:
                quick_wins.append({
                    "action": "Standardize Date Format",
                    "description": "Use MM/YYYY format consistently for all dates",
                    "time_required": "5 minutes",
                    "impact": "Medium"
                })
        
        # Email format
        email = personal_info.get("email", "")
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            quick_wins.append({
                "action": "Fix Email Format",
                "description": "Ensure email address is properly formatted",
                "time_required": "1 minute",
                "impact": "High"
            })
        
        return quick_wins
    
    def _generate_long_term_strategy(self, resume_data: Dict[str, Any],
                                   job_requirements: Dict[str, Any] = None) -> Dict[str, List[str]]:
        """Generate long-term career development strategy"""
        
        strategy = {
            "skill_development_path": [],
            "experience_building": [],
            "networking_recommendations": [],
            "certification_roadmap": [],
            "industry_positioning": []
        }
        
        current_experience = resume_data.get("experience", [])
        years_experience = self._estimate_total_experience(current_experience)
        
        # Experience-based recommendations
        if years_experience < 2:
            strategy["experience_building"] = [
                "Focus on building foundational experience in core technologies",
                "Seek mentorship opportunities with senior developers",
                "Contribute to open-source projects to build portfolio",
                "Consider internships or entry-level positions for experience"
            ]
        elif years_experience < 5:
            strategy["experience_building"] = [
                "Take on leadership roles in projects",
                "Develop expertise in specific technology domains",
                "Start mentoring junior team members",
                "Pursue complex technical challenges and solutions"
            ]
        else:
            strategy["experience_building"] = [
                "Focus on strategic technical leadership",
                "Drive architectural decisions and technology adoption",
                "Build cross-functional collaboration skills",
                "Consider management or technical lead opportunities"
            ]
        
        # Industry positioning
        if job_requirements:
            industry = job_requirements.get("company_info", {}).get("industry", "technology")
            
            if industry == "technology":
                strategy["industry_positioning"] = [
                    "Stay current with emerging technology trends",
                    "Build expertise in cloud technologies and DevOps",
                    "Develop understanding of AI/ML applications",
                    "Focus on scalable system design and architecture"
                ]
            elif industry == "finance":
                strategy["industry_positioning"] = [
                    "Understand financial domain and regulatory requirements",
                    "Develop expertise in security and compliance",
                    "Learn about fintech trends and blockchain technology",
                    "Focus on high-performance, reliable system development"
                ]
        
        # Networking recommendations
        strategy["networking_recommendations"] = [
            "Join professional associations in your field",
            "Attend industry conferences and meetups",
            "Engage actively on LinkedIn with industry content",
            "Build relationships with colleagues and industry peers",
            "Consider speaking at conferences or writing technical blogs"
        ]
        
        return strategy
    
    def _extract_all_skills(self, resume_data: Dict[str, Any]) -> List[str]:
        """Extract all skills from resume data"""
        
        skills = resume_data.get("skills", {})
        all_skills = []
        
        for skill_category in skills.values():
            if isinstance(skill_category, list):
                all_skills.extend(skill_category)
        
        return all_skills
    
    def _extract_resume_text(self, resume_data: Dict[str, Any]) -> str:
        """Extract all text content from resume data"""
        
        text_parts = []
        
        for section_name, section_data in resume_data.items():
            if section_name == "metadata":
                continue
                
            if isinstance(section_data, str):
                text_parts.append(section_data)
            elif isinstance(section_data, dict):
                for value in section_data.values():
                    if isinstance(value, str):
                        text_parts.append(value)
                    elif isinstance(value, list):
                        text_parts.extend([str(item) for item in value])
            elif isinstance(section_data, list):
                for item in section_data:
                    if isinstance(item, dict):
                        for value in item.values():
                            if isinstance(value, str):
                                text_parts.append(value)
                            elif isinstance(value, list):
                                text_parts.extend([str(subitem) for subitem in value])
                    else:
                        text_parts.append(str(item))
        
        return " ".join(text_parts)
    
    def _identify_missing_job_skills(self, resume_data: Dict[str, Any],
                                   job_requirements: Dict[str, Any]) -> List[str]:
        """Identify skills mentioned in job requirements but missing from resume"""
        
        resume_skills = [skill.lower() for skill in self._extract_all_skills(resume_data)]
        required_skills = [skill.lower() for skill in job_requirements.get("required_skills", [])]
        
        return [skill for skill in required_skills if skill not in resume_skills]
    
    def _estimate_total_experience(self, experience: List[Dict[str, Any]]) -> float:
        """Estimate total years of experience"""
        
        total_years = 0.0
        
        for exp in experience:
            start_date = exp.get("start_date", "")
            end_date = exp.get("end_date", "Present")
            
            if start_date:
                try:
                    start_parts = start_date.split("/")
                    if len(start_parts) >= 2:
                        start_year = int(start_parts[-1])
                        
                        if end_date.lower() == "present":
                            end_year = datetime.now().year
                        else:
                            end_parts = end_date.split("/")
                            end_year = int(end_parts[-1]) if len(end_parts) >= 2 else start_year
                        
                        years = end_year - start_year
                        total_years += max(years, 0)
                
                except (ValueError, IndexError):
                    continue
        
        return total_years
    
    def _estimate_improvement_potential(self, category_scores: Dict[str, float]) -> Dict[str, float]:
        """Estimate potential score improvement by category"""
        
        potential = {}
        
        for category, score in category_scores.items():
            if score < 50:
                potential[category] = 30  # High improvement potential
            elif score < 70:
                potential[category] = 20  # Medium improvement potential
            elif score < 85:
                potential[category] = 10  # Low improvement potential
            else:
                potential[category] = 5   # Minimal improvement potential
        
        return potential
    
    def _log_recommendation_generation(self, resume_data: Dict[str, Any],
                                     scoring_result: Any,
                                     recommendations: Dict[str, Any]):
        """Log recommendation generation for tracking"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "initial_score": scoring_result.overall_score,
            "recommendation_count": recommendations["metadata"]["recommendation_count"],
            "weakest_areas": self._identify_weakest_areas(scoring_result.category_scores),
            "has_job_requirements": recommendations["metadata"]["improvement_context"]["job_targeted"]
        }
        
        self.recommendation_history.append(log_entry)
    
    def get_recommendation_statistics(self) -> Dict[str, Any]:
        """Get recommendation generation statistics"""
        
        if not self.recommendation_history:
            return {"message": "No recommendation history available"}
        
        total_recommendations = len(self.recommendation_history)
        avg_score = sum(log["initial_score"] for log in self.recommendation_history) / total_recommendations
        avg_recommendations = sum(log["recommendation_count"] for log in self.recommendation_history) / total_recommendations
        
        stats = {
            "total_recommendations_generated": total_recommendations,
            "average_initial_score": avg_score,
            "average_recommendations_per_resume": avg_recommendations,
            "job_targeted_percentage": len([log for log in self.recommendation_history 
                                          if log["has_job_requirements"]]) / total_recommendations * 100,
            "common_weak_areas": self._get_common_weak_areas()
        }
        
        return stats
    
    def _get_common_weak_areas(self) -> Dict[str, int]:
        """Get most common weak areas across all recommendations"""
        
        weak_area_counts = {}
        
        for log in self.recommendation_history:
            for area in log["weakest_areas"]:
                weak_area_counts[area] = weak_area_counts.get(area, 0) + 1
        
        return dict(sorted(weak_area_counts.items(), key=lambda x: x[1], reverse=True))


# Example usage and testing
def test_improvement_agent():
    """Test function for the Improvement Recommendation Agent"""
    
    # Mock config
    config_list = [
        {
            "model": "gpt-4",
            "api_key": "your-api-key-here",
            "base_url": "https://api.openai.com/v1",
        }
    ]
    
    # Mock resume data
    sample_resume = {
        "personal_info": {"name": "John Doe", "email": "john@email.com"},
        "experience": [{"title": "Developer", "responsibilities": ["Worked on web apps"]}],
        "skills": {"technical_skills": ["Python", "JavaScript"]},
        "education": [{"degree": "BS Computer Science"}]
    }
    
    # Mock scoring result
    class MockScoringResult:
        overall_score = 65
        category_scores = {
            "skills_match": 60,
            "experience_relevance": 55,
            "education_alignment": 75,
            "format_structure": 70,
            "keyword_optimization": 65
        }
        detailed_breakdown = {"missing_elements": ["LinkedIn profile URL"]}
    
    mock_result = MockScoringResult()
    
    # Initialize improvement agent
    improvement_agent = ImprovementRecommendationAgent(config_list)
    
    # Generate recommendations
    recommendations = improvement_agent.generate_improvements(
        sample_resume, mock_result
    )
    
    print("Improvement Recommendations Generated:")
    print(json.dumps(recommendations, indent=2))


if __name__ == "__main__":
    test_improvement_agent()
