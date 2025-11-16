def create_tone_analysis_task(agent, tone_reference):
    """Task for analyzing desired tone from reference"""
    return Task(
        description=f'''Analyze the writing tone and style from this reference: {tone_reference}
        
        If it's a URL, fetch and analyze the content.
        If it's descriptive text, analyze the style characteristics.
        
        Provide detailed style guidelines including:
        - Formality level
        - Reading complexity
        - Sentence structure preferences
        - Engagement approach
        - Specific writing instructions
        
        These guidelines will be used by the writer to match the tone.''',
        expected_output='''Comprehensive tone analysis report with:
        - Detailed style metrics
        - Clear formality level
        - Reading level assessment
        - Specific writing guidelines
        - Recommended approach for content creation''',
        agent=agent
    )