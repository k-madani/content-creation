"""
Content Quality Scoring System
Evaluates content across multiple dimensions
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import re

console = Console()


class ContentQualityScorer:
    """Evaluate content quality across multiple dimensions"""
    
    def __init__(self):
        self.scores = {}
    
    def evaluate_content(self, content: str, target_word_count: int = 1200, 
                        keywords: list = None) -> dict:
        """
        Comprehensive quality evaluation
        
        Args:
            content: Generated content to evaluate
            target_word_count: Target word count
            keywords: Target keywords for SEO
            
        Returns:
            Dictionary with scores and analysis
        """
        
        # 1. Structure Score (25 points)
        structure_score = self._evaluate_structure(content)
        
        # 2. Completeness Score (25 points)
        completeness_score = self._evaluate_completeness(content, target_word_count)
        
        # 3. Readability Score (25 points)
        readability_score = self._evaluate_readability(content)
        
        # 4. SEO Score (25 points)
        seo_score = self._evaluate_seo(content, keywords)
        
        # Calculate overall score
        overall_score = (
            structure_score * 0.25 +
            completeness_score * 0.25 +
            readability_score * 0.25 +
            seo_score * 0.25
        )
        
        # Determine grade
        grade = self._get_grade(overall_score)
        
        return {
            'overall_score': round(overall_score, 1),
            'grade': grade,
            'structure_score': structure_score,
            'completeness_score': completeness_score,
            'readability_score': readability_score,
            'seo_score': seo_score,
            'details': {
                'word_count': len(content.split()),
                'target_word_count': target_word_count,
                'has_title': content.strip().startswith('#'),
                'header_count': content.count('##'),
                'has_conclusion': self._has_conclusion(content)
            }
        }
    
    def _evaluate_structure(self, content: str) -> int:
        """Evaluate content structure (0-100)"""
        
        score = 0
        
        # Has H1 title (20 points)
        if content.strip().startswith('#'):
            score += 20
        
        # Has H2 subheaders (30 points)
        h2_count = content.count('##')
        if h2_count >= 5:
            score += 30
        elif h2_count >= 3:
            score += 25
        elif h2_count >= 1:
            score += 15
        
        # Has lists or formatting (20 points)
        has_lists = bool(re.search(r'^\s*[-*]\s', content, re.MULTILINE))
        has_numbered = bool(re.search(r'^\s*\d+\.\s', content, re.MULTILINE))
        if has_lists or has_numbered:
            score += 20
        
        # Has conclusion (15 points)
        if self._has_conclusion(content):
            score += 15
        
        # Logical paragraphs (15 points)
        paragraphs = content.split('\n\n')
        if len(paragraphs) >= 5:
            score += 15
        elif len(paragraphs) >= 3:
            score += 10
        
        return min(score, 100)
    
    def _evaluate_completeness(self, content: str, target: int) -> int:
        """Evaluate completeness (0-100)"""
        
        word_count = len(content.split())
        
        # Word count accuracy (50 points)
        percentage = (word_count / target) if target > 0 else 0
        if 0.85 <= percentage <= 1.15:  # Within ±15%
            word_score = 50
        elif 0.70 <= percentage <= 1.30:  # Within ±30%
            word_score = 35
        else:
            word_score = 20
        
        # Has introduction (25 points)
        first_paragraph = content.split('\n\n')[1] if '\n\n' in content else ""
        has_intro = len(first_paragraph.split()) > 50
        intro_score = 25 if has_intro else 10
        
        # Has conclusion (25 points)
        conclusion_score = 25 if self._has_conclusion(content) else 10
        
        return word_score + intro_score + conclusion_score
    
    def _evaluate_readability(self, content: str) -> int:
        """Evaluate readability (0-100)"""
        
        score = 0
        
        # Average sentence length
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if sentences:
            words = content.split()
            avg_sentence_length = len(words) / len(sentences)
            
            # Optimal: 15-25 words per sentence (40 points)
            if 15 <= avg_sentence_length <= 25:
                score += 40
            elif 10 <= avg_sentence_length <= 30:
                score += 30
            else:
                score += 20
        
        # Paragraph length (30 points)
        paragraphs = [p for p in content.split('\n\n') if p.strip() and not p.strip().startswith('#')]
        if paragraphs:
            avg_para_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs)
            
            # Optimal: 50-150 words per paragraph
            if 50 <= avg_para_length <= 150:
                score += 30
            elif 30 <= avg_para_length <= 200:
                score += 20
            else:
                score += 10
        
        # Uses formatting (30 points)
        has_bold = '**' in content or '<strong>' in content
        has_lists = bool(re.search(r'^\s*[-*]\s', content, re.MULTILINE))
        has_headers = '##' in content
        
        formatting_score = sum([
            10 if has_bold else 0,
            10 if has_lists else 0,
            10 if has_headers else 0
        ])
        score += formatting_score
        
        return min(score, 100)
    
    def _evaluate_seo(self, content: str, keywords: list = None) -> int:
        """Evaluate SEO optimization (0-100)"""
        
        score = 0
        content_lower = content.lower()
        
        # Has meta information in content (20 points)
        has_meta_title = 'meta title' in content_lower or '**meta title' in content_lower
        has_meta_desc = 'meta description' in content_lower
        if has_meta_title:
            score += 10
        if has_meta_desc:
            score += 10
        
        # Keywords present (30 points)
        if keywords:
            keywords_found = sum(1 for kw in keywords if kw.lower() in content_lower)
            keyword_score = (keywords_found / len(keywords)) * 30
            score += keyword_score
        else:
            score += 20  # Partial credit if no keywords specified
        
        # Header optimization (25 points)
        headers = re.findall(r'^#{1,3}\s+(.+)$', content, re.MULTILINE)
        if len(headers) >= 4:
            score += 25
        elif len(headers) >= 2:
            score += 15
        
        # Has SEO elements (25 points)
        has_url_slug = 'url slug' in content_lower or 'slug:' in content_lower
        has_alt_text = 'alt text' in content_lower or 'alt=' in content_lower
        has_internal_links = '[' in content and '](' in content
        
        seo_elements = sum([
            10 if has_url_slug else 0,
            8 if has_alt_text else 0,
            7 if has_internal_links else 0
        ])
        score += seo_elements
        
        return min(score, 100)
    
    def _has_conclusion(self, content: str) -> bool:
        """Check if content has a conclusion section"""
        
        conclusion_keywords = ['conclusion', 'final thoughts', 'in summary', 
                              'to sum up', 'in closing', 'takeaway']
        
        # Check last 30% of content
        content_lower = content.lower()
        last_section = content_lower[-len(content_lower)//3:]
        
        return any(keyword in last_section for keyword in conclusion_keywords)
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        
        if score >= 95:
            return "A+ 🏆"
        elif score >= 90:
            return "A ⭐"
        elif score >= 85:
            return "A- ✨"
        elif score >= 80:
            return "B+ 💫"
        elif score >= 75:
            return "B ✓"
        elif score >= 70:
            return "B- ≈"
        else:
            return "C ⚠️"
    
    def display_quality_report(self, quality_data: dict):
        """Display quality report in a nice format"""
        
        console.print("\n")
        console.print("="*60, style="bold cyan")
        console.print("📊 CONTENT QUALITY ANALYSIS", style="bold cyan")
        console.print("="*60 + "\n", style="bold cyan")
        
        # Overall score panel
        overall_panel = Panel(
            f"[bold white]{quality_data['overall_score']}/100[/bold white]\n"
            f"[bold yellow]Grade: {quality_data['grade']}[/bold yellow]",
            title="[bold cyan]Overall Quality Score[/bold cyan]",
            border_style="cyan"
        )
        console.print(overall_panel)
        
        # Dimension scores table
        scores_table = Table(title="[bold]Score Breakdown by Dimension[/bold]", show_header=True)
        scores_table.add_column("Dimension", style="cyan", width=20)
        scores_table.add_column("Score", justify="right", style="yellow")
        scores_table.add_column("Rating", justify="center")
        
        dimensions = [
            ("📐 Structure", quality_data['structure_score']),
            ("📏 Completeness", quality_data['completeness_score']),
            ("📖 Readability", quality_data['readability_score']),
            ("🎯 SEO", quality_data['seo_score'])
        ]
        
        for name, score in dimensions:
            rating = self._get_rating(score)
            scores_table.add_row(name, f"{score}/100", rating)
        
        console.print("\n")
        console.print(scores_table)
        
        # Content details
        details = quality_data['details']
        
        console.print("\n[bold cyan]📋 Content Details:[/bold cyan]")
        details_table = Table(show_header=False, box=None)
        details_table.add_column("Metric", style="dim")
        details_table.add_column("Value", style="white")
        
        word_diff = details['word_count'] - details['target_word_count']
        word_status = "✅" if abs(word_diff) <= details['target_word_count'] * 0.15 else "⚠️"
        
        details_table.add_row("Word Count", f"{word_status} {details['word_count']} (target: {details['target_word_count']})")
        details_table.add_row("Has Title", "✅ Yes" if details['has_title'] else "❌ No")
        details_table.add_row("Subheaders", f"✅ {details['header_count']}" if details['header_count'] >= 3 else f"⚠️ {details['header_count']}")
        details_table.add_row("Has Conclusion", "✅ Yes" if details['has_conclusion'] else "⚠️ No")
        
        console.print(details_table)
        
        # Recommendations
        console.print("\n[bold cyan]💡 Recommendations:[/bold cyan]")
        recommendations = self._generate_recommendations(quality_data)
        
        for i, rec in enumerate(recommendations, 1):
            console.print(f"  {i}. {rec}")
        
        console.print("\n" + "="*60 + "\n")
    
    def _get_rating(self, score: int) -> str:
        """Get emoji rating for score"""
        
        if score >= 90:
            return "🟢 Excellent"
        elif score >= 80:
            return "🟡 Very Good"
        elif score >= 70:
            return "🟠 Good"
        elif score >= 60:
            return "🔴 Fair"
        else:
            return "⚫ Needs Work"
    
    def _generate_recommendations(self, quality_data: dict) -> list:
        """Generate improvement recommendations"""
        
        recommendations = []
        
        # Structure recommendations
        if quality_data['structure_score'] < 80:
            if not quality_data['details']['has_title']:
                recommendations.append("Add a clear H1 title at the beginning")
            if quality_data['details']['header_count'] < 3:
                recommendations.append("Add more H2 subheaders (aim for 3-5)")
            if not quality_data['details']['has_conclusion']:
                recommendations.append("Add a strong conclusion section")
        
        # Completeness recommendations
        if quality_data['completeness_score'] < 80:
            word_diff = quality_data['details']['word_count'] - quality_data['details']['target_word_count']
            if abs(word_diff) > quality_data['details']['target_word_count'] * 0.15:
                if word_diff < 0:
                    recommendations.append(f"Content is {abs(word_diff)} words short - expand key sections")
                else:
                    recommendations.append(f"Content is {word_diff} words over - consider condensing")
        
        # Readability recommendations
        if quality_data['readability_score'] < 80:
            recommendations.append("Improve readability: use shorter sentences and more formatting")
        
        # SEO recommendations
        if quality_data['seo_score'] < 80:
            recommendations.append("Enhance SEO: ensure meta tags and keyword optimization")
        
        # Overall recommendations
        if quality_data['overall_score'] >= 90:
            recommendations.append("🎉 Excellent quality! Ready for publication")
        elif quality_data['overall_score'] >= 80:
            recommendations.append("✅ Good quality! Minor improvements suggested")
        elif quality_data['overall_score'] >= 70:
            recommendations.append("⚠️ Acceptable quality. Consider addressing issues above")
        else:
            recommendations.append("⚠️ Needs significant improvement. Consider regenerating")
        
        return recommendations if recommendations else ["✅ Content meets all quality standards!"]


# Create singleton instance
quality_scorer = ContentQualityScorer()