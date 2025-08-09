"""
Visualization Agent for ATS System
Creates professional charts, graphs, and visual reports
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import json
from datetime import datetime
import base64
import io


class VisualizationAgent:
    """
    Agent for creating professional visualizations and reports
    No AutoGen dependency - pure visualization functionality
    """
    
    def __init__(self):
        self.visualization_history = []
        self.color_palette = {
            "primary": "#1f77b4",
            "secondary": "#ff7f0e", 
            "success": "#2ca02c",
            "warning": "#d62728",
            "info": "#9467bd",
            "light": "#8c564b",
            "dark": "#e377c2"
        }
    
    def create_score_dashboard(self, scoring_result: Any, 
                             benchmark_data: Dict[str, Any] = None) -> Dict[str, go.Figure]:
        """
        Create comprehensive scoring dashboard
        
        Args:
            scoring_result: ATS scoring results
            benchmark_data: Industry benchmark data
            
        Returns:
            Dictionary of Plotly figures for dashboard
        """
        
        dashboard = {}
        
        # 1. Overall Score Gauge
        dashboard["score_gauge"] = self._create_score_gauge(scoring_result.overall_score)
        
        # 2. Category Breakdown Radar Chart
        dashboard["radar_chart"] = self._create_radar_chart(
            scoring_result.category_scores, benchmark_data
        )
        
        # 3. Category Bar Chart
        dashboard["bar_chart"] = self._create_category_bar_chart(scoring_result.category_scores)
        
        # 4. Score Distribution Comparison
        if benchmark_data:
            dashboard["distribution"] = self._create_score_distribution(
                scoring_result.overall_score, benchmark_data
            )
        
        # 5. Improvement Potential Chart
        dashboard["improvement_potential"] = self._create_improvement_potential_chart(
            scoring_result.category_scores
        )
        
        # Log visualization creation
        self._log_visualization("score_dashboard", scoring_result.overall_score)
        
        return dashboard
    
    def create_comparison_charts(self, resume_scores: List[Dict[str, Any]],
                               labels: List[str] = None) -> Dict[str, go.Figure]:
        """
        Create comparison charts for multiple resumes
        
        Args:
            resume_scores: List of scoring results
            labels: Optional labels for each resume
            
        Returns:
            Dictionary of comparison charts
        """
        
        if not labels:
            labels = [f"Resume {i+1}" for i in range(len(resume_scores))]
        
        comparison_charts = {}
        
        # 1. Overall Score Comparison
        comparison_charts["overall_comparison"] = self._create_overall_score_comparison(
            resume_scores, labels
        )
        
        # 2. Category Heatmap
        comparison_charts["category_heatmap"] = self._create_category_heatmap(
            resume_scores, labels
        )
        
        # 3. Score Trends (if historical data)
        if len(resume_scores) > 1:
            comparison_charts["score_trends"] = self._create_score_trends(
                resume_scores, labels
            )
        
        return comparison_charts
    
    def create_improvement_visualizations(self, current_scores: Dict[str, float],
                                        improvement_recommendations: Dict[str, Any],
                                        projected_scores: Dict[str, float] = None) -> Dict[str, go.Figure]:
        """
        Create improvement-focused visualizations
        
        Args:
            current_scores: Current category scores
            improvement_recommendations: Improvement recommendations
            projected_scores: Projected scores after improvements
            
        Returns:
            Dictionary of improvement visualizations
        """
        
        improvement_viz = {}
        
        # 1. Before/After Comparison
        if projected_scores:
            improvement_viz["before_after"] = self._create_before_after_comparison(
                current_scores, projected_scores
            )
        
        # 2. Improvement Priority Matrix
        improvement_viz["priority_matrix"] = self._create_improvement_priority_matrix(
            current_scores, improvement_recommendations
        )
        
        # 3. Quick Wins vs Long-term Chart
        improvement_viz["effort_impact"] = self._create_effort_impact_chart(
            improvement_recommendations
        )
        
        # 4. Skill Gap Analysis
        if "skill_development" in improvement_recommendations:
            improvement_viz["skill_gaps"] = self._create_skill_gap_visualization(
                improvement_recommendations["skill_development"]
            )
        
        return improvement_viz
    
    def create_job_matching_visualizations(self, resume_data: Dict[str, Any],
                                         job_requirements: Dict[str, Any],
                                         matching_analysis: Dict[str, Any]) -> Dict[str, go.Figure]:
        """
        Create job matching visualizations
        
        Args:
            resume_data: Processed resume data
            job_requirements: Job requirements data
            matching_analysis: Matching analysis results
            
        Returns:
            Dictionary of job matching visualizations
        """
        
        job_viz = {}
        
        # 1. Skill Match Analysis
        job_viz["skill_match"] = self._create_skill_match_chart(
            resume_data, job_requirements
        )
        
        # 2. Requirements Fulfillment
        job_viz["requirements_fulfillment"] = self._create_requirements_fulfillment_chart(
            matching_analysis
        )
        
        # 3. Experience Alignment
        job_viz["experience_alignment"] = self._create_experience_alignment_chart(
            resume_data, job_requirements
        )
        
        # 4. Keyword Coverage
        job_viz["keyword_coverage"] = self._create_keyword_coverage_chart(
            resume_data, job_requirements
        )
        
        return job_viz
    
    def _create_score_gauge(self, score: float) -> go.Figure:
        """Create a gauge chart for overall score"""
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Overall ATS Score"},
            delta = {'reference': 70},  # Average score reference
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': self._get_score_color(score)},
                'steps': [
                    {'range': [0, 50], 'color': "#ffebee"},
                    {'range': [50, 70], 'color': "#fff3e0"},
                    {'range': [70, 85], 'color': "#e8f5e8"},
                    {'range': [85, 100], 'color': "#e3f2fd"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            height=400,
            font={'color': "darkblue", 'family': "Arial"},
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        return fig
    
    def _create_radar_chart(self, category_scores: Dict[str, float],
                           benchmark_data: Dict[str, Any] = None) -> go.Figure:
        """Create radar chart for category scores"""
        
        categories = list(category_scores.keys())
        scores = list(category_scores.values())
        
        # Format category names for display
        category_labels = [cat.replace('_', ' ').title() for cat in categories]
        
        fig = go.Figure()
        
        # Add resume scores
        fig.add_trace(go.Scatterpolar(
            r=scores,
            theta=category_labels,
            fill='toself',
            name='Your Score',
            line_color=self.color_palette["primary"],
            fillcolor=f'rgba(31, 119, 180, 0.3)'
        ))
        
        # Add benchmark if available
        if benchmark_data and "average_scores" in benchmark_data:
            benchmark_scores = [benchmark_data["average_scores"].get(cat, 70) for cat in categories]
            
            fig.add_trace(go.Scatterpolar(
                r=benchmark_scores,
                theta=category_labels,
                fill='toself',
                name='Industry Average',
                line_color=self.color_palette["secondary"],
                fillcolor=f'rgba(255, 127, 14, 0.2)'
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title="Score Breakdown by Category",
            height=500,
            margin=dict(l=80, r=80, t=100, b=80)
        )
        
        return fig
    
    def _create_category_bar_chart(self, category_scores: Dict[str, float]) -> go.Figure:
        """Create horizontal bar chart for category scores"""
        
        categories = [cat.replace('_', ' ').title() for cat in category_scores.keys()]
        scores = list(category_scores.values())
        colors = [self._get_score_color(score) for score in scores]
        
        fig = go.Figure(go.Bar(
            x=scores,
            y=categories,
            orientation='h',
            marker_color=colors,
            text=[f'{score:.1f}%' for score in scores],
            textposition='inside',
            textfont=dict(color='white', size=12)
        ))
        
        fig.update_layout(
            title="Category Score Breakdown",
            xaxis_title="Score",
            yaxis_title="Categories",
            height=400,
            margin=dict(l=150, r=50, t=50, b=50),
            xaxis=dict(range=[0, 100])
        )
        
        return fig
    
    def _create_score_distribution(self, user_score: float,
                                 benchmark_data: Dict[str, Any]) -> go.Figure:
        """Create score distribution chart with user position"""
        
        # Generate sample distribution data (in real implementation, use actual data)
        np.random.seed(42)
        scores = np.random.normal(70, 15, 1000)
        scores = np.clip(scores, 0, 100)
        
        fig = go.Figure()
        
        # Add histogram
        fig.add_trace(go.Histogram(
            x=scores,
            nbinsx=20,
            name='Score Distribution',
            marker_color=self.color_palette["info"],
            opacity=0.7
        ))
        
        # Add user score line
        fig.add_vline(
            x=user_score,
            line_dash="dash",
            line_color=self.color_palette["warning"],
            annotation_text=f"Your Score: {user_score:.1f}",
            annotation_position="top"
        )
        
        # Add benchmark lines
        if "average_score" in benchmark_data:
            fig.add_vline(
                x=benchmark_data["average_score"],
                line_dash="dot",
                line_color=self.color_palette["secondary"],
                annotation_text=f"Industry Avg: {benchmark_data['average_score']:.1f}",
                annotation_position="bottom"
            )
        
        fig.update_layout(
            title="Score Distribution vs Industry Benchmark",
            xaxis_title="ATS Score",
            yaxis_title="Frequency",
            height=400,
            showlegend=True
        )
        
        return fig
    
    def _create_improvement_potential_chart(self, category_scores: Dict[str, float]) -> go.Figure:
        """Create chart showing improvement potential by category"""
        
        categories = [cat.replace('_', ' ').title() for cat in category_scores.keys()]
        current_scores = list(category_scores.values())
        
        # Calculate improvement potential (simplified)
        max_realistic_scores = [min(score + (100 - score) * 0.7, 95) for score in current_scores]
        improvement_potential = [max_score - current for max_score, current in 
                               zip(max_realistic_scores, current_scores)]
        
        fig = go.Figure()
        
        # Current scores
        fig.add_trace(go.Bar(
            name='Current Score',
            x=categories,
            y=current_scores,
            marker_color=self.color_palette["primary"]
        ))
        
        # Improvement potential
        fig.add_trace(go.Bar(
            name='Improvement Potential',
            x=categories,
            y=improvement_potential,
            base=current_scores,
            marker_color=self.color_palette["success"],
            opacity=0.7
        ))
        
        fig.update_layout(
            title="Current Score vs Improvement Potential",
            xaxis_title="Categories",
            yaxis_title="Score",
            barmode='overlay',
            height=400,
            yaxis=dict(range=[0, 100])
        )
        
        return fig
    
    def _create_before_after_comparison(self, current_scores: Dict[str, float],
                                      projected_scores: Dict[str, float]) -> go.Figure:
        """Create before/after comparison chart"""
        
        categories = [cat.replace('_', ' ').title() for cat in current_scores.keys()]
        current = list(current_scores.values())
        projected = list(projected_scores.values())
        
        x = np.arange(len(categories))
        width = 0.35
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Current',
            x=[cat + ' (Current)' for cat in categories],
            y=current,
            marker_color=self.color_palette["primary"]
        ))
        
        fig.add_trace(go.Bar(
            name='Projected',
            x=[cat + ' (Projected)' for cat in categories],
            y=projected,
            marker_color=self.color_palette["success"]
        ))
        
        fig.update_layout(
            title="Before vs After: Projected Score Improvements",
            xaxis_title="Categories",
            yaxis_title="Score",
            height=400,
            yaxis=dict(range=[0, 100])
        )
        
        return fig
    
    def _create_skill_match_chart(self, resume_data: Dict[str, Any],
                                job_requirements: Dict[str, Any]) -> go.Figure:
        """Create skill matching visualization"""
        
        # Extract skills from resume
        skills = resume_data.get("skills", {})
        all_resume_skills = []
        for skill_category in skills.values():
            if isinstance(skill_category, list):
                all_resume_skills.extend([skill.lower() for skill in skill_category])
        
        # Get required skills from job
        required_skills = [skill.lower() for skill in job_requirements.get("required_skills", [])]
        preferred_skills = [skill.lower() for skill in job_requirements.get("preferred_skills", [])]
        
        # Calculate matches
        matched_required = [skill for skill in required_skills if skill in all_resume_skills]
        matched_preferred = [skill for skill in preferred_skills if skill in all_resume_skills]
        missing_required = [skill for skill in required_skills if skill not in all_resume_skills]
        missing_preferred = [skill for skill in preferred_skills if skill not in all_resume_skills]
        
        # Create skill match data
        skill_data = {
            'Category': ['Required Skills', 'Preferred Skills'],
            'Matched': [len(matched_required), len(matched_preferred)],
            'Missing': [len(missing_required), len(missing_preferred)]
        }
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Matched',
            x=skill_data['Category'],
            y=skill_data['Matched'],
            marker_color=self.color_palette["success"]
        ))
        
        fig.add_trace(go.Bar(
            name='Missing',
            x=skill_data['Category'],
            y=skill_data['Missing'],
            marker_color=self.color_palette["warning"]
        ))
        
        fig.update_layout(
            title="Skill Match Analysis",
            xaxis_title="Skill Categories",
            yaxis_title="Number of Skills",
            barmode='group',
            height=400
        )
        
        return fig
    
    def _create_improvement_priority_matrix(self, current_scores: Dict[str, float],
                                          improvement_recommendations: Dict[str, Any]) -> go.Figure:
        """Create improvement priority matrix"""
        
        # Extract priority actions if available
        priority_actions = improvement_recommendations.get("priority_actions", [])
        
        if not priority_actions:
            # Create sample data based on scores
            categories = list(current_scores.keys())
            efforts = [3 - (score // 30) for score in current_scores.values()]  # Lower score = higher effort
            impacts = [4 - (score // 25) for score in current_scores.values()]  # Lower score = higher impact
            
            fig = go.Figure(go.Scatter(
                x=efforts,
                y=impacts,
                mode='markers+text',
                text=[cat.replace('_', ' ').title() for cat in categories],
                textposition="middle center",
                marker=dict(
                    size=[60] * len(categories),
                    color=list(current_scores.values()),
                    colorscale='RdYlGn',
                    colorbar=dict(title="Current Score"),
                    showscale=True
                )
            ))
        else:
            # Use actual priority actions
            actions = [action["action"] for action in priority_actions[:5]]  # Top 5
            efforts = []
            impacts = []
            
            for action in priority_actions[:5]:
                effort_map = {"Low": 1, "Medium": 2, "High": 3}
                impact_map = {"Low": 1, "Medium": 2, "High": 3}
                
                efforts.append(effort_map.get(action.get("effort", "Medium"), 2))
                impacts.append(impact_map.get(action.get("impact", "Medium"), 2))
            
            fig = go.Figure(go.Scatter(
                x=efforts,
                y=impacts,
                mode='markers+text',
                text=actions,
                textposition="middle center",
                marker=dict(
                    size=60,
                    color=self.color_palette["primary"],
                    opacity=0.7
                )
            ))
        
        fig.update_layout(
            title="Improvement Priority Matrix",
            xaxis_title="Implementation Effort",
            yaxis_title="Impact Level",
            xaxis=dict(tickmode='array', tickvals=[1, 2, 3], ticktext=['Low', 'Medium', 'High']),
            yaxis=dict(tickmode='array', tickvals=[1, 2, 3], ticktext=['Low', 'Medium', 'High']),
            height=400
        )
        
        return fig
    
    def _get_score_color(self, score: float) -> str:
        """Get color based on score value"""
        if score >= 90:
            return "#2ca02c"  # Green
        elif score >= 75:
            return "#1f77b4"  # Blue
        elif score >= 60:
            return "#ff7f0e"  # Orange
        else:
            return "#d62728"  # Red
    
    def _log_visualization(self, viz_type: str, score: float = None):
        """Log visualization creation"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "visualization_type": viz_type,
            "score": score
        }
        self.visualization_history.append(log_entry)
    
    def export_chart_as_image(self, fig: go.Figure, format: str = "png") -> str:
        """Export chart as base64 encoded image"""
        
        img_bytes = fig.to_image(format=format, width=800, height=600)
        img_base64 = base64.b64encode(img_bytes).decode()
        
        return img_base64
    
    def create_report_summary(self, scoring_result: Any,
                             improvement_recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary data for reports"""
        
        summary = {
            "overall_performance": {
                "score": scoring_result.overall_score,
                "grade": self._get_letter_grade(scoring_result.overall_score),
                "percentile": scoring_result.benchmark_comparison.get("percentile_estimate", 50)
            },
            "category_performance": {
                category: {
                    "score": score,
                    "level": self._get_performance_level(score)
                }
                for category, score in scoring_result.category_scores.items()
            },
            "improvement_summary": {
                "priority_count": len(improvement_recommendations.get("priority_actions", [])),
                "quick_wins": len(improvement_recommendations.get("quick_wins", [])),
                "potential_improvement": sum(improvement_recommendations["metadata"]
                                           .get("score_improvement_potential", {}).values())
            },
            "recommendations_by_effort": {
                "low_effort": [],
                "medium_effort": [],
                "high_effort": []
            }
        }
        
        # Categorize recommendations by effort
        for action in improvement_recommendations.get("priority_actions", []):
            effort = action.get("effort", "Medium").lower()
            if effort in summary["recommendations_by_effort"]:
                summary["recommendations_by_effort"][effort].append(action["action"])
        
        return summary
    
    def _get_letter_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _get_performance_level(self, score: float) -> str:
        """Get performance level description"""
        if score >= 90:
            return "Excellent"
        elif score >= 75:
            return "Good"
        elif score >= 60:
            return "Fair"
        else:
            return "Needs Improvement"
    
    def get_visualization_statistics(self) -> Dict[str, Any]:
        """Get visualization creation statistics"""
        
        if not self.visualization_history:
            return {"message": "No visualization history available"}
        
        viz_types = {}
        for log in self.visualization_history:
            viz_type = log["visualization_type"]
            viz_types[viz_type] = viz_types.get(viz_type, 0) + 1
        
        stats = {
            "total_visualizations": len(self.visualization_history),
            "visualization_types": viz_types,
            "average_score": np.mean([log["score"] for log in self.visualization_history 
                                    if log["score"] is not None])
        }
        
        return stats


# Additional utility functions for chart creation
def _create_effort_impact_chart(improvement_recommendations: Dict[str, Any]) -> go.Figure:
    """Create effort vs impact chart for improvements"""
    
    quick_wins = improvement_recommendations.get("quick_wins", [])
    priority_actions = improvement_recommendations.get("priority_actions", [])
    
    # Create data for plotting
    items = []
    efforts = []
    impacts = []
    categories = []
    
    # Add quick wins
    for item in quick_wins:
        items.append(item.get("action", "Quick Win"))
        efforts.append(1)  # Low effort
        impacts.append(2)  # Medium impact
        categories.append("Quick Win")
    
    # Add priority actions
    effort_map = {"Low": 1, "Medium": 2, "High": 3}
    impact_map = {"Low": 1, "Medium": 2, "High": 3}
    
    for item in priority_actions:
        items.append(item.get("action", "Priority Action"))
        efforts.append(effort_map.get(item.get("effort", "Medium"), 2))
        impacts.append(impact_map.get(item.get("impact", "Medium"), 2))
        categories.append("Priority Action")
    
    fig = go.Figure()
    
    # Add quick wins
    quick_win_indices = [i for i, cat in enumerate(categories) if cat == "Quick Win"]
    if quick_win_indices:
        fig.add_trace(go.Scatter(
            x=[efforts[i] for i in quick_win_indices],
            y=[impacts[i] for i in quick_win_indices],
            text=[items[i] for i in quick_win_indices],
            mode='markers+text',
            name='Quick Wins',
            marker=dict(size=15, color='green'),
            textposition="middle center"
        ))
    
    # Add priority actions
    priority_indices = [i for i, cat in enumerate(categories) if cat == "Priority Action"]
    if priority_indices:
        fig.add_trace(go.Scatter(
            x=[efforts[i] for i in priority_indices],
            y=[impacts[i] for i in priority_indices],
            text=[items[i] for i in priority_indices],
            mode='markers+text',
            name='Priority Actions',
            marker=dict(size=15, color='blue'),
            textposition="middle center"
        ))
    
    fig.update_layout(
        title="Effort vs Impact: Improvement Recommendations",
        xaxis_title="Implementation Effort",
        yaxis_title="Expected Impact",
        xaxis=dict(tickmode='array', tickvals=[1, 2, 3], ticktext=['Low', 'Medium', 'High']),
        yaxis=dict(tickmode='array', tickvals=[1, 2, 3], ticktext=['Low', 'Medium', 'High']),
        height=400,
        showlegend=True
    )
    
    return fig


def _create_skill_gap_visualization(skill_development: Dict[str, List[str]]) -> go.Figure:
    """Create skill gap visualization"""
    
    immediate_skills = skill_development.get("immediate_skills", [])
    long_term_skills = skill_development.get("long_term_development", [])
    certifications = skill_development.get("certifications", [])
    
    # Create data for plotting
    skill_types = []
    skill_counts = []
    
    if immediate_skills:
        skill_types.append("Immediate Skills")
        skill_counts.append(len(immediate_skills))
    
    if long_term_skills:
        skill_types.append("Long-term Skills")
        skill_counts.append(len(long_term_skills))
    
    if certifications:
        skill_types.append("Certifications")
        skill_counts.append(len(certifications))
    
    if not skill_types:
        # Create empty chart
        fig = go.Figure()
        fig.add_annotation(
            text="No skill gap data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(title="Skill Gap Analysis", height=400)
        return fig
    
    fig = go.Figure(go.Bar(
        x=skill_types,
        y=skill_counts,
        marker_color=['#ff7f0e', '#2ca02c', '#1f77b4'],
        text=skill_counts,
        textposition='auto'
    ))
    
    fig.update_layout(
        title="Skill Development Recommendations",
        xaxis_title="Skill Categories",
        yaxis_title="Number of Skills",
        height=400
    )
    
    return fig


# Example usage and testing
def test_visualization_agent():
    """Test function for the Visualization Agent"""
    
    # Mock scoring result
    class MockScoringResult:
        overall_score = 75
        category_scores = {
            "skills_match": 80,
            "experience_relevance": 70,
            "education_alignment": 75,
            "format_structure": 85,
            "keyword_optimization": 65
        }
        benchmark_comparison = {"percentile_estimate": 65}
    
    mock_result = MockScoringResult()
    
    # Initialize visualization agent
    viz_agent = VisualizationAgent()
    
    # Create dashboard
    dashboard = viz_agent.create_score_dashboard(mock_result)
    
    print("Dashboard created with charts:")
    for chart_name in dashboard.keys():
        print(f"- {chart_name}")
    
    # Test individual chart
    gauge_chart = dashboard["score_gauge"]
    print(f"\nGauge chart created successfully: {type(gauge_chart)}")


if __name__ == "__main__":
    test_visualization_agent()
