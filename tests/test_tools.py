"""
Pytest Test Suite for Content Creation Tools
Updated for CrewAI Integration with Free LLMs
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from tools.tone_analyzer import tone_analyzer
from tools.seo_optimizer import seo_optimizer
from tools.research_tool import research_tool


class TestToneAnalyzer:
    """Test suite for Tone Analyzer tool"""
    
    @pytest.fixture
    def casual_text(self):
        """Casual text sample"""
        return """
        Hey! So I've been using Docker for a while now and it's pretty awesome. 
        You should definitely try it out. It'll make your life so much easier!
        Docker containers are super convenient and they just work everywhere.
        """
    
    @pytest.fixture
    def formal_text(self):
        """Formal text sample"""
        return """
        Docker containerization represents a significant advancement in software deployment.
        Organizations implementing this technology report substantial improvements in efficiency.
        The platform demonstrates considerable potential for enterprise applications.
        Docker architecture facilitates consistent deployment across diverse environments.
        """
    
    def test_analyzer_initializes(self):
        """Test that analyzer initializes correctly"""
        assert tone_analyzer is not None
        assert tone_analyzer.name == "Tone Analyzer"
        assert "Analyzes writing style" in tone_analyzer.description
    
    def test_casual_tone_detection(self, casual_text):
        """Test detection of casual tone"""
        result = tone_analyzer._run(casual_text, "casual")
        assert result is not None
        assert "Casual" in result or "Conversational" in result
        assert "TONE ANALYSIS RESULTS" in result
    
    def test_formal_tone_detection(self, formal_text):
        """Test detection of formal tone"""
        result = tone_analyzer._run(formal_text, "formal")
        assert result is not None
        assert "Formal" in result or "Professional" in result
    
    def test_short_text_error(self):
        """Test error handling for short text"""
        result = tone_analyzer._run("Too short", "professional")
        assert "Error" in result or "too short" in result.lower()
    
    def test_metrics_extraction(self, casual_text):
        """Test that metrics are calculated"""
        result = tone_analyzer._run(casual_text, "casual")
        assert "Flesch Reading Ease" in result
        assert "Grade Level" in result
        assert "Formality:" in result
        assert "TONE PROFILE:" in result
    
    def test_target_tone_assessment(self, casual_text):
        """Test target tone matching"""
        result = tone_analyzer._run(casual_text, "professional")
        assert "TARGET TONE ASSESSMENT" in result
        assert "Target: professional" in result
    
    def test_style_guidelines(self, formal_text):
        """Test style guidelines generation"""
        result = tone_analyzer._run(formal_text, "formal")
        assert "STYLE GUIDELINES" in result
        assert "RECOMMENDED APPROACH" in result


class TestSEOOptimizer:
    """Test suite for SEO Optimizer tool"""
    
    @pytest.fixture
    def good_content(self):
        """Well-structured content sample"""
        return """
# Docker Containerization Guide

Docker is a powerful platform for containerization. This guide covers Docker basics.

## What is Docker?

Docker allows you to package applications with dependencies. It's used by many developers.

## Benefits of Docker

Docker provides portability and consistency. Teams use Docker for deployment worldwide.

## Getting Started

To start with Docker, install it first. Then create your first container.

## Docker Commands

Learn essential Docker commands for container management. Docker CLI is powerful.

## Conclusion

Docker simplifies deployment. Start using Docker today for better workflows.
        """
    
    @pytest.fixture
    def short_content(self):
        """Too short content"""
        return "Docker is great!"
    
    def test_optimizer_initializes(self):
        """Test that optimizer initializes correctly"""
        assert seo_optimizer is not None
        assert seo_optimizer.name == "SEO Optimizer"
        assert "SEO effectiveness" in seo_optimizer.description
    
    def test_seo_score_calculation(self, good_content):
        """Test that SEO score is calculated"""
        result = seo_optimizer._run(good_content, "Docker")
        assert "SEO SCORE:" in result
        assert "/100" in result
    
    def test_keyword_analysis(self, good_content):
        """Test keyword analysis with target keyword"""
        result = seo_optimizer._run(good_content, "Docker")
        assert "KEYWORD ANALYSIS" in result
        assert "Target Keyword: Docker" in result
        assert "Keyword Count:" in result
        assert "Keyword Density:" in result
    
    def test_readability_metrics(self, good_content):
        """Test readability calculation"""
        result = seo_optimizer._run(good_content)
        assert "Flesch Reading Ease" in result
        assert "Grade Level" in result
        assert "READABILITY:" in result
    
    def test_structure_analysis(self, good_content):
        """Test content structure analysis"""
        result = seo_optimizer._run(good_content)
        assert "H1 Headers:" in result
        assert "H2 Headers:" in result
        assert "STRUCTURE:" in result
    
    def test_recommendations_generated(self, good_content):
        """Test that recommendations are provided"""
        result = seo_optimizer._run(good_content)
        assert "RECOMMENDATIONS" in result
    
    def test_short_content_handling(self, short_content):
        """Test handling of too short content"""
        result = seo_optimizer._run(short_content)
        assert "Error" in result or "too short" in result.lower()
    
    def test_keyword_placement_checks(self, good_content):
        """Test keyword placement analysis"""
        result = seo_optimizer._run(good_content, "Docker")
        assert "In Title:" in result
        assert "In First Paragraph:" in result
        assert "In Headers:" in result


class TestResearchTool:
    """Test suite for Research Tool"""
    
    def test_research_tool_initializes(self):
        """Test that research tool initializes"""
        assert research_tool is not None
        assert research_tool.name == "Free Research Tool"
    
    @pytest.mark.slow
    def test_research_tool_wikipedia(self):
        """Test Wikipedia search functionality"""
        result = research_tool._run("Python programming language", max_results=2)
        assert result is not None
        assert len(result) > 100
        assert "Python" in result or "programming" in result.lower()
    
    @pytest.mark.slow
    def test_research_tool_formatting(self):
        """Test result formatting"""
        result = research_tool._run("artificial intelligence", max_results=3)
        assert "Research Results" in result or "Result" in result
        assert len(result) > 50


class TestIntegration:
    """Integration tests for complete workflow"""
    
    @pytest.mark.slow
    @pytest.mark.integration
    def test_tool_combination(self):
        """Test using multiple tools together"""
        # Research
        research_result = research_tool._run("Docker containers", max_results=2)
        assert len(research_result) > 100
        
        # Create sample content
        content = """
# Introduction to Docker

Docker is a containerization platform. This guide explains Docker basics.

## What is Docker?

Docker containers package applications with their dependencies.
        """
        
        # Analyze SEO
        seo_result = seo_optimizer._run(content, "Docker")
        assert "SEO SCORE:" in seo_result
        
        # Analyze tone
        tone_result = tone_analyzer._run(content, "professional")
        assert "TONE ANALYSIS" in tone_result
    
    @pytest.mark.slow
    @pytest.mark.integration
    def test_full_agent_workflow(self):
        """Test complete agent workflow (if time permits)"""
        # This would test the full multi-agent workflow
        # Marked as slow since it involves actual content generation
        pass


# Pytest configuration
def pytest_configure(config):
    """Configure custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])