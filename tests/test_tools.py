import pytest
from src.tools.tone_analyzer import ToneAnalyzerTool
from src.tools.seo_optimizer import SEOOptimizerTool


class TestToneAnalyzer:
    """Test suite for Tone Analyzer tool"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.analyzer = ToneAnalyzerTool()
        
        self.casual_text = """
        Hey! So I've been using Docker for a while now and it's pretty awesome. 
        You should definitely try it out. It'll make your life so much easier!
        """
        
        self.formal_text = """
        Docker containerization represents a significant advancement in software deployment.
        Organizations implementing this technology report substantial improvements in efficiency.
        The platform demonstrates considerable potential for enterprise applications.
        """
    
    def test_analyzer_initializes(self):
        """Test that analyzer initializes correctly"""
        assert self.analyzer is not None
        assert self.analyzer.name == "Tone Analyzer"
    
    def test_casual_tone_detection(self):
        """Test detection of casual tone"""
        result = self.analyzer.run(self.casual_text)
        assert "Casual" in result or "Conversational" in result
    
    def test_formal_tone_detection(self):
        """Test detection of formal tone"""
        result = self.analyzer.run(self.formal_text)
        assert "Formal" in result or "Professional" in result
    
    def test_short_text_error(self):
        """Test error handling for short text"""
        result = self.analyzer.run("Too short")
        assert "Error" in result or "too short" in result.lower()
    
    def test_metrics_extraction(self):
        """Test that metrics are calculated"""
        result = self.analyzer.run(self.casual_text)
        assert "Flesch Reading Ease" in result
        assert "Grade Level" in result
        assert "Formality" in result


class TestSEOOptimizer:
    """Test suite for SEO Optimizer tool"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.optimizer = SEOOptimizerTool()
        
        self.good_content = """
# Docker Containerization Guide

Docker is a powerful platform for containerization. This guide covers Docker basics.

## What is Docker?

Docker allows you to package applications with dependencies. It's used by many developers.

## Benefits of Docker

Docker provides portability and consistency. Teams use Docker for deployment.

## Getting Started

To start with Docker, install it first. Then create your first container.
        """
    
    def test_optimizer_initializes(self):
        """Test that optimizer initializes correctly"""
        assert self.optimizer is not None
        assert self.optimizer.name == "SEO Optimizer"
    
    def test_seo_score_calculation(self):
        """Test that SEO score is calculated"""
        result = self.optimizer.run(self.good_content, "Docker")
        assert "SEO SCORE:" in result
        assert "/100" in result
    
    def test_keyword_analysis(self):
        """Test keyword analysis with target keyword"""
        result = self.optimizer.run(self.good_content, "Docker")
        assert "KEYWORD ANALYSIS" in result
        assert "Docker" in result
    
    def test_readability_metrics(self):
        """Test readability calculation"""
        result = self.optimizer.run(self.good_content)
        assert "Flesch Reading Ease" in result
        assert "Grade Level" in result
    
    def test_structure_analysis(self):
        """Test content structure analysis"""
        result = self.optimizer.run(self.good_content)
        assert "H1 Headers" in result
        assert "H2 Headers" in result
    
    def test_recommendations_generated(self):
        """Test that recommendations are provided"""
        result = self.optimizer.run(self.good_content)
        assert "RECOMMENDATIONS" in result


class TestIntegration:
    """Integration tests for complete workflow"""
    
    @pytest.mark.slow
    def test_full_workflow(self):
        """Test complete content generation workflow"""
        # This would test the full agent workflow
        # Marked as slow since it calls APIs
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])