from crewai import Task

def create_research_task(agent, topic):
    """Task for researching a topic thoroughly"""
    return Task(
        description=f'''Research the topic: "{topic}"
        
        Your research must include:
        1. Clear definition and key concepts
        2. Current trends and recent developments
        3. Practical applications and real-world examples
        4. Common challenges or misconceptions
        5. Expert opinions, statistics, or data points
        6. Credible sources (prioritize official docs, reputable tech sites)
        
        Focus on information that would be valuable for a blog post.
        Provide a comprehensive summary with all key points organized clearly.''',
        expected_output='''A detailed research report containing:
        - Key definitions and concepts
        - Important statistics and data
        - Practical examples
        - Current trends
        - Credible source references''',
        agent=agent
    )

def create_writing_task(agent, topic):
    """Task for writing the blog post"""
    return Task(
        description=f'''Write a comprehensive blog post about: "{topic}"
        
        Use the research provided to write an informative and engaging article.
        
        Requirements:
        - Length: 800-1000 words
        - Style: Clear, engaging, accessible to general technical audience
        - Structure: 
          * Compelling introduction with hook
          * 3-5 main sections with descriptive headers
          * Practical examples throughout
          * Strong conclusion
        - Format: Use markdown with headers (##, ###)
        - Tone: Professional but conversational
        - Explain technical terms when first used
        
        Make it informative, practical, and enjoyable to read.''',
        expected_output='''A complete blog post in markdown format with:
        - Engaging title
        - Well-structured sections with headers
        - 800-1000 words
        - Practical examples
        - Clear explanations''',
        agent=agent
    )

def create_editing_task(agent):
    """Task for editing and polishing the content"""
    return Task(
        description='''Review and improve the blog post provided by the writer.
        
        Your editing should focus on:
        
        1. Grammar and spelling
           - Fix any errors
           - Ensure proper punctuation
        
        2. Clarity and readability
           - Simplify complex sentences
           - Improve word choice
           - Ensure concepts are clearly explained
        
        3. Structure and flow
           - Check logical progression
           - Improve transitions between sections
           - Ensure coherent narrative
        
        4. Engagement
           - Strengthen weak sections
           - Add impact to key points
           - Ensure introduction hooks readers
        
        5. Consistency
           - Maintain consistent tone
           - Ensure formatting is uniform
           - Check header hierarchy
        
        Make the content publication-ready and professional.''',
        expected_output='''A polished, publication-ready blog post with:
        - All grammar and spelling errors fixed
        - Improved clarity and flow
        - Enhanced engagement
        - Consistent professional tone
        - Ready for immediate publication''',
        agent=agent
    )