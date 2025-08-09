"""
Main Streamlit Application for ATS Resume Scoring System
Professional UI for resume upload, scoring, and recommendations
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import io
import base64
from datetime import datetime
import os
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

try:
    from agents.resume_processor import ResumeProcessingAgent
    from agents.ats_scorer import ATSScoringAgent, ScoringWeights
    from agents.job_analyzer import JobDescriptionAnalyzer
    from agents.improvement_agent import ImprovementRecommendationAgent
    from agents.visualization_agent import VisualizationAgent
    from database.operations import DatabaseManager
    from rag.knowledge_base import RAGKnowledgeBase
    from utils.config import get_autogen_config, is_llm_enabled
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please ensure all required modules are installed and configured properly.")
    st.stop()


class ATSStreamlitApp:
    """Main Streamlit application class"""
    
    def __init__(self):
        self.setup_page_config()
        self.initialize_session_state()
        self.load_configuration()
    
    def setup_page_config(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="Professional ATS Resume Scorer",
            page_icon="📄",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS
        st.markdown("""
        <style>
        .main-header {
            font-size: 3rem;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .score-container {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
        
        .score-excellent {
            background-color: #d4edda;
            border-left: 5px solid #28a745;
        }
        
        .score-good {
            background-color: #d1ecf1;
            border-left: 5px solid #17a2b8;
        }
        
        .score-fair {
            background-color: #fff3cd;
            border-left: 5px solid #ffc107;
        }
        
        .score-poor {
            background-color: #f8d7da;
            border-left: 5px solid #dc3545;
        }
        
        .metric-card {
            background-color: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 0.5rem 0;
        }
        
        .recommendation-item {
            background-color: #e3f2fd;
            padding: 0.8rem;
            margin: 0.5rem 0;
            border-radius: 5px;
            border-left: 3px solid #2196f3;
        }
        
        .upload-section {
            border: 2px dashed #cccccc;
            border-radius: 10px;
            padding: 2rem;
            text-align: center;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def initialize_session_state(self):
        """Initialize Streamlit session state variables"""
        if 'processed_resume' not in st.session_state:
            st.session_state.processed_resume = None
        if 'scoring_result' not in st.session_state:
            st.session_state.scoring_result = None
        if 'job_requirements' not in st.session_state:
            st.session_state.job_requirements = None
        if 'processing_history' not in st.session_state:
            st.session_state.processing_history = []
        if 'current_industry' not in st.session_state:
            st.session_state.current_industry = "general"
    
    def load_configuration(self):
        """Load application configuration"""
        # Use our configuration system instead of Streamlit secrets
        autogen_config = get_autogen_config()
        
        if autogen_config:
            self.config_list = [autogen_config]
        else:
            # Fallback configuration for pure Python mode
            st.warning("⚠️ No LLM configuration found. Running in pure Python mode with limited functionality.")
            self.config_list = None
        
        # Initialize agents
        if self.config_list:
            self.resume_processor = ResumeProcessingAgent(self.config_list)
            self.ats_scorer = ATSScoringAgent(self.config_list)
            self.job_analyzer = JobDescriptionAnalyzer(self.config_list)
            self.improvement_agent = ImprovementRecommendationAgent(self.config_list)
        else:
            # Initialize with fallback or show error
            st.error("❌ Cannot initialize LLM agents without proper configuration. Please check your API keys.")
            st.stop()
        
        self.visualization_agent = VisualizationAgent()
    
    def run(self):
        """Main application entry point"""
        
        # Header
        st.markdown('<h1 class="main-header">🎯 Professional ATS Resume Scorer</h1>', 
                   unsafe_allow_html=True)
        
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
        <p style='font-size: 1.2rem; color: #666;'>
        Get professional ATS scoring with detailed feedback and improvement recommendations
        </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar
        self.render_sidebar()
        
        # Main content tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📄 Resume Upload", 
            "📊 Scoring Results", 
            "💡 Improvements", 
            "🎯 Job Matching",
            "📈 Analytics"
        ])
        
        with tab1:
            self.render_upload_section()
        
        with tab2:
            self.render_scoring_results()
        
        with tab3:
            self.render_improvements()
        
        with tab4:
            self.render_job_matching()
        
        with tab5:
            self.render_analytics()
    
    def render_sidebar(self):
        """Render sidebar with configuration options"""
        
        st.sidebar.header("⚙️ Configuration")
        
        # Industry selection
        industries = [
            "general", "technology", "healthcare", "finance", 
            "marketing", "sales", "education", "consulting"
        ]
        
        selected_industry = st.sidebar.selectbox(
            "Select Industry",
            industries,
            index=industries.index(st.session_state.current_industry)
        )
        
        if selected_industry != st.session_state.current_industry:
            st.session_state.current_industry = selected_industry
            st.rerun()
        
        # Scoring weights customization
        st.sidebar.subheader("📊 Scoring Weights")
        
        with st.sidebar.expander("Customize Weights"):
            skills_weight = st.slider("Skills Match", 0.0, 1.0, 0.30, 0.05)
            experience_weight = st.slider("Experience", 0.0, 1.0, 0.25, 0.05)
            education_weight = st.slider("Education", 0.0, 1.0, 0.15, 0.05)
            format_weight = st.slider("Format", 0.0, 1.0, 0.15, 0.05)
            keyword_weight = st.slider("Keywords", 0.0, 1.0, 0.15, 0.05)
            
            total_weight = skills_weight + experience_weight + education_weight + format_weight + keyword_weight
            
            if abs(total_weight - 1.0) > 0.01:
                st.sidebar.warning(f"Weights should sum to 1.0 (current: {total_weight:.2f})")
            else:
                # Update scoring weights
                self.ats_scorer.weights = ScoringWeights(
                    skills_match=skills_weight,
                    experience_relevance=experience_weight,
                    education_alignment=education_weight,
                    format_structure=format_weight,
                    keyword_optimization=keyword_weight
                )
        
        # Statistics
        st.sidebar.subheader("📈 Statistics")
        history_count = len(st.session_state.processing_history)
        st.sidebar.metric("Resumes Processed", history_count)
        
        if history_count > 0:
            avg_score = sum(h.get('score', 0) for h in st.session_state.processing_history) / history_count
            st.sidebar.metric("Average Score", f"{avg_score:.1f}")
    
    def render_upload_section(self):
        """Render the resume upload section"""
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="upload-section">', unsafe_allow_html=True)
            
            # File upload
            uploaded_file = st.file_uploader(
                "Upload your resume",
                type=['pdf', 'docx', 'txt'],
                help="Supported formats: PDF, DOCX, TXT (Max size: 5MB)"
            )
            
            if uploaded_file is not None:
                # Display file information
                st.success(f"✅ File uploaded: {uploaded_file.name}")
                st.info(f"📁 Size: {uploaded_file.size / 1024:.1f} KB")
                
                # Process button
                if st.button("🚀 Process Resume", type="primary"):
                    self.process_uploaded_resume(uploaded_file)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Sample resumes
            st.subheader("📋 Try Sample Resumes")
            
            sample_files = self.get_sample_resumes()
            if sample_files:
                selected_sample = st.selectbox(
                    "Choose a sample resume:",
                    ["Select..."] + sample_files
                )
                
                if selected_sample != "Select..." and st.button("Load Sample"):
                    self.load_sample_resume(selected_sample)
        
        with col2:
            # Processing tips
            st.markdown("""
            ### 💡 Tips for Best Results
            
            **Resume Format:**
            - Use clear section headers
            - Include quantified achievements
            - List relevant skills
            - Maintain consistent formatting
            
            **Content Tips:**
            - Include contact information
            - Add LinkedIn profile
            - Use action verbs
            - Highlight relevant experience
            
            **File Requirements:**
            - Maximum size: 5MB
            - Supported: PDF, DOCX, TXT
            - Ensure text is selectable
            """)
    
    def process_uploaded_resume(self, uploaded_file):
        """Process the uploaded resume file"""
        
        try:
            with st.spinner("🔄 Processing resume..."):
                # Save uploaded file temporarily
                temp_file_path = f"temp_{uploaded_file.name}"
                
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Process resume
                processed_data = self.resume_processor.process_resume(temp_file_path)
                
                # Clean up temp file
                os.remove(temp_file_path)
                
                # Store in session state
                st.session_state.processed_resume = processed_data
                
                # Score the resume
                self.score_current_resume()
                
                st.success("✅ Resume processed successfully!")
                st.balloons()
        
        except Exception as e:
            st.error(f"❌ Error processing resume: {str(e)}")
    
    def score_current_resume(self):
        """Score the currently processed resume"""
        
        if not st.session_state.processed_resume:
            return
        
        try:
            with st.spinner("📊 Calculating ATS score..."):
                # Score the resume
                scoring_result = self.ats_scorer.score_resume(
                    st.session_state.processed_resume,
                    st.session_state.job_requirements,
                    st.session_state.current_industry
                )
                
                st.session_state.scoring_result = scoring_result
                
                # Add to history
                history_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'filename': st.session_state.processed_resume.get('metadata', {}).get('file_name', 'Unknown'),
                    'score': scoring_result.overall_score,
                    'industry': st.session_state.current_industry
                }
                
                st.session_state.processing_history.append(history_entry)
        
        except Exception as e:
            st.error(f"❌ Error calculating score: {str(e)}")
    
    def render_scoring_results(self):
        """Render the scoring results section"""
        
        if not st.session_state.scoring_result:
            st.info("📄 Please upload and process a resume first.")
            return
        
        result = st.session_state.scoring_result
        
        # Overall score display
        self.display_overall_score(result)
        
        # Category breakdown
        self.display_category_breakdown(result)
        
        # Detailed analysis
        self.display_detailed_analysis(result)
        
        # Export options
        self.render_export_options(result)
    
    def display_overall_score(self, result):
        """Display the overall ATS score"""
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            # Large score display
            score_class = self.get_score_class(result.overall_score)
            
            st.markdown(f"""
            <div class="score-container {score_class}">
                <h2 style="text-align: center; margin: 0;">
                    🎯 ATS Score: {result.overall_score}/100
                </h2>
                <p style="text-align: center; margin: 0.5rem 0;">
                    {self.get_score_interpretation(result.overall_score)}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Confidence interval
            ci_lower, ci_upper = result.confidence_interval
            st.metric(
                "Confidence Range",
                f"{ci_lower:.1f} - {ci_upper:.1f}",
                help="95% confidence interval for the score"
            )
        
        with col3:
            # Benchmark comparison
            benchmark = result.benchmark_comparison
            st.metric(
                "Industry Ranking",
                benchmark['performance_level'],
                f"{benchmark['percentile_estimate']}th percentile"
            )
    
    def display_category_breakdown(self, result):
        """Display category score breakdown"""
        
        st.subheader("📊 Category Breakdown")
        
        # Create radar chart
        categories = list(result.category_scores.keys())
        scores = list(result.category_scores.values())
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=scores,
            theta=[cat.replace('_', ' ').title() for cat in categories],
            fill='toself',
            name='Your Score',
            line_color='#1f77b4'
        ))
        
        # Add industry average
        avg_scores = [70] * len(categories)  # Simplified average
        fig.add_trace(go.Scatterpolar(
            r=avg_scores,
            theta=[cat.replace('_', ' ').title() for cat in categories],
            fill='toself',
            name='Industry Average',
            line_color='#ff7f0e',
            opacity=0.5
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title="Score Comparison by Category"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Category details
        col1, col2 = st.columns(2)
        
        for i, (category, score) in enumerate(result.category_scores.items()):
            col = col1 if i % 2 == 0 else col2
            
            with col:
                progress_color = self.get_progress_color(score)
                
                st.markdown(f"""
                <div class="metric-card">
                    <h4>{category.replace('_', ' ').title()}</h4>
                    <div style="background-color: #f0f0f0; border-radius: 10px; overflow: hidden;">
                        <div style="background-color: {progress_color}; width: {score}%; height: 20px; 
                                    display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                            {score:.1f}%
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    def display_detailed_analysis(self, result):
        """Display detailed scoring analysis"""
        
        st.subheader("🔍 Detailed Analysis")
        
        breakdown = result.detailed_breakdown
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Strengths
            st.markdown("### ✅ Strengths")
            if breakdown.get('strengths'):
                for strength in breakdown['strengths']:
                    st.markdown(f"- {strength}")
            else:
                st.info("No major strengths identified")
        
        with col2:
            # Areas for improvement
            st.markdown("### 🔧 Areas for Improvement")
            if breakdown.get('weaknesses'):
                for weakness in breakdown['weaknesses']:
                    st.markdown(f"- {weakness}")
            else:
                st.success("No major weaknesses identified")
        
        # Missing elements
        if breakdown.get('missing_elements'):
            st.markdown("### ❌ Missing Elements")
            for missing in breakdown['missing_elements']:
                st.markdown(f"- {missing}")
    
    def render_improvements(self):
        """Render the improvements section"""
        
        if not st.session_state.scoring_result:
            st.info("📄 Please process a resume first to see improvement recommendations.")
            return
        
        st.subheader("💡 Personalized Improvement Recommendations")
        
        result = st.session_state.scoring_result
        
        # Priority recommendations
        st.markdown("### 🎯 Priority Actions")
        
        for i, recommendation in enumerate(result.recommendations[:3], 1):
            st.markdown(f"""
            <div class="recommendation-item">
                <strong>Priority {i}:</strong> {recommendation}
            </div>
            """, unsafe_allow_html=True)
        
        # Additional recommendations
        if len(result.recommendations) > 3:
            with st.expander("📋 Additional Recommendations"):
                for recommendation in result.recommendations[3:]:
                    st.markdown(f"- {recommendation}")
        
        # Improvement simulator
        self.render_improvement_simulator()
    
    def render_improvement_simulator(self):
        """Render improvement impact simulator"""
        
        st.subheader("🎮 Improvement Impact Simulator")
        
        st.markdown("See how improvements would affect your score:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Simulate Improvements:**")
            
            skills_boost = st.slider("Skills Enhancement", 0, 30, 0, 
                                   help="Expected improvement in skills score")
            experience_boost = st.slider("Experience Enhancement", 0, 20, 0,
                                       help="Expected improvement in experience score")
            format_boost = st.slider("Format Improvement", 0, 25, 0,
                                   help="Expected improvement in formatting")
            keyword_boost = st.slider("Keyword Optimization", 0, 20, 0,
                                     help="Expected improvement in keyword optimization")
        
        with col2:
            if any([skills_boost, experience_boost, format_boost, keyword_boost]):
                # Calculate simulated score
                current_result = st.session_state.scoring_result
                simulated_scores = current_result.category_scores.copy()
                
                simulated_scores['skills_match'] = min(100, 
                    simulated_scores['skills_match'] + skills_boost)
                simulated_scores['experience_relevance'] = min(100, 
                    simulated_scores['experience_relevance'] + experience_boost)
                simulated_scores['format_structure'] = min(100, 
                    simulated_scores['format_structure'] + format_boost)
                simulated_scores['keyword_optimization'] = min(100, 
                    simulated_scores['keyword_optimization'] + keyword_boost)
                
                # Calculate new overall score
                weights = self.ats_scorer.weights
                new_overall = (
                    simulated_scores['skills_match'] * weights.skills_match +
                    simulated_scores['experience_relevance'] * weights.experience_relevance +
                    simulated_scores['education_alignment'] * weights.education_alignment +
                    simulated_scores['format_structure'] * weights.format_structure +
                    simulated_scores['keyword_optimization'] * weights.keyword_optimization
                )
                
                improvement = new_overall - current_result.overall_score
                
                st.metric("Simulated Score", f"{new_overall:.1f}", f"+{improvement:.1f}")
                
                if improvement > 0:
                    st.success(f"🎉 Potential improvement: +{improvement:.1f} points!")
    
    def render_job_matching(self):
        """Render job matching section"""
        
        st.subheader("🎯 Job Description Matching")
        
        # Job description input
        col1, col2 = st.columns([2, 1])
        
        with col1:
            job_description = st.text_area(
                "Paste Job Description",
                height=200,
                placeholder="Paste the full job description here for targeted analysis..."
            )
            
            if job_description and st.button("🔍 Analyze Job Match"):
                self.analyze_job_match(job_description)
        
        with col2:
            st.markdown("""
            ### 🎯 Job Matching Benefits
            
            - **Targeted Scoring**: Score against specific job requirements
            - **Keyword Analysis**: Identify missing keywords
            - **Skill Gap Analysis**: See required vs. current skills
            - **Customized Recommendations**: Get job-specific advice
            """)
        
        # Display current job requirements if any
        if st.session_state.job_requirements:
            self.display_job_analysis()
    
    def analyze_job_match(self, job_description):
        """Analyze job description and update requirements"""
        
        try:
            with st.spinner("🔄 Analyzing job description..."):
                # Extract requirements from job description
                job_requirements = self.job_analyzer.analyze_job_description(job_description)
                st.session_state.job_requirements = job_requirements
                
                # Re-score if resume is processed
                if st.session_state.processed_resume:
                    self.score_current_resume()
                
                st.success("✅ Job description analyzed successfully!")
        
        except Exception as e:
            st.error(f"❌ Error analyzing job description: {str(e)}")
    
    def display_job_analysis(self):
        """Display job analysis results"""
        
        st.subheader("📋 Job Requirements Analysis")
        
        req = st.session_state.job_requirements
        
        col1, col2 = st.columns(2)
        
        with col1:
            if req.get('required_skills'):
                st.markdown("**Required Skills:**")
                for skill in req['required_skills']:
                    st.markdown(f"- {skill}")
        
        with col2:
            if req.get('preferred_experience'):
                st.markdown("**Preferred Experience:**")
                for exp in req['preferred_experience']:
                    st.markdown(f"- {exp}")
        
        # Skill gap analysis
        if st.session_state.processed_resume:
            self.display_skill_gap_analysis()
    
    def display_skill_gap_analysis(self):
        """Display skill gap analysis"""
        
        st.subheader("📊 Skill Gap Analysis")
        
        resume_data = st.session_state.processed_resume
        job_req = st.session_state.job_requirements
        
        # Extract resume skills
        skills = resume_data.get('skills', {})
        all_resume_skills = []
        for skill_category in skills.values():
            if isinstance(skill_category, list):
                all_resume_skills.extend([skill.lower() for skill in skill_category])
        
        # Required skills
        required_skills = [skill.lower() for skill in job_req.get('required_skills', [])]
        
        # Calculate matches and gaps
        matched_skills = list(set(all_resume_skills) & set(required_skills))
        missing_skills = list(set(required_skills) - set(all_resume_skills))
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ✅ Matched Skills")
            for skill in matched_skills:
                st.markdown(f"- {skill.title()}")
        
        with col2:
            st.markdown("### ❌ Missing Skills")
            for skill in missing_skills:
                st.markdown(f"- {skill.title()}")
        
        # Match percentage
        if required_skills:
            match_percentage = (len(matched_skills) / len(required_skills)) * 100
            st.metric("Skill Match Rate", f"{match_percentage:.1f}%")
    
    def render_analytics(self):
        """Render analytics and statistics"""
        
        st.subheader("📈 Analytics Dashboard")
        
        if not st.session_state.processing_history:
            st.info("📊 No data available yet. Process some resumes to see analytics.")
            return
        
        # Processing history
        df = pd.DataFrame(st.session_state.processing_history)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Score distribution
            fig = px.histogram(df, x='score', nbins=10, 
                             title="Score Distribution",
                             labels={'score': 'ATS Score', 'count': 'Frequency'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Scores over time
            fig = px.line(df, x='timestamp', y='score', 
                         title="Score Trends",
                         labels={'timestamp': 'Date', 'score': 'ATS Score'})
            st.plotly_chart(fig, use_container_width=True)
        
        # Statistics table
        st.subheader("📊 Processing Statistics")
        
        stats = {
            'Total Resumes': len(df),
            'Average Score': f"{df['score'].mean():.1f}",
            'Highest Score': f"{df['score'].max():.1f}",
            'Lowest Score': f"{df['score'].min():.1f}",
            'Score Standard Deviation': f"{df['score'].std():.1f}"
        }
        
        for key, value in stats.items():
            st.metric(key, value)
    
    def render_export_options(self, result):
        """Render export options for results"""
        
        st.subheader("📥 Export Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Export PDF Report"):
                pdf_data = self.generate_pdf_report(result)
                st.download_button(
                    label="Download PDF",
                    data=pdf_data,
                    file_name=f"ats_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
        
        with col2:
            if st.button("📊 Export CSV Data"):
                csv_data = self.generate_csv_export(result)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"ats_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col3:
            if st.button("📋 Export JSON"):
                json_data = self.generate_json_export(result)
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name=f"ats_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    
    def get_score_class(self, score):
        """Get CSS class based on score"""
        if score >= 90:
            return "score-excellent"
        elif score >= 75:
            return "score-good"
        elif score >= 60:
            return "score-fair"
        else:
            return "score-poor"
    
    def get_score_interpretation(self, score):
        """Get score interpretation text"""
        if score >= 90:
            return "Excellent - Top candidate profile"
        elif score >= 75:
            return "Good - Strong candidate"
        elif score >= 60:
            return "Fair - Some improvements needed"
        else:
            return "Needs significant improvement"
    
    def get_progress_color(self, score):
        """Get progress bar color based on score"""
        if score >= 90:
            return "#28a745"
        elif score >= 75:
            return "#17a2b8"
        elif score >= 60:
            return "#ffc107"
        else:
            return "#dc3545"
    
    def get_sample_resumes(self):
        """Get list of sample resume files"""
        sample_dir = Path(__file__).parent.parent / "data" / "sample_resumes"
        if sample_dir.exists():
            return [f.name for f in sample_dir.glob("*") if f.suffix in ['.pdf', '.docx', '.txt']]
        return []
    
    def load_sample_resume(self, filename):
        """Load a sample resume"""
        sample_path = Path(__file__).parent.parent / "data" / "sample_resumes" / filename
        if sample_path.exists():
            try:
                processed_data = self.resume_processor.process_resume(str(sample_path))
                st.session_state.processed_resume = processed_data
                self.score_current_resume()
                st.success(f"✅ Sample resume '{filename}' loaded successfully!")
            except Exception as e:
                st.error(f"❌ Error loading sample resume: {str(e)}")
    
    def generate_pdf_report(self, result):
        """Generate PDF report (simplified)"""
        # This would typically use a library like ReportLab
        # For now, return a simple text representation
        report_text = f"""
        ATS Resume Scoring Report
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Overall Score: {result.overall_score}/100
        
        Category Breakdown:
        {json.dumps(result.category_scores, indent=2)}
        
        Recommendations:
        {chr(10).join(f'- {rec}' for rec in result.recommendations)}
        """
        return report_text.encode()
    
    def generate_csv_export(self, result):
        """Generate CSV export"""
        data = {
            'Category': list(result.category_scores.keys()),
            'Score': list(result.category_scores.values())
        }
        df = pd.DataFrame(data)
        return df.to_csv(index=False)
    
    def generate_json_export(self, result):
        """Generate JSON export"""
        export_data = {
            'overall_score': result.overall_score,
            'category_scores': result.category_scores,
            'confidence_interval': result.confidence_interval,
            'recommendations': result.recommendations,
            'export_timestamp': datetime.now().isoformat()
        }
        return json.dumps(export_data, indent=2)


# Main application entry point
def main():
    """Main function to run the Streamlit app"""
    app = ATSStreamlitApp()
    app.run()


if __name__ == "__main__":
    main()
