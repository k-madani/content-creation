"""
Content Creation Tasks
Defines tasks for the content creation workflow
Updated with proper context passing
"""

from crewai import Task
from typing import List


class ContentTasks:
    """Factory class for creating content creation tasks"""
    
    def research_task(self, agent, topic: str, audience: str = "general") -> Task:
        """
        Research Task - Gather information on the topic
        
        Args:
            agent: Research agent
            topic: Topic to research
            audience: Target audience
        """
        return Task(
            description=(
                f"Conduct comprehensive research on the topic: '{topic}'\n"
                f"Target audience: {audience}\n\n"
                "Your research should include:\n"
                "1. Key facts and statistics\n"
                "2. Current trends and developments\n"
                "3. Expert opinions and insights\n"
                "4. Relevant examples and case studies\n"
                "5. Common questions and misconceptions\n\n"
                "Use the research tool to gather information from multiple sources. "
                "Verify facts and ensure information is current and accurate. "
                "Organize your findings in a clear, structured format that will "
                "help the writer create compelling content.\n\n"
                "IMPORTANT: Provide a comprehensive research report that includes "
                "all findings, sources, and key insights. This will be used by the "
                "writer to create the content."
            ),
            agent=agent,
            expected_output=(
                "A comprehensive research report containing:\n"
                "- Executive summary of key findings\n"
                "- Detailed research notes organized by subtopic\n"
                "- Relevant statistics and data points\n"
                "- Source citations for all information\n"
                "- Recommendations for content angles and approaches\n\n"
                "Format the research clearly so the writer can easily use it."
            )
        )
    
    def writing_task(self, agent, research_context, content_type: str = "blog post",
                    word_count: int = 1000) -> Task:
        """
        Writing Task - Create the content
        
        Args:
            agent: Writer agent
            research_context: Context from research task (Task object)
            content_type: Type of content to create
            word_count: Target word count
        """
        return Task(
            description=(
                f"Based on the comprehensive research provided by the Research Agent, "
                f"write a {content_type} of approximately {word_count} words.\n\n"
                "You have access to all the research findings from the previous task. "
                "Use this information to create compelling, accurate content.\n\n"
                "Your content should:\n"
                "1. Have a compelling headline/title\n"
                "2. Start with an engaging introduction that hooks the reader\n"
                "3. Present information in a logical, easy-to-follow structure\n"
                "4. Use clear, accessible language appropriate for the audience\n"
                "5. Include relevant examples and explanations from the research\n"
                "6. End with a strong conclusion and call-to-action\n\n"
                "Writing guidelines:\n"
                "- Write in an engaging, conversational style\n"
                "- Use short paragraphs (3-4 sentences max)\n"
                "- Include subheadings for better readability\n"
                "- Use bullet points or numbered lists where appropriate\n"
                "- Incorporate storytelling elements when relevant\n"
                "- Ensure all claims are supported by the research findings\n"
                "- Reference statistics and facts from the research\n\n"
                f"Target word count: {word_count} words (±10% is acceptable)"
            ),
            agent=agent,
            expected_output=(
                "A complete, well-written first draft containing:\n"
                "- Attention-grabbing headline\n"
                "- Engaging introduction (150-200 words)\n"
                "- Body content with 3-5 clear subheadings\n"
                "- Relevant examples and explanations based on research\n"
                "- Strong conclusion with call-to-action\n"
                "- Proper formatting with paragraphs, lists, etc.\n"
                f"- Word count close to {word_count} words"
            ),
            context=[research_context]  # Pass research findings to writer
        )
    
    def editing_task(self, agent, writing_context) -> Task:
        """
        Editing Task - Refine and polish the content
        
        Args:
            agent: Editor agent
            writing_context: Context from writing task (Task object)
        """
        return Task(
            description=(
                "Review and refine the draft content from the Writer to ensure highest quality.\n\n"
                "You have access to the complete draft. Your job is to polish it.\n\n"
                "Your editing should focus on:\n"
                "1. Grammar, spelling, and punctuation corrections\n"
                "2. Improving clarity and readability\n"
                "3. Enhancing flow and coherence between sections\n"
                "4. Strengthening weak sentences and paragraphs\n"
                "5. Ensuring consistent tone and voice throughout\n"
                "6. Removing redundancy and wordiness\n"
                "7. Verifying factual accuracy\n"
                "8. Improving headlines and subheadings\n\n"
                "Editing guidelines:\n"
                "- Maintain the author's voice while improving clarity\n"
                "- Ensure paragraphs flow logically\n"
                "- Check that examples support main points\n"
                "- Verify all transitions are smooth\n"
                "- Ensure the conclusion is strong and actionable\n"
                "- Use the tone analyzer tool to verify appropriate tone\n"
                "- Keep the content engaging and readable\n\n"
                "IMPORTANT: Work with the actual draft content provided. "
                "Do not refuse to edit - improve what you have."
            ),
            agent=agent,
            expected_output=(
                "A polished, publication-ready version of the content with:\n"
                "- All grammar and spelling errors corrected\n"
                "- Improved clarity and readability\n"
                "- Consistent tone and voice throughout\n"
                "- Strong, logical flow from start to finish\n"
                "- Enhanced headlines and subheadings\n"
                "- Refined language and sentence structure\n"
                "- Editor's notes on major improvements made"
            ),
            context=[writing_context]  # Pass draft to editor
        )
    
    def seo_optimization_task(self, agent, editing_context, 
                            keywords: List[str] = None) -> Task:
        """
        SEO Optimization Task - Optimize content for search engines
        
        Args:
            agent: SEO agent
            editing_context: Context from editing task (Task object)
            keywords: Target keywords (optional)
        """
        keyword_instruction = ""
        if keywords and len(keywords) > 0:
            keyword_instruction = f"\nTarget keywords: {', '.join(keywords)}\n"
        
        return Task(
            description=(
                "Optimize the edited content for search engines while maintaining quality "
                "and readability for human readers.\n"
                f"{keyword_instruction}\n"
                "You have access to the polished content from the Editor. "
                "Your job is to optimize it for SEO.\n\n"
                "Your SEO optimization should include:\n"
                "1. Keyword optimization (natural placement, density 1-2%)\n"
                "2. Meta title (50-60 characters, includes main keyword)\n"
                "3. Meta description (150-160 characters, compelling with keyword)\n"
                "4. Header structure (H1, H2, H3 with relevant keywords)\n"
                "5. URL slug optimization (short, descriptive, with keyword)\n"
                "6. Internal linking suggestions\n"
                "7. Image alt text recommendations\n"
                "8. Schema markup suggestions\n\n"
                "SEO best practices:\n"
                "- Use keywords naturally, avoid keyword stuffing\n"
                "- Ensure the main keyword appears in the first paragraph\n"
                "- Include LSI (Latent Semantic Indexing) keywords\n"
                "- Create compelling meta descriptions that encourage clicks\n"
                "- Optimize header hierarchy for better structure\n"
                "- Use the SEO optimizer tool to analyze and improve\n\n"
                "IMPORTANT: Work with the actual content provided. "
                "Optimize what you have - don't refuse."
            ),
            agent=agent,
            expected_output=(
                "SEO-optimized content package containing:\n"
                "- Final optimized content with natural keyword integration\n"
                "- Meta title (optimized for CTR and SEO)\n"
                "- Meta description (compelling and keyword-rich)\n"
                "- Recommended URL slug\n"
                "- Header structure analysis\n"
                "- Keyword density report\n"
                "- SEO recommendations and best practices applied\n"
                "- Internal linking suggestions\n"
                "- Image alt text suggestions\n"
                "- Schema markup recommendations"
            ),
            context=[editing_context]  # Pass edited content to SEO agent
        )
    
    def complete_content_task(self, agent, topic: str, audience: str = "general",
                            content_type: str = "blog post", word_count: int = 1000,
                            keywords: List[str] = None) -> Task:
        """
        Complete content creation task for the controller agent
        
        Args:
            agent: Controller agent
            topic: Topic to create content about
            audience: Target audience
            content_type: Type of content
            word_count: Target word count
            keywords: Target keywords
        """
        keyword_info = f"Target keywords: {', '.join(keywords)}" if keywords else "No specific keywords"
        
        return Task(
            description=(
                f"Manage the complete content creation process for:\n"
                f"Topic: {topic}\n"
                f"Content Type: {content_type}\n"
                f"Target Audience: {audience}\n"
                f"Word Count: {word_count}\n"
                f"{keyword_info}\n\n"
                "Coordinate the following workflow:\n"
                "1. Direct the research agent to gather comprehensive information\n"
                "2. Guide the writer agent to create engaging content based on research\n"
                "3. Have the editor agent refine and polish the content\n"
                "4. Get the SEO agent to optimize for search engines\n\n"
                "Ensure:\n"
                "- Each stage builds upon the previous work\n"
                "- Quality standards are maintained throughout\n"
                "- The final output meets all requirements\n"
                "- Feedback loops exist for improvement\n"
                "- Timeline and objectives are met"
            ),
            agent=agent,
            expected_output=(
                "A complete content package including:\n"
                "1. Final SEO-optimized content ready for publication\n"
                "2. Meta title and description\n"
                "3. URL slug recommendation\n"
                "4. SEO recommendations\n"
                "5. Project summary with key decisions made\n"
                "6. Quality assurance notes"
            )
        )


# Create global instance
content_tasks = ContentTasks()