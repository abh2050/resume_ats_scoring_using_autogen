"""
Database Operations Module for ATS System
Handles resume data storage, job templates, scoring history, and user sessions
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
from contextlib import contextmanager


@dataclass
class ResumeRecord:
    """Resume record data structure"""
    id: str
    filename: str
    file_hash: str
    processed_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    user_session: str = None


@dataclass
class ScoringRecord:
    """Scoring record data structure"""
    id: str
    resume_id: str
    job_id: str
    overall_score: float
    category_scores: Dict[str, float]
    scoring_metadata: Dict[str, Any]
    created_at: datetime
    user_session: str = None


@dataclass
class JobTemplate:
    """Job template data structure"""
    id: str
    title: str
    company: str
    description: str
    requirements: Dict[str, Any]
    created_at: datetime
    is_template: bool = True


@dataclass
class UserSession:
    """User session data structure"""
    session_id: str
    created_at: datetime
    last_activity: datetime
    session_data: Dict[str, Any]


class DatabaseManager:
    """
    Database manager for ATS system
    Handles SQLite operations for resume storage, scoring, and session management
    """
    
    def __init__(self, db_path: str = "ats_system.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create resumes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resumes (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    file_hash TEXT UNIQUE NOT NULL,
                    processed_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_session TEXT
                )
            """)
            
            # Create scoring_history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scoring_history (
                    id TEXT PRIMARY KEY,
                    resume_id TEXT NOT NULL,
                    job_id TEXT,
                    overall_score REAL NOT NULL,
                    category_scores TEXT NOT NULL,
                    scoring_metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_session TEXT,
                    FOREIGN KEY (resume_id) REFERENCES resumes (id)
                )
            """)
            
            # Create job_templates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS job_templates (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    company TEXT,
                    description TEXT NOT NULL,
                    requirements TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_template BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Create user_sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    session_id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    session_data TEXT
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_resume_hash ON resumes (file_hash)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scoring_resume ON scoring_history (resume_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_activity ON user_sessions (last_activity)")
            
            conn.commit()
            self.logger.info("Database initialized successfully")
    
    @contextmanager
    def get_connection(self):
        """Get database connection with context management"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def _generate_id(self, data: str) -> str:
        """Generate unique ID from data"""
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _calculate_file_hash(self, content: bytes) -> str:
        """Calculate file hash for duplicate detection"""
        return hashlib.md5(content).hexdigest()
    
    # Resume Operations
    def store_resume(self, filename: str, file_content: bytes,
                    processed_data: Dict[str, Any], user_session: str = None) -> str:
        """
        Store resume data in database
        
        Args:
            filename: Original filename
            file_content: Raw file content for hash calculation
            processed_data: Processed resume data
            user_session: User session ID
            
        Returns:
            Resume ID
        """
        
        file_hash = self._calculate_file_hash(file_content)
        
        # Check for existing resume
        existing_id = self.get_resume_by_hash(file_hash)
        if existing_id:
            self.logger.info(f"Resume already exists with ID: {existing_id}")
            return existing_id
        
        resume_id = self._generate_id(f"{filename}_{file_hash}_{datetime.now().isoformat()}")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO resumes (id, filename, file_hash, processed_data, user_session)
                VALUES (?, ?, ?, ?, ?)
            """, (resume_id, filename, file_hash, json.dumps(processed_data), user_session))
            conn.commit()
        
        self.logger.info(f"Resume stored with ID: {resume_id}")
        return resume_id
    
    def get_resume(self, resume_id: str) -> Optional[ResumeRecord]:
        """Get resume by ID"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,))
            row = cursor.fetchone()
            
            if row:
                return ResumeRecord(
                    id=row['id'],
                    filename=row['filename'],
                    file_hash=row['file_hash'],
                    processed_data=json.loads(row['processed_data']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    user_session=row['user_session']
                )
        
        return None
    
    def get_resume_by_hash(self, file_hash: str) -> Optional[str]:
        """Get resume ID by file hash"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM resumes WHERE file_hash = ?", (file_hash,))
            row = cursor.fetchone()
            
            return row['id'] if row else None
    
    def get_user_resumes(self, user_session: str) -> List[ResumeRecord]:
        """Get all resumes for a user session"""
        
        resumes = []
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM resumes WHERE user_session = ? ORDER BY created_at DESC",
                (user_session,)
            )
            
            for row in cursor.fetchall():
                resumes.append(ResumeRecord(
                    id=row['id'],
                    filename=row['filename'],
                    file_hash=row['file_hash'],
                    processed_data=json.loads(row['processed_data']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    user_session=row['user_session']
                ))
        
        return resumes
    
    def update_resume(self, resume_id: str, processed_data: Dict[str, Any]) -> bool:
        """Update resume processed data"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE resumes 
                SET processed_data = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (json.dumps(processed_data), resume_id))
            
            success = cursor.rowcount > 0
            conn.commit()
        
        if success:
            self.logger.info(f"Resume {resume_id} updated successfully")
        
        return success
    
    def delete_resume(self, resume_id: str) -> bool:
        """Delete resume and associated scoring records"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Delete associated scoring records first
            cursor.execute("DELETE FROM scoring_history WHERE resume_id = ?", (resume_id,))
            
            # Delete resume
            cursor.execute("DELETE FROM resumes WHERE id = ?", (resume_id,))
            
            success = cursor.rowcount > 0
            conn.commit()
        
        if success:
            self.logger.info(f"Resume {resume_id} deleted successfully")
        
        return success
    
    # Scoring Operations
    def store_scoring_result(self, resume_id: str, overall_score: float,
                           category_scores: Dict[str, float],
                           scoring_metadata: Dict[str, Any] = None,
                           job_id: str = None, user_session: str = None) -> str:
        """Store scoring result"""
        
        scoring_id = self._generate_id(f"{resume_id}_{overall_score}_{datetime.now().isoformat()}")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO scoring_history 
                (id, resume_id, job_id, overall_score, category_scores, scoring_metadata, user_session)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                scoring_id, resume_id, job_id, overall_score,
                json.dumps(category_scores),
                json.dumps(scoring_metadata) if scoring_metadata else None,
                user_session
            ))
            conn.commit()
        
        self.logger.info(f"Scoring result stored with ID: {scoring_id}")
        return scoring_id
    
    def get_scoring_history(self, resume_id: str) -> List[ScoringRecord]:
        """Get scoring history for a resume"""
        
        scores = []
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM scoring_history 
                WHERE resume_id = ? 
                ORDER BY created_at DESC
            """, (resume_id,))
            
            for row in cursor.fetchall():
                scores.append(ScoringRecord(
                    id=row['id'],
                    resume_id=row['resume_id'],
                    job_id=row['job_id'],
                    overall_score=row['overall_score'],
                    category_scores=json.loads(row['category_scores']),
                    scoring_metadata=json.loads(row['scoring_metadata']) if row['scoring_metadata'] else {},
                    created_at=datetime.fromisoformat(row['created_at']),
                    user_session=row['user_session']
                ))
        
        return scores
    
    def get_latest_score(self, resume_id: str) -> Optional[ScoringRecord]:
        """Get latest scoring result for a resume"""
        
        history = self.get_scoring_history(resume_id)
        return history[0] if history else None
    
    def get_scoring_statistics(self, user_session: str = None) -> Dict[str, Any]:
        """Get scoring statistics"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            base_query = "SELECT overall_score, category_scores FROM scoring_history"
            params = []
            
            if user_session:
                base_query += " WHERE user_session = ?"
                params.append(user_session)
            
            cursor.execute(base_query, params)
            results = cursor.fetchall()
            
            if not results:
                return {"message": "No scoring data available"}
            
            scores = [row['overall_score'] for row in results]
            
            # Calculate category statistics
            all_category_scores = {}
            for row in results:
                category_scores = json.loads(row['category_scores'])
                for category, score in category_scores.items():
                    if category not in all_category_scores:
                        all_category_scores[category] = []
                    all_category_scores[category].append(score)
            
            category_stats = {}
            for category, scores_list in all_category_scores.items():
                category_stats[category] = {
                    "average": sum(scores_list) / len(scores_list),
                    "min": min(scores_list),
                    "max": max(scores_list),
                    "count": len(scores_list)
                }
            
            stats = {
                "total_scores": len(scores),
                "average_score": sum(scores) / len(scores),
                "min_score": min(scores),
                "max_score": max(scores),
                "category_statistics": category_stats
            }
        
        return stats
    
    # Job Template Operations
    def store_job_template(self, title: str, company: str, description: str,
                          requirements: Dict[str, Any]) -> str:
        """Store job template"""
        
        job_id = self._generate_id(f"{title}_{company}_{datetime.now().isoformat()}")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO job_templates (id, title, company, description, requirements)
                VALUES (?, ?, ?, ?, ?)
            """, (job_id, title, company, description, json.dumps(requirements)))
            conn.commit()
        
        self.logger.info(f"Job template stored with ID: {job_id}")
        return job_id
    
    def get_job_template(self, job_id: str) -> Optional[JobTemplate]:
        """Get job template by ID"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM job_templates WHERE id = ?", (job_id,))
            row = cursor.fetchone()
            
            if row:
                return JobTemplate(
                    id=row['id'],
                    title=row['title'],
                    company=row['company'],
                    description=row['description'],
                    requirements=json.loads(row['requirements']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    is_template=bool(row['is_template'])
                )
        
        return None
    
    def get_job_templates(self, limit: int = 50) -> List[JobTemplate]:
        """Get all job templates"""
        
        templates = []
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM job_templates 
                WHERE is_template = TRUE 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            for row in cursor.fetchall():
                templates.append(JobTemplate(
                    id=row['id'],
                    title=row['title'],
                    company=row['company'],
                    description=row['description'],
                    requirements=json.loads(row['requirements']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    is_template=bool(row['is_template'])
                ))
        
        return templates
    
    def search_job_templates(self, search_term: str) -> List[JobTemplate]:
        """Search job templates by title or company"""
        
        templates = []
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM job_templates 
                WHERE (title LIKE ? OR company LIKE ?) AND is_template = TRUE
                ORDER BY created_at DESC
            """, (f"%{search_term}%", f"%{search_term}%"))
            
            for row in cursor.fetchall():
                templates.append(JobTemplate(
                    id=row['id'],
                    title=row['title'],
                    company=row['company'],
                    description=row['description'],
                    requirements=json.loads(row['requirements']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    is_template=bool(row['is_template'])
                ))
        
        return templates
    
    # Session Management
    def create_session(self, session_data: Dict[str, Any] = None) -> str:
        """Create new user session"""
        
        session_id = self._generate_id(f"session_{datetime.now().isoformat()}")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_sessions (session_id, session_data)
                VALUES (?, ?)
            """, (session_id, json.dumps(session_data) if session_data else "{}"))
            conn.commit()
        
        self.logger.info(f"Session created with ID: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get session by ID"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            
            if row:
                return UserSession(
                    session_id=row['session_id'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    last_activity=datetime.fromisoformat(row['last_activity']),
                    session_data=json.loads(row['session_data'])
                )
        
        return None
    
    def update_session_activity(self, session_id: str,
                               session_data: Dict[str, Any] = None) -> bool:
        """Update session last activity"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if session_data:
                cursor.execute("""
                    UPDATE user_sessions 
                    SET last_activity = CURRENT_TIMESTAMP, session_data = ?
                    WHERE session_id = ?
                """, (json.dumps(session_data), session_id))
            else:
                cursor.execute("""
                    UPDATE user_sessions 
                    SET last_activity = CURRENT_TIMESTAMP
                    WHERE session_id = ?
                """, (session_id,))
            
            success = cursor.rowcount > 0
            conn.commit()
        
        return success
    
    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """Clean up old sessions"""
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM user_sessions 
                WHERE last_activity < ?
            """, (cutoff_date.isoformat(),))
            
            deleted_count = cursor.rowcount
            conn.commit()
        
        self.logger.info(f"Cleaned up {deleted_count} old sessions")
        return deleted_count
    
    # Analytics and Reporting
    def get_database_statistics(self) -> Dict[str, Any]:
        """Get overall database statistics"""
        
        stats = {}
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Resume count
            cursor.execute("SELECT COUNT(*) as count FROM resumes")
            stats['total_resumes'] = cursor.fetchone()['count']
            
            # Scoring count
            cursor.execute("SELECT COUNT(*) as count FROM scoring_history")
            stats['total_scores'] = cursor.fetchone()['count']
            
            # Job template count
            cursor.execute("SELECT COUNT(*) as count FROM job_templates")
            stats['total_job_templates'] = cursor.fetchone()['count']
            
            # Active session count
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute(
                "SELECT COUNT(*) as count FROM user_sessions WHERE last_activity > ?",
                (week_ago,)
            )
            stats['active_sessions'] = cursor.fetchone()['count']
            
            # Average score
            cursor.execute("SELECT AVG(overall_score) as avg_score FROM scoring_history")
            avg_result = cursor.fetchone()
            stats['average_score'] = avg_result['avg_score'] if avg_result['avg_score'] else 0
        
        return stats
    
    def export_data(self, table_name: str, format: str = "json") -> str:
        """Export table data"""
        
        with self.get_connection() as conn:
            if format == "json":
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                data = [dict(row) for row in rows]
                return json.dumps(data, indent=2, default=str)
            
            elif format == "csv":
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                return df.to_csv(index=False)
        
        raise ValueError(f"Unsupported format: {format}")
    
    def backup_database(self, backup_path: str) -> bool:
        """Create database backup"""
        
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            self.logger.info(f"Database backed up to: {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            return False


# Utility functions
def create_sample_job_templates(db_manager: DatabaseManager) -> List[str]:
    """Create sample job templates for testing"""
    
    templates = [
        {
            "title": "Software Engineer",
            "company": "Tech Corp",
            "description": "Develop and maintain web applications using modern technologies.",
            "requirements": {
                "required_skills": ["Python", "JavaScript", "SQL", "Git"],
                "preferred_skills": ["React", "Django", "AWS", "Docker"],
                "experience_years": 3,
                "education": "Bachelor's in Computer Science or related field"
            }
        },
        {
            "title": "Data Scientist",
            "company": "Analytics Inc",
            "description": "Analyze large datasets to derive business insights and build predictive models.",
            "requirements": {
                "required_skills": ["Python", "R", "SQL", "Machine Learning", "Statistics"],
                "preferred_skills": ["TensorFlow", "PyTorch", "Tableau", "Spark"],
                "experience_years": 4,
                "education": "Master's in Data Science, Statistics, or related field"
            }
        },
        {
            "title": "Marketing Manager",
            "company": "Growth Co",
            "description": "Lead marketing campaigns and analyze customer acquisition strategies.",
            "requirements": {
                "required_skills": ["Digital Marketing", "Analytics", "Project Management"],
                "preferred_skills": ["Google Ads", "Facebook Ads", "SEO", "Content Marketing"],
                "experience_years": 5,
                "education": "Bachelor's in Marketing, Business, or related field"
            }
        }
    ]
    
    job_ids = []
    for template in templates:
        job_id = db_manager.store_job_template(**template)
        job_ids.append(job_id)
    
    return job_ids


# Example usage and testing
def test_database_operations():
    """Test database operations"""
    
    # Initialize database
    db_manager = DatabaseManager("test_ats.db")
    
    # Create session
    session_id = db_manager.create_session({"user_type": "test"})
    print(f"Created session: {session_id}")
    
    # Store sample resume
    sample_resume_data = {
        "personal_info": {"name": "John Doe", "email": "john@example.com"},
        "skills": {"technical": ["Python", "SQL"], "soft": ["Communication"]},
        "experience": [{"title": "Developer", "company": "ABC Corp", "duration": "2 years"}]
    }
    
    resume_id = db_manager.store_resume(
        "john_doe_resume.pdf",
        b"sample file content",
        sample_resume_data,
        session_id
    )
    print(f"Stored resume: {resume_id}")
    
    # Store scoring result
    scoring_id = db_manager.store_scoring_result(
        resume_id,
        75.5,
        {"skills": 80, "experience": 70, "education": 75},
        {"version": "1.0", "timestamp": datetime.now().isoformat()},
        user_session=session_id
    )
    print(f"Stored scoring result: {scoring_id}")
    
    # Create sample job templates
    job_ids = create_sample_job_templates(db_manager)
    print(f"Created job templates: {job_ids}")
    
    # Get statistics
    stats = db_manager.get_database_statistics()
    print(f"Database statistics: {stats}")
    
    # Clean up test database
    import os
    if os.path.exists("test_ats.db"):
        os.remove("test_ats.db")
        print("Test database cleaned up")


if __name__ == "__main__":
    test_database_operations()
