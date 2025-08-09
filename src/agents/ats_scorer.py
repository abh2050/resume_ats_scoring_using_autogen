"""
ATS Scoring Agent for Resume Evaluation
Implements consistent scoring algorithm with detailed breakdowns
"""

import autogen
from typing import Dict, List, Any, Optional, Tuple
import json
import hashlib
from datetime import datetime
import re
import numpy as np
from dataclasses import dataclass


@dataclass
class ScoringWeights:
    """Configuration class for scoring weights"""
    skills_match: float = 0.30          # 30%
    experience_relevance: float = 0.25   # 25%
    education_alignment: float = 0.15    # 15%
    format_structure: float = 0.15       # 15%
    keyword_optimization: float = 0.15   # 15%


@dataclass
class ScoreResult:
    """Data class for scoring results"""
    overall_score: float
    category_scores: Dict[str, float]
    detailed_breakdown: Dict[str, Any]
    confidence_interval: Tuple[float, float]
    consistency_hash: str
    benchmark_comparison: Dict[str, Any]
    recommendations: List[str]


class ATSScoringAgent:
    """
    AutoGen agent for consistent ATS resume scoring
    Provides detailed breakdowns and benchmark comparisons
    """
    
    def __init__(self, config_list: List[Dict[str, Any]], scoring_weights: ScoringWeights = None):
        self.config_list = config_list
        self.weights = scoring_weights or ScoringWeights()
        self.scoring_history = []
        self.consistency_cache = {}
        
        # Industry benchmarks (configurable)
        self.industry_benchmarks = {
            "technology": {"average_score": 75, "top_percentile": 90},
            "healthcare": {"average_score": 70, "top_percentile": 85},
            "finance": {"average_score": 78, "top_percentile": 92},
            "marketing": {"average_score": 72, "top_percentile": 87},
            "general": {"average_score": 70, "top_percentile": 85}
        }
        
        # Create the AutoGen agent
        self.agent = autogen.AssistantAgent(
            name="ATS_Scorer",
            llm_config={"config_list": config_list},
            system_message="""You are an expert ATS (Applicant Tracking System) Scoring Agent specializing in:
            
            1. CONSISTENT SCORING:
            - Apply standardized scoring criteria across all resumes
            - Ensure identical resumes receive identical scores
            - Maintain scoring consistency over time
            - Provide confidence intervals for score reliability
            
            2. DETAILED CATEGORY ANALYSIS:
            - Skills Match (30%): Alignment with required skills
            - Experience Relevance (25%): Quality and relevance of work experience
            - Education Alignment (15%): Educational background match
            - Format & Structure (15%): Resume formatting and organization
            - Keyword Optimization (15%): Presence of relevant keywords
            
            3. BENCHMARK COMPARISON:
            - Compare scores against industry standards
            - Identify percentile rankings
            - Provide competitive analysis context
            
            4. ACTIONABLE INSIGHTS:
            - Identify specific areas for improvement
            - Provide quantitative reasoning for scores
            - Suggest optimization strategies
            
            Maintain objectivity and consistency in all scoring decisions.
            Provide detailed explanations for score calculations."""
        )
    
    def score_resume(self, resume_data: Dict[str, Any], job_requirements: Dict[str, Any] = None, 
                    industry: str = "general") -> ScoreResult:
        """
        Score a resume using the consistent ATS algorithm
        
        Args:
            resume_data: Processed resume data in JSON format
            job_requirements: Optional job requirements for targeted scoring
            industry: Industry context for benchmarking
            
        Returns:
            Comprehensive scoring result with breakdowns
        """
        
        # Generate consistency hash for the resume
        consistency_hash = self._generate_consistency_hash(resume_data, job_requirements)
        
        # Check if we've scored this exact resume before
        if consistency_hash in self.consistency_cache:
            cached_result = self.consistency_cache[consistency_hash]
            cached_result.consistency_hash = consistency_hash
            return cached_result
        
        # Calculate individual category scores
        category_scores = {
            "skills_match": self._score_skills_match(resume_data, job_requirements),
            "experience_relevance": self._score_experience_relevance(resume_data, job_requirements),
            "education_alignment": self._score_education_alignment(resume_data, job_requirements),
            "format_structure": self._score_format_structure(resume_data),
            "keyword_optimization": self._score_keyword_optimization(resume_data, job_requirements)
        }
        
        # Calculate weighted overall score
        overall_score = (
            category_scores["skills_match"] * self.weights.skills_match +
            category_scores["experience_relevance"] * self.weights.experience_relevance +
            category_scores["education_alignment"] * self.weights.education_alignment +
            category_scores["format_structure"] * self.weights.format_structure +
            category_scores["keyword_optimization"] * self.weights.keyword_optimization
        )
        
        # Generate detailed breakdown
        detailed_breakdown = self._generate_detailed_breakdown(
            resume_data, category_scores, job_requirements
        )
        
        # Calculate confidence interval
        confidence_interval = self._calculate_confidence_interval(category_scores)
        
        # Benchmark comparison
        benchmark_comparison = self._compare_with_benchmarks(overall_score, industry)
        
        # Generate recommendations
        recommendations = self._generate_scoring_recommendations(category_scores, detailed_breakdown)
        
        # Create result object
        result = ScoreResult(
            overall_score=round(overall_score, 2),
            category_scores={k: round(v, 2) for k, v in category_scores.items()},
            detailed_breakdown=detailed_breakdown,
            confidence_interval=(round(confidence_interval[0], 2), round(confidence_interval[1], 2)),
            consistency_hash=consistency_hash,
            benchmark_comparison=benchmark_comparison,
            recommendations=recommendations
        )
        
        # Cache the result for consistency
        self.consistency_cache[consistency_hash] = result
        
        # Log scoring
        self._log_scoring(resume_data, result, job_requirements, industry)
        
        return result
    
    def _score_skills_match(self, resume_data: Dict[str, Any], 
                           job_requirements: Dict[str, Any] = None) -> float:
        """Score skills match (30% weight)"""
        
        skills = resume_data.get("skills", {})
        all_resume_skills = []
        
        # Combine all skill categories
        for skill_category in skills.values():
            if isinstance(skill_category, list):
                all_resume_skills.extend([skill.lower() for skill in skill_category])
        
        if not all_resume_skills:
            return 0.0
        
        # If job requirements provided, calculate match
        if job_requirements and job_requirements.get("required_skills"):
            required_skills = [skill.lower() for skill in job_requirements["required_skills"]]
            matched_skills = len(set(all_resume_skills) & set(required_skills))
            total_required = len(required_skills)
            
            if total_required > 0:
                match_percentage = (matched_skills / total_required) * 100
                return min(match_percentage, 100.0)
        
        # Default scoring based on skill quantity and quality
        skill_count = len(all_resume_skills)
        
        # Score based on skill diversity and count
        if skill_count >= 15:
            return 95.0
        elif skill_count >= 10:
            return 85.0
        elif skill_count >= 7:
            return 75.0
        elif skill_count >= 5:
            return 65.0
        elif skill_count >= 3:
            return 50.0
        else:
            return 30.0
    
    def _score_experience_relevance(self, resume_data: Dict[str, Any], 
                                  job_requirements: Dict[str, Any] = None) -> float:
        """Score experience relevance (25% weight)"""
        
        experience = resume_data.get("experience", [])
        
        if not experience:
            return 0.0
        
        total_score = 0.0
        weights_sum = 0.0
        
        for exp in experience:
            exp_score = 0.0
            weight = 1.0
            
            # Score based on duration
            duration = self._calculate_duration(exp.get("start_date"), exp.get("end_date"))
            if duration >= 3:
                exp_score += 30  # Long-term experience bonus
            elif duration >= 1:
                exp_score += 20
            else:
                exp_score += 10
            
            # Score based on responsibilities
            responsibilities = exp.get("responsibilities", [])
            if len(responsibilities) >= 5:
                exp_score += 25
            elif len(responsibilities) >= 3:
                exp_score += 20
            else:
                exp_score += 10
            
            # Score based on achievements
            achievements = exp.get("achievements", [])
            if achievements:
                exp_score += 25
                # Bonus for quantified achievements
                quantified = sum(1 for ach in achievements if any(char.isdigit() for char in ach))
                if quantified > 0:
                    exp_score += 15
            
            # Score based on title seniority
            title = exp.get("title", "").lower()
            if any(word in title for word in ["senior", "lead", "manager", "director", "vp"]):
                exp_score += 20
                weight = 1.5  # Higher weight for senior roles
            elif any(word in title for word in ["junior", "intern", "assistant"]):
                weight = 0.8
            
            # Job relevance if requirements provided
            if job_requirements and job_requirements.get("preferred_experience"):
                pref_exp = [exp.lower() for exp in job_requirements["preferred_experience"]]
                exp_text = f"{exp.get('title', '')} {' '.join(responsibilities)}".lower()
                
                relevance_matches = sum(1 for pref in pref_exp if pref in exp_text)
                if relevance_matches > 0:
                    exp_score += relevance_matches * 10
            
            total_score += exp_score * weight
            weights_sum += weight
        
        if weights_sum > 0:
            average_score = total_score / weights_sum
            return min(average_score, 100.0)
        
        return 0.0
    
    def _score_education_alignment(self, resume_data: Dict[str, Any], 
                                 job_requirements: Dict[str, Any] = None) -> float:
        """Score education alignment (15% weight)"""
        
        education = resume_data.get("education", [])
        
        if not education:
            return 40.0  # Some base score for work experience
        
        highest_score = 0.0
        
        for edu in education:
            edu_score = 0.0
            degree = edu.get("degree", "").lower()
            
            # Score based on degree level
            if "phd" in degree or "doctorate" in degree:
                edu_score += 100
            elif "master" in degree or "mba" in degree:
                edu_score += 85
            elif "bachelor" in degree:
                edu_score += 75
            elif "associate" in degree:
                edu_score += 60
            elif any(cert in degree for cert in ["certificate", "diploma"]):
                edu_score += 50
            else:
                edu_score += 40
            
            # Institution quality bonus (simplified)
            institution = edu.get("institution", "").lower()
            if any(word in institution for word in ["university", "college", "institute"]):
                edu_score += 10
            
            # GPA bonus
            gpa = edu.get("gpa")
            if gpa:
                try:
                    gpa_float = float(gpa)
                    if gpa_float >= 3.7:
                        edu_score += 15
                    elif gpa_float >= 3.3:
                        edu_score += 10
                    elif gpa_float >= 3.0:
                        edu_score += 5
                except ValueError:
                    pass
            
            # Field relevance if job requirements provided
            if job_requirements and job_requirements.get("preferred_education"):
                pref_fields = [field.lower() for field in job_requirements["preferred_education"]]
                if any(field in degree for field in pref_fields):
                    edu_score += 20
            
            highest_score = max(highest_score, edu_score)
        
        return min(highest_score, 100.0)
    
    def _score_format_structure(self, resume_data: Dict[str, Any]) -> float:
        """Score format and structure (15% weight)"""
        
        score = 0.0
        
        # Check presence of key sections
        required_sections = ["personal_info", "experience", "education", "skills"]
        present_sections = sum(1 for section in required_sections 
                             if resume_data.get(section) and resume_data[section])
        
        score += (present_sections / len(required_sections)) * 40
        
        # Personal info completeness
        personal_info = resume_data.get("personal_info", {})
        required_personal = ["name", "email", "phone"]
        present_personal = sum(1 for field in required_personal 
                             if personal_info.get(field) and 
                             personal_info[field] != "Not specified")
        
        score += (present_personal / len(required_personal)) * 20
        
        # Content organization
        experience = resume_data.get("experience", [])
        if experience:
            # Check if experiences have required fields
            complete_experiences = 0
            for exp in experience:
                required_exp_fields = ["title", "company", "start_date"]
                if all(exp.get(field) for field in required_exp_fields):
                    complete_experiences += 1
            
            if len(experience) > 0:
                score += (complete_experiences / len(experience)) * 20
        
        # Skills organization
        skills = resume_data.get("skills", {})
        if skills:
            skill_categories = len([cat for cat in skills.values() if cat])
            if skill_categories >= 3:
                score += 20
            elif skill_categories >= 2:
                score += 15
            elif skill_categories >= 1:
                score += 10
        
        return min(score, 100.0)
    
    def _score_keyword_optimization(self, resume_data: Dict[str, Any], 
                                  job_requirements: Dict[str, Any] = None) -> float:
        """Score keyword optimization (15% weight)"""
        
        # Extract all text content from resume
        all_text = self._extract_all_text(resume_data).lower()
        
        if not all_text:
            return 0.0
        
        # Industry-specific keywords (simplified)
        industry_keywords = {
            "technology": ["python", "java", "javascript", "react", "sql", "api", "database", 
                          "software", "development", "programming", "framework", "cloud"],
            "healthcare": ["patient", "clinical", "medical", "healthcare", "treatment", 
                          "diagnosis", "care", "hospital", "nursing"],
            "finance": ["financial", "accounting", "budget", "analysis", "reporting", 
                       "compliance", "risk", "investment", "banking"],
            "marketing": ["marketing", "campaign", "brand", "advertising", "social media", 
                         "analytics", "content", "strategy", "digital"],
            "general": ["management", "leadership", "communication", "project", "team", 
                       "problem solving", "analysis", "strategy", "development"]
        }
        
        # Use job requirements keywords if available
        target_keywords = []
        if job_requirements:
            if job_requirements.get("keywords"):
                target_keywords = [kw.lower() for kw in job_requirements["keywords"]]
            if job_requirements.get("required_skills"):
                target_keywords.extend([skill.lower() for skill in job_requirements["required_skills"]])
        
        # Fallback to general keywords
        if not target_keywords:
            target_keywords = industry_keywords["general"]
        
        # Count keyword matches
        matched_keywords = 0
        for keyword in target_keywords:
            if keyword in all_text:
                matched_keywords += 1
        
        if len(target_keywords) > 0:
            match_percentage = (matched_keywords / len(target_keywords)) * 100
            return min(match_percentage, 100.0)
        
        return 50.0  # Default score if no keywords to match
    
    def _calculate_duration(self, start_date: str, end_date: str) -> float:
        """Calculate duration in years from date strings"""
        
        if not start_date:
            return 0.0
        
        try:
            # Simple duration calculation (assuming MM/YYYY format)
            if end_date and end_date.lower() != "present":
                start_parts = start_date.split("/")
                end_parts = end_date.split("/")
                
                if len(start_parts) >= 2 and len(end_parts) >= 2:
                    start_year = int(start_parts[-1])
                    start_month = int(start_parts[0])
                    end_year = int(end_parts[-1])
                    end_month = int(end_parts[0])
                    
                    duration = end_year - start_year + (end_month - start_month) / 12
                    return max(duration, 0.0)
            else:
                # Calculate from start to present
                start_parts = start_date.split("/")
                if len(start_parts) >= 2:
                    start_year = int(start_parts[-1])
                    current_year = datetime.now().year
                    duration = current_year - start_year
                    return max(duration, 0.0)
        
        except (ValueError, IndexError):
            pass
        
        return 0.0
    
    def _extract_all_text(self, resume_data: Dict[str, Any]) -> str:
        """Extract all text content from resume data"""
        
        text_parts = []
        
        # Extract from all sections
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
    
    def _generate_consistency_hash(self, resume_data: Dict[str, Any], 
                                  job_requirements: Dict[str, Any] = None) -> str:
        """Generate a hash for consistency checking"""
        
        # Create a normalized string representation
        resume_str = json.dumps(resume_data, sort_keys=True)
        job_str = json.dumps(job_requirements or {}, sort_keys=True)
        
        combined_str = f"{resume_str}|{job_str}|{self.weights.__dict__}"
        
        return hashlib.md5(combined_str.encode()).hexdigest()
    
    def _generate_detailed_breakdown(self, resume_data: Dict[str, Any], 
                                   category_scores: Dict[str, float],
                                   job_requirements: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate detailed scoring breakdown"""
        
        breakdown = {
            "scoring_timestamp": datetime.now().isoformat(),
            "weights_used": {
                "skills_match": self.weights.skills_match,
                "experience_relevance": self.weights.experience_relevance,
                "education_alignment": self.weights.education_alignment,
                "format_structure": self.weights.format_structure,
                "keyword_optimization": self.weights.keyword_optimization
            },
            "category_analysis": {},
            "strengths": [],
            "weaknesses": [],
            "missing_elements": []
        }
        
        # Analyze each category
        for category, score in category_scores.items():
            analysis = {"score": score, "level": "", "details": []}
            
            if score >= 90:
                analysis["level"] = "Excellent"
                breakdown["strengths"].append(f"{category.replace('_', ' ').title()}: {score:.1f}")
            elif score >= 75:
                analysis["level"] = "Good"
            elif score >= 60:
                analysis["level"] = "Fair"
                breakdown["weaknesses"].append(f"{category.replace('_', ' ').title()}: {score:.1f}")
            else:
                analysis["level"] = "Needs Improvement"
                breakdown["weaknesses"].append(f"{category.replace('_', ' ').title()}: {score:.1f}")
            
            breakdown["category_analysis"][category] = analysis
        
        # Identify missing elements
        if not resume_data.get("personal_info", {}).get("linkedin"):
            breakdown["missing_elements"].append("LinkedIn profile URL")
        
        if not resume_data.get("skills", {}).get("certifications"):
            breakdown["missing_elements"].append("Professional certifications")
        
        experience = resume_data.get("experience", [])
        if experience:
            quantified_achievements = 0
            for exp in experience:
                achievements = exp.get("achievements", [])
                quantified_achievements += sum(1 for ach in achievements 
                                             if any(char.isdigit() for char in ach))
            
            if quantified_achievements == 0:
                breakdown["missing_elements"].append("Quantified achievements with numbers/percentages")
        
        return breakdown
    
    def _calculate_confidence_interval(self, category_scores: Dict[str, float]) -> Tuple[float, float]:
        """Calculate confidence interval for the overall score"""
        
        scores = list(category_scores.values())
        
        if len(scores) == 0:
            return (0.0, 0.0)
        
        # Calculate weighted average
        weighted_scores = [
            scores[0] * self.weights.skills_match,
            scores[1] * self.weights.experience_relevance,
            scores[2] * self.weights.education_alignment,
            scores[3] * self.weights.format_structure,
            scores[4] * self.weights.keyword_optimization
        ]
        
        overall = sum(weighted_scores)
        
        # Simple confidence interval calculation
        std_dev = np.std(scores)
        margin_error = 1.96 * (std_dev / np.sqrt(len(scores)))  # 95% confidence
        
        lower_bound = max(0, overall - margin_error)
        upper_bound = min(100, overall + margin_error)
        
        return (lower_bound, upper_bound)
    
    def _compare_with_benchmarks(self, score: float, industry: str) -> Dict[str, Any]:
        """Compare score with industry benchmarks"""
        
        benchmark = self.industry_benchmarks.get(industry, self.industry_benchmarks["general"])
        
        comparison = {
            "industry": industry,
            "score": score,
            "industry_average": benchmark["average_score"],
            "top_percentile_threshold": benchmark["top_percentile"],
            "performance_level": "",
            "percentile_estimate": 0
        }
        
        if score >= benchmark["top_percentile"]:
            comparison["performance_level"] = "Top 10%"
            comparison["percentile_estimate"] = 95
        elif score >= benchmark["average_score"] + 10:
            comparison["performance_level"] = "Above Average"
            comparison["percentile_estimate"] = 75
        elif score >= benchmark["average_score"]:
            comparison["performance_level"] = "Average"
            comparison["percentile_estimate"] = 50
        elif score >= benchmark["average_score"] - 10:
            comparison["performance_level"] = "Below Average"
            comparison["percentile_estimate"] = 25
        else:
            comparison["performance_level"] = "Needs Significant Improvement"
            comparison["percentile_estimate"] = 10
        
        return comparison
    
    def _generate_scoring_recommendations(self, category_scores: Dict[str, float], 
                                        detailed_breakdown: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on scores"""
        
        recommendations = []
        
        # Skills-based recommendations
        if category_scores["skills_match"] < 70:
            recommendations.append("Add more relevant technical skills matching job requirements")
        
        # Experience-based recommendations
        if category_scores["experience_relevance"] < 70:
            recommendations.append("Include more quantified achievements in work experience")
            recommendations.append("Add action verbs and specific accomplishments")
        
        # Education recommendations
        if category_scores["education_alignment"] < 60:
            recommendations.append("Consider adding relevant certifications or training")
        
        # Format recommendations
        if category_scores["format_structure"] < 70:
            recommendations.append("Improve resume formatting and organization")
            recommendations.append("Ensure all sections are complete and well-structured")
        
        # Keyword recommendations
        if category_scores["keyword_optimization"] < 70:
            recommendations.append("Include more industry-relevant keywords")
            recommendations.append("Optimize for ATS keyword scanning")
        
        # General recommendations based on overall performance
        overall_avg = sum(category_scores.values()) / len(category_scores)
        if overall_avg < 60:
            recommendations.append("Consider professional resume review and rewriting")
        
        return recommendations
    
    def _log_scoring(self, resume_data: Dict[str, Any], result: ScoreResult, 
                    job_requirements: Dict[str, Any], industry: str):
        """Log scoring for tracking and analysis"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "resume_hash": result.consistency_hash,
            "overall_score": result.overall_score,
            "category_scores": result.category_scores,
            "industry": industry,
            "had_job_requirements": job_requirements is not None,
            "confidence_interval": result.confidence_interval
        }
        
        self.scoring_history.append(log_entry)
    
    def get_scoring_statistics(self) -> Dict[str, Any]:
        """Get scoring statistics for monitoring"""
        
        if not self.scoring_history:
            return {"message": "No scoring history available"}
        
        scores = [entry["overall_score"] for entry in self.scoring_history]
        
        stats = {
            "total_scored": len(self.scoring_history),
            "average_score": np.mean(scores),
            "score_distribution": {
                "excellent_90_plus": len([s for s in scores if s >= 90]),
                "good_75_89": len([s for s in scores if 75 <= s < 90]),
                "fair_60_74": len([s for s in scores if 60 <= s < 75]),
                "needs_improvement_below_60": len([s for s in scores if s < 60])
            },
            "consistency_rate": len(self.consistency_cache) / len(self.scoring_history) * 100,
            "recent_average": np.mean(scores[-10:]) if len(scores) >= 10 else np.mean(scores)
        }
        
        return stats


# Example usage and testing
def test_ats_scorer():
    """Test function for the ATS Scoring Agent"""
    
    config_list = [
        {
            "model": "gpt-4", 
            "api_key": "your-api-key-here",
            "base_url": "https://api.openai.com/v1",
        }
    ]
    
    # Sample resume data
    sample_resume = {
        "personal_info": {
            "name": "John Doe",
            "email": "john.doe@email.com",
            "phone": "(555) 123-4567",
            "location": "New York, NY",
            "linkedin": "linkedin.com/in/johndoe"
        },
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "start_date": "01/2020",
                "end_date": "Present",
                "responsibilities": [
                    "Developed web applications using React and Node.js",
                    "Led team of 3 developers",
                    "Implemented CI/CD pipelines"
                ],
                "achievements": [
                    "Improved application performance by 40%",
                    "Reduced deployment time by 60%"
                ]
            }
        ],
        "education": [
            {
                "degree": "Bachelor of Science in Computer Science",
                "institution": "Tech University",
                "graduation_date": "05/2018",
                "gpa": "3.8"
            }
        ],
        "skills": {
            "technical_skills": ["Python", "JavaScript", "React", "Node.js", "SQL"],
            "tools_technologies": ["Git", "Docker", "AWS", "Jenkins"]
        }
    }
    
    # Sample job requirements
    job_requirements = {
        "required_skills": ["Python", "JavaScript", "React", "SQL"],
        "preferred_experience": ["web development", "team leadership"],
        "keywords": ["software engineer", "full stack", "agile"]
    }
    
    # Initialize scorer
    scorer = ATSScoringAgent(config_list)
    
    # Score the resume
    result = scorer.score_resume(sample_resume, job_requirements, "technology")
    
    print("ATS Scoring Results:")
    print(f"Overall Score: {result.overall_score}")
    print(f"Category Scores: {result.category_scores}")
    print(f"Confidence Interval: {result.confidence_interval}")
    print(f"Benchmark Comparison: {result.benchmark_comparison}")
    print(f"Recommendations: {result.recommendations}")
    
    # Test consistency
    result2 = scorer.score_resume(sample_resume, job_requirements, "technology")
    print(f"\nConsistency Test: {result.overall_score == result2.overall_score}")


if __name__ == "__main__":
    test_ats_scorer()
