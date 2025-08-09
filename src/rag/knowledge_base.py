"""
RAG Knowledge Base System for ATS
Retrieval-Augmented Generation for industry requirements, best practices, and historical patterns
"""

import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import sqlite3
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
from collections import defaultdict
import re


@dataclass
class KnowledgeEntry:
    """Knowledge base entry structure"""
    id: str
    category: str
    title: str
    content: str
    tags: List[str]
    embedding: Optional[List[float]]
    source: str
    created_at: datetime
    metadata: Dict[str, Any]


@dataclass
class SkillTaxonomy:
    """Skill taxonomy entry"""
    skill_name: str
    category: str
    subcategory: str
    aliases: List[str]
    related_skills: List[str]
    industry_relevance: Dict[str, float]  # industry -> relevance score
    difficulty_level: str  # beginner, intermediate, advanced, expert


class RAGKnowledgeBase:
    """
    RAG Knowledge Base for ATS System
    Manages industry requirements, best practices, and historical patterns
    """
    
    def __init__(self, db_path: str = "rag_knowledge.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.skill_taxonomy = {}
        self.industry_patterns = {}
        self._init_knowledge_base()
        self._load_skill_taxonomy()
        self._load_industry_patterns()
    
    def _init_knowledge_base(self):
        """Initialize knowledge base tables"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Knowledge entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_entries (
                id TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                tags TEXT,
                embedding TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        
        # Skill taxonomy table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skill_taxonomy (
                skill_name TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                subcategory TEXT,
                aliases TEXT,
                related_skills TEXT,
                industry_relevance TEXT,
                difficulty_level TEXT
            )
        """)
        
        # Industry patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS industry_patterns (
                industry TEXT PRIMARY KEY,
                common_skills TEXT NOT NULL,
                trending_skills TEXT,
                skill_weights TEXT,
                experience_patterns TEXT,
                education_requirements TEXT,
                salary_ranges TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Historical scoring patterns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scoring_patterns (
                pattern_id TEXT PRIMARY KEY,
                industry TEXT,
                job_level TEXT,
                score_distributions TEXT,
                common_issues TEXT,
                improvement_patterns TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_entries (category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_skill_category ON skill_taxonomy (category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_industry ON industry_patterns (industry)")
        
        conn.commit()
        conn.close()
        
        self.logger.info("Knowledge base initialized")
    
    def _load_skill_taxonomy(self):
        """Load skill taxonomy into memory"""
        
        # Initialize with common skills taxonomy
        default_skills = self._get_default_skill_taxonomy()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM skill_taxonomy")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Load default taxonomy
            for skill_data in default_skills:
                self.add_skill_to_taxonomy(**skill_data)
        
        # Load into memory
        cursor.execute("SELECT * FROM skill_taxonomy")
        for row in cursor.fetchall():
            skill = SkillTaxonomy(
                skill_name=row[0],
                category=row[1],
                subcategory=row[2] if row[2] else "",
                aliases=json.loads(row[3]) if row[3] else [],
                related_skills=json.loads(row[4]) if row[4] else [],
                industry_relevance=json.loads(row[5]) if row[5] else {},
                difficulty_level=row[6] if row[6] else "intermediate"
            )
            self.skill_taxonomy[skill.skill_name.lower()] = skill
        
        conn.close()
        self.logger.info(f"Loaded {len(self.skill_taxonomy)} skills into taxonomy")
    
    def _load_industry_patterns(self):
        """Load industry patterns into memory"""
        
        # Initialize with default patterns if empty
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM industry_patterns")
        count = cursor.fetchone()[0]
        
        if count == 0:
            default_patterns = self._get_default_industry_patterns()
            for industry, pattern_data in default_patterns.items():
                self.add_industry_pattern(industry, pattern_data)
        
        # Load into memory
        cursor.execute("SELECT * FROM industry_patterns")
        for row in cursor.fetchall():
            industry = row[0]
            self.industry_patterns[industry] = {
                "common_skills": json.loads(row[1]),
                "trending_skills": json.loads(row[2]) if row[2] else [],
                "skill_weights": json.loads(row[3]) if row[3] else {},
                "experience_patterns": json.loads(row[4]) if row[4] else {},
                "education_requirements": json.loads(row[5]) if row[5] else {},
                "salary_ranges": json.loads(row[6]) if row[6] else {}
            }
        
        conn.close()
        self.logger.info(f"Loaded {len(self.industry_patterns)} industry patterns")
    
    def add_knowledge_entry(self, category: str, title: str, content: str,
                          tags: List[str] = None, source: str = "manual",
                          metadata: Dict[str, Any] = None) -> str:
        """Add new knowledge entry"""
        
        entry_id = self._generate_id(f"{category}_{title}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO knowledge_entries 
            (id, category, title, content, tags, source, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            entry_id, category, title, content,
            json.dumps(tags) if tags else None,
            source,
            json.dumps(metadata) if metadata else None
        ))
        conn.commit()
        conn.close()
        
        self.logger.info(f"Added knowledge entry: {entry_id}")
        return entry_id
    
    def search_knowledge(self, query: str, category: str = None,
                        limit: int = 10) -> List[KnowledgeEntry]:
        """Search knowledge base entries"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Simple text search (in production, use vector similarity)
        base_query = """
            SELECT * FROM knowledge_entries 
            WHERE (title LIKE ? OR content LIKE ? OR tags LIKE ?)
        """
        params = [f"%{query}%", f"%{query}%", f"%{query}%"]
        
        if category:
            base_query += " AND category = ?"
            params.append(category)
        
        base_query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(base_query, params)
        
        entries = []
        for row in cursor.fetchall():
            entry = KnowledgeEntry(
                id=row[0],
                category=row[1],
                title=row[2],
                content=row[3],
                tags=json.loads(row[4]) if row[4] else [],
                embedding=json.loads(row[5]) if row[5] else None,
                source=row[6],
                created_at=datetime.fromisoformat(row[7]),
                metadata=json.loads(row[8]) if row[8] else {}
            )
            entries.append(entry)
        
        conn.close()
        return entries
    
    def add_skill_to_taxonomy(self, skill_name: str, category: str,
                            subcategory: str = "", aliases: List[str] = None,
                            related_skills: List[str] = None,
                            industry_relevance: Dict[str, float] = None,
                            difficulty_level: str = "intermediate"):
        """Add skill to taxonomy"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO skill_taxonomy 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            skill_name.lower(),
            category,
            subcategory,
            json.dumps(aliases) if aliases else None,
            json.dumps(related_skills) if related_skills else None,
            json.dumps(industry_relevance) if industry_relevance else None,
            difficulty_level
        ))
        conn.commit()
        conn.close()
        
        # Update in-memory taxonomy
        skill = SkillTaxonomy(
            skill_name=skill_name,
            category=category,
            subcategory=subcategory,
            aliases=aliases or [],
            related_skills=related_skills or [],
            industry_relevance=industry_relevance or {},
            difficulty_level=difficulty_level
        )
        self.skill_taxonomy[skill_name.lower()] = skill
    
    def get_skill_info(self, skill_name: str) -> Optional[SkillTaxonomy]:
        """Get skill information from taxonomy"""
        return self.skill_taxonomy.get(skill_name.lower())
    
    def find_skill_matches(self, skills: List[str]) -> Dict[str, SkillTaxonomy]:
        """Find matching skills in taxonomy with fuzzy matching"""
        
        matches = {}
        
        for skill in skills:
            skill_lower = skill.lower()
            
            # Direct match
            if skill_lower in self.skill_taxonomy:
                matches[skill] = self.skill_taxonomy[skill_lower]
                continue
            
            # Alias match
            for taxonomy_skill, skill_data in self.skill_taxonomy.items():
                if skill_lower in [alias.lower() for alias in skill_data.aliases]:
                    matches[skill] = skill_data
                    break
                
                # Partial match (simple substring)
                if skill_lower in taxonomy_skill or taxonomy_skill in skill_lower:
                    matches[skill] = skill_data
                    break
        
        return matches
    
    def get_related_skills(self, skill_name: str) -> List[str]:
        """Get related skills for a given skill"""
        
        skill_info = self.get_skill_info(skill_name)
        if skill_info:
            return skill_info.related_skills
        return []
    
    def analyze_skill_gaps(self, resume_skills: List[str],
                          job_requirements: List[str]) -> Dict[str, Any]:
        """Analyze skill gaps using taxonomy"""
        
        resume_matches = self.find_skill_matches(resume_skills)
        job_matches = self.find_skill_matches(job_requirements)
        
        # Categorize skills
        resume_categories = defaultdict(list)
        job_categories = defaultdict(list)
        
        for skill, skill_info in resume_matches.items():
            resume_categories[skill_info.category].append(skill)
        
        for skill, skill_info in job_matches.items():
            job_categories[skill_info.category].append(skill)
        
        # Find gaps
        missing_skills = []
        category_gaps = {}
        
        for category, required_skills in job_categories.items():
            available_skills = resume_categories.get(category, [])
            missing_in_category = [skill for skill in required_skills 
                                 if skill not in available_skills]
            
            if missing_in_category:
                category_gaps[category] = missing_in_category
                missing_skills.extend(missing_in_category)
        
        # Suggest related skills
        skill_suggestions = {}
        for missing_skill in missing_skills:
            related = self.get_related_skills(missing_skill)
            available_related = [skill for skill in related if skill in resume_skills]
            if available_related:
                skill_suggestions[missing_skill] = available_related
        
        return {
            "missing_skills": missing_skills,
            "category_gaps": category_gaps,
            "skill_suggestions": skill_suggestions,
            "resume_skill_categories": dict(resume_categories),
            "job_skill_categories": dict(job_categories)
        }
    
    def add_industry_pattern(self, industry: str, pattern_data: Dict[str, Any]):
        """Add industry pattern"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO industry_patterns 
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            industry,
            json.dumps(pattern_data.get("common_skills", [])),
            json.dumps(pattern_data.get("trending_skills", [])),
            json.dumps(pattern_data.get("skill_weights", {})),
            json.dumps(pattern_data.get("experience_patterns", {})),
            json.dumps(pattern_data.get("education_requirements", {})),
            json.dumps(pattern_data.get("salary_ranges", {}))
        ))
        conn.commit()
        conn.close()
        
        self.industry_patterns[industry] = pattern_data
    
    def get_industry_insights(self, industry: str) -> Dict[str, Any]:
        """Get industry-specific insights"""
        
        if industry not in self.industry_patterns:
            return {"message": f"No data available for industry: {industry}"}
        
        return self.industry_patterns[industry]
    
    def get_trending_skills(self, industry: str = None) -> List[str]:
        """Get trending skills for industry or overall"""
        
        if industry and industry in self.industry_patterns:
            return self.industry_patterns[industry].get("trending_skills", [])
        
        # Aggregate trending skills across all industries
        all_trending = []
        for pattern in self.industry_patterns.values():
            all_trending.extend(pattern.get("trending_skills", []))
        
        # Count occurrences and return top trending
        from collections import Counter
        skill_counts = Counter(all_trending)
        return [skill for skill, count in skill_counts.most_common(20)]
    
    def analyze_resume_for_industry(self, resume_data: Dict[str, Any],
                                  target_industry: str) -> Dict[str, Any]:
        """Analyze resume against industry patterns"""
        
        if target_industry not in self.industry_patterns:
            return {"error": f"Industry {target_industry} not found in knowledge base"}
        
        industry_data = self.industry_patterns[target_industry]
        
        # Extract resume skills
        resume_skills = []
        skills_section = resume_data.get("skills", {})
        for skill_category in skills_section.values():
            if isinstance(skill_category, list):
                resume_skills.extend([skill.lower() for skill in skill_category])
        
        # Analyze against industry requirements
        common_skills = [skill.lower() for skill in industry_data.get("common_skills", [])]
        trending_skills = [skill.lower() for skill in industry_data.get("trending_skills", [])]
        
        # Calculate matches
        common_matches = len([skill for skill in resume_skills if skill in common_skills])
        trending_matches = len([skill for skill in resume_skills if skill in trending_skills])
        
        # Industry alignment score
        total_common = len(common_skills)
        total_trending = len(trending_skills)
        
        common_score = (common_matches / total_common * 100) if total_common > 0 else 0
        trending_score = (trending_matches / total_trending * 100) if total_trending > 0 else 0
        
        overall_alignment = (common_score * 0.7 + trending_score * 0.3)
        
        # Missing skills
        missing_common = [skill for skill in common_skills if skill not in resume_skills]
        missing_trending = [skill for skill in trending_skills if skill not in resume_skills]
        
        return {
            "industry_alignment_score": overall_alignment,
            "common_skills_score": common_score,
            "trending_skills_score": trending_score,
            "matched_skills": {
                "common": [skill for skill in resume_skills if skill in common_skills],
                "trending": [skill for skill in resume_skills if skill in trending_skills]
            },
            "missing_skills": {
                "common": missing_common[:10],  # Top 10 missing
                "trending": missing_trending[:5]  # Top 5 trending missing
            },
            "recommendations": self._generate_industry_recommendations(
                missing_common, missing_trending, industry_data
            )
        }
    
    def _generate_industry_recommendations(self, missing_common: List[str],
                                         missing_trending: List[str],
                                         industry_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on industry analysis"""
        
        recommendations = []
        
        if missing_common:
            recommendations.append(
                f"Focus on acquiring these essential skills: {', '.join(missing_common[:5])}"
            )
        
        if missing_trending:
            recommendations.append(
                f"Stay current with trending skills: {', '.join(missing_trending[:3])}"
            )
        
        # Education recommendations
        edu_reqs = industry_data.get("education_requirements", {})
        if edu_reqs:
            recommendations.append(
                f"Consider pursuing relevant certifications or education in: {', '.join(edu_reqs.keys())}"
            )
        
        return recommendations
    
    def get_best_practices(self, category: str) -> List[KnowledgeEntry]:
        """Get best practices for a category"""
        return self.search_knowledge("best practice", category)
    
    def add_scoring_pattern(self, industry: str, job_level: str,
                          score_distributions: Dict[str, Any],
                          common_issues: List[str],
                          improvement_patterns: Dict[str, Any]) -> str:
        """Add scoring pattern for historical analysis"""
        
        pattern_id = self._generate_id(f"{industry}_{job_level}_{datetime.now().isoformat()}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scoring_patterns 
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            pattern_id, industry, job_level,
            json.dumps(score_distributions),
            json.dumps(common_issues),
            json.dumps(improvement_patterns)
        ))
        conn.commit()
        conn.close()
        
        return pattern_id
    
    def get_scoring_benchmarks(self, industry: str = None,
                             job_level: str = None) -> Dict[str, Any]:
        """Get scoring benchmarks and patterns"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM scoring_patterns WHERE 1=1"
        params = []
        
        if industry:
            query += " AND industry = ?"
            params.append(industry)
        
        if job_level:
            query += " AND job_level = ?"
            params.append(job_level)
        
        cursor.execute(query, params)
        patterns = cursor.fetchall()
        conn.close()
        
        if not patterns:
            return {"message": "No scoring patterns found"}
        
        # Aggregate patterns
        all_distributions = []
        all_issues = []
        all_improvements = {}
        
        for pattern in patterns:
            score_dist = json.loads(pattern[3])
            issues = json.loads(pattern[4])
            improvements = json.loads(pattern[5])
            
            all_distributions.append(score_dist)
            all_issues.extend(issues)
            
            for category, improvement_list in improvements.items():
                if category not in all_improvements:
                    all_improvements[category] = []
                all_improvements[category].extend(improvement_list)
        
        # Calculate aggregated benchmarks
        from collections import Counter
        issue_counts = Counter(all_issues)
        
        return {
            "sample_size": len(patterns),
            "common_issues": [issue for issue, count in issue_counts.most_common(10)],
            "improvement_strategies": all_improvements,
            "score_distributions": all_distributions
        }
    
    def _generate_id(self, data: str) -> str:
        """Generate unique ID"""
        import hashlib
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _get_default_skill_taxonomy(self) -> List[Dict[str, Any]]:
        """Get default skill taxonomy"""
        
        return [
            {
                "skill_name": "Python",
                "category": "Programming Languages",
                "subcategory": "Backend",
                "aliases": ["python3", "py"],
                "related_skills": ["Django", "Flask", "FastAPI", "NumPy", "Pandas"],
                "industry_relevance": {"technology": 0.9, "finance": 0.8, "healthcare": 0.7},
                "difficulty_level": "intermediate"
            },
            {
                "skill_name": "JavaScript",
                "category": "Programming Languages",
                "subcategory": "Frontend",
                "aliases": ["js", "javascript", "es6"],
                "related_skills": ["React", "Node.js", "TypeScript", "Vue.js"],
                "industry_relevance": {"technology": 0.95, "media": 0.8, "retail": 0.7},
                "difficulty_level": "intermediate"
            },
            {
                "skill_name": "React",
                "category": "Web Frameworks",
                "subcategory": "Frontend",
                "aliases": ["reactjs", "react.js"],
                "related_skills": ["JavaScript", "Redux", "Next.js", "TypeScript"],
                "industry_relevance": {"technology": 0.9, "startup": 0.9},
                "difficulty_level": "intermediate"
            },
            {
                "skill_name": "Machine Learning",
                "category": "Data Science",
                "subcategory": "AI/ML",
                "aliases": ["ml", "artificial intelligence", "ai"],
                "related_skills": ["Python", "TensorFlow", "PyTorch", "Scikit-learn"],
                "industry_relevance": {"technology": 0.9, "finance": 0.8, "healthcare": 0.9},
                "difficulty_level": "advanced"
            },
            {
                "skill_name": "SQL",
                "category": "Databases",
                "subcategory": "Query Languages",
                "aliases": ["mysql", "postgresql", "sqlite"],
                "related_skills": ["Python", "Data Analysis", "Database Design"],
                "industry_relevance": {"technology": 0.85, "finance": 0.9, "healthcare": 0.8},
                "difficulty_level": "beginner"
            }
        ]
    
    def _get_default_industry_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Get default industry patterns"""
        
        return {
            "technology": {
                "common_skills": [
                    "Python", "JavaScript", "SQL", "Git", "Linux",
                    "AWS", "Docker", "React", "Node.js", "API Development"
                ],
                "trending_skills": [
                    "Kubernetes", "GraphQL", "TypeScript", "Rust", "Go",
                    "Machine Learning", "DevOps", "Microservices"
                ],
                "skill_weights": {
                    "Programming Languages": 0.3,
                    "Web Frameworks": 0.25,
                    "Cloud Platforms": 0.2,
                    "Databases": 0.15,
                    "Tools": 0.1
                },
                "experience_patterns": {
                    "junior": "0-2 years",
                    "mid": "3-5 years",
                    "senior": "6+ years"
                },
                "education_requirements": {
                    "Computer Science": 0.4,
                    "Engineering": 0.3,
                    "Mathematics": 0.15,
                    "Self-taught": 0.15
                }
            },
            "finance": {
                "common_skills": [
                    "Python", "R", "SQL", "Excel", "Financial Modeling",
                    "Risk Management", "Bloomberg Terminal", "VBA"
                ],
                "trending_skills": [
                    "Machine Learning", "Blockchain", "Cryptocurrency",
                    "RegTech", "Algorithmic Trading"
                ],
                "skill_weights": {
                    "Programming": 0.25,
                    "Financial Knowledge": 0.35,
                    "Analytics": 0.25,
                    "Risk Management": 0.15
                }
            },
            "healthcare": {
                "common_skills": [
                    "Python", "R", "SQL", "Healthcare Analytics",
                    "HIPAA Compliance", "Electronic Health Records"
                ],
                "trending_skills": [
                    "AI in Healthcare", "Telemedicine", "Genomics",
                    "Digital Health", "Medical Imaging"
                ],
                "skill_weights": {
                    "Healthcare Knowledge": 0.4,
                    "Technology Skills": 0.3,
                    "Analytics": 0.2,
                    "Compliance": 0.1
                }
            }
        }


# Example usage and testing
def test_rag_knowledge_base():
    """Test RAG knowledge base functionality"""
    
    # Initialize knowledge base
    rag_kb = RAGKnowledgeBase("test_rag.db")
    
    # Add knowledge entry
    entry_id = rag_kb.add_knowledge_entry(
        category="resume_writing",
        title="Best Practices for Technical Resumes",
        content="Use action verbs, quantify achievements, include relevant keywords...",
        tags=["resume", "technical", "best_practices"],
        source="expert_knowledge"
    )
    print(f"Added knowledge entry: {entry_id}")
    
    # Search knowledge
    results = rag_kb.search_knowledge("resume best practices")
    print(f"Found {len(results)} knowledge entries")
    
    # Test skill taxonomy
    python_info = rag_kb.get_skill_info("python")
    print(f"Python skill info: {python_info}")
    
    # Test skill gap analysis
    resume_skills = ["python", "javascript", "html", "css"]
    job_skills = ["python", "react", "node.js", "aws", "docker"]
    
    gap_analysis = rag_kb.analyze_skill_gaps(resume_skills, job_skills)
    print(f"Skill gap analysis: {gap_analysis}")
    
    # Test industry analysis
    sample_resume = {
        "skills": {
            "technical": ["Python", "JavaScript", "SQL"],
            "frameworks": ["React", "Django"]
        }
    }
    
    industry_analysis = rag_kb.analyze_resume_for_industry(sample_resume, "technology")
    print(f"Industry analysis: {industry_analysis}")
    
    # Clean up test database
    import os
    if os.path.exists("test_rag.db"):
        os.remove("test_rag.db")
        print("Test database cleaned up")


if __name__ == "__main__":
    test_rag_knowledge_base()
