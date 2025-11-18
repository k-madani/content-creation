import os
from datetime import datetime
from dotenv import load_dotenv
from crewai import Crew, Process
from agents.content_agents import (
    create_research_agent,
    create_writer_agent,
    create_editor_agent,
    create_seo_agent
)
from tasks.content_tasks import (
    create_research_task,
    create_writing_task,
    create_editing_task,
    create_seo_task
)
from tools.tone_analyzer import ToneAnalyzerTool
from tools.seo_optimizer import SEOOptimizerTool
from utils.error_handler import retry_with_backoff, log_performance

# Load environment variables
load_dotenv()
os.environ["OPENAI_MODEL_NAME"] = "gpt-4o-mini"

@retry_with_backoff(max_retries=3)
@log_performance
def create_content(topic, tone_reference=None, target_keyword=None, enable_seo=True):
    """
    Main function to orchestrate content creation
    
    Args:
        topic: The topic to write about
        tone_reference: Optional text or URL to analyze for tone matching
        target_keyword: Optional keyword to optimize for
        enable_seo: Whether to run SEO analysis
        
    Returns:
        The final polished blog post with optional SEO analysis
    """
    
    print("\n" + "=" * 70)
    print(f"CONTENTCRAFT AI - CONTENT CREATION SYSTEM")
    print("=" * 70)
    print(f"\nTopic: {topic}")
    
    if target_keyword:
        print(f"Target Keyword: {target_keyword}")
    
    # Analyze tone if reference provided
    tone_guidelines = None
    if tone_reference:
        print(f"Tone Reference: {tone_reference[:100]}...")
        print("\nAnalyzing tone...")
        tone_analyzer = ToneAnalyzerTool()
        tone_guidelines = tone_analyzer.run(tone_reference)
        print("Tone analysis complete!")
    
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")
    
    # Create agents
    print("Initializing agents...")
    agents = [
        create_research_agent(),
        create_writer_agent(),
        create_editor_agent()
    ]
    
    agent_names = "Research, Writer, Editor"
    
    if enable_seo:
        agents.append(create_seo_agent())
        agent_names += ", SEO Specialist"
    
    print(f"Agents created: {agent_names}\n")
    
    # Create tasks
    print("Creating tasks...")
    tasks = [
        create_research_task(agents[0], topic)
    ]
    
    # Enhanced writing task with tone guidelines
    if tone_guidelines:
        tasks.append(create_writing_task_with_tone(agents[1], topic, tone_guidelines))
    else:
        tasks.append(create_writing_task(agents[1], topic))
    
    tasks.append(create_editing_task(agents[2]))
    
    if enable_seo:
        tasks.append(create_seo_task(agents[3], target_keyword))
    
    print(f"Tasks created: {len(tasks)} tasks\n")
    
    # Create crew with sequential process
    print("Assembling crew...\n")
    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
        verbose=True
    )
    
    # Execute the workflow
    print("=" * 70)
    print("STARTING CONTENT CREATION WORKFLOW")
    print("=" * 70 + "\n")
    
    result = crew.kickoff()
    
    print("\n" + "=" * 70)
    print("WORKFLOW COMPLETE")
    print("=" * 70 + "\n")
    
    # If SEO enabled, also run detailed SEO analysis on final content
    if enable_seo and not isinstance(result, str):
        result_str = str(result)
    else:
        result_str = result
    
    if enable_seo:
        print("\nRunning detailed SEO analysis...")
        seo_tool = SEOOptimizerTool()
        seo_report = seo_tool.run(result_str, target_keyword)
        
        # Append SEO report to output
        result_with_seo = f"{result_str}\n\n{'='*70}\nSEO ANALYSIS\n{'='*70}\n{seo_report}"
        return result_with_seo
    
    return result

def create_writing_task_with_tone(agent, topic, tone_guidelines):
    """Create writing task with specific tone guidelines"""
    from crewai import Task
    
    return Task(
        description=f'''Write a comprehensive blog post about: "{topic}"
        
        Use the research provided to write an informative and engaging article.
        
        IMPORTANT - TONE REQUIREMENTS:
        {tone_guidelines}
        
        Follow these tone guidelines precisely while writing.
        
        Requirements:
        - Length: 800-1000 words
        - Structure: 
          * Compelling introduction with hook
          * 3-5 main sections with descriptive headers
          * Practical examples throughout
          * Strong conclusion
        - Format: Use markdown with headers (##, ###)
        - Match the tone profile specified above
        
        Make it informative, practical, and match the specified tone exactly.''',
        expected_output='''A complete blog post in markdown format with:
        - Engaging title
        - Well-structured sections with headers
        - 800-1000 words
        - Practical examples
        - Clear explanations
        - Tone matching the specified guidelines''',
        agent=agent
    )

def save_output(content, topic):
    """Save the generated content to a file"""
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create filename from topic
    filename = topic.lower().replace(" ", "_")[:50]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"{output_dir}/{filename}_{timestamp}.md"
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(str(content))
    
    return output_file

def main():
    """Main function with interactive input"""
    print("\n" + "=" * 70)
    print("CONTENTCRAFT AI - Multi-Agent Content Creation System")
    print("=" * 70)
    print("\nModel: gpt-4o-mini")
    print("Agents: Research, Writer, Editor, SEO Specialist")
    print("Custom Tools: Tone Analyzer, SEO Optimizer")
    print("\n" + "=" * 70 + "\n")
    
    # Get topic from user
    topic = input("Enter the topic for your blog post: ").strip()
    
    if not topic:
        print("Error: Topic cannot be empty")
        return
    
    # Ask for target keyword
    print("\nEnter a target keyword for SEO optimization (optional):")
    target_keyword = input("Target keyword (or press Enter to skip): ").strip()
    if not target_keyword:
        target_keyword = None
    
    # Ask if user wants tone matching
    print("\nDo you want to match a specific writing tone?")
    print("You can provide:")
    print("  1. A URL to analyze")
    print("  2. Sample text (paste a paragraph)")
    print("  3. Just press Enter to skip")
    
    tone_ref = input("\nTone reference (or Enter to skip): ").strip()
    
    if not tone_ref:
        tone_ref = None
    
    # Summary
    print(f"\n{'='*70}")
    print("GENERATION SETTINGS:")
    print(f"{'='*70}")
    print(f"Topic: {topic}")
    print(f"Target Keyword: {target_keyword if target_keyword else 'None'}")
    print(f"Tone Matching: {'Enabled' if tone_ref else 'Disabled'}")
    print(f"SEO Analysis: Enabled")
    print(f"{'='*70}\n")
    
    print("Estimated time: 8-12 minutes")
    print("Starting content generation...\n")
    
    # Generate content
    result = create_content(topic, tone_ref, target_keyword, enable_seo=True)
    
    # Save output
    output_file = save_output(result, topic)
    
    print("\n" + "=" * 70)
    print("CONTENT CREATION COMPLETE")
    print("=" * 70)
    print(f"\nOutput saved to: {output_file}")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

if __name__ == "__main__":
    main()