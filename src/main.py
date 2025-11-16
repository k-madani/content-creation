import os
from datetime import datetime
from dotenv import load_dotenv
from crewai import Crew, Process
from agents.content_agents import (
    create_research_agent,
    create_writer_agent,
    create_editor_agent
)
from tasks.content_tasks import (
    create_research_task,
    create_writing_task,
    create_editing_task
)
from tools.tone_analyzer import ToneAnalyzerTool

# Load environment variables
load_dotenv()
os.environ["OPENAI_MODEL_NAME"] = "gpt-4o-mini"

def create_content(topic, tone_reference=None):
    """
    Main function to orchestrate content creation
    
    Args:
        topic: The topic to write about
        tone_reference: Optional text or URL to analyze for tone matching
        
    Returns:
        The final polished blog post
    """
    
    print("\n" + "=" * 70)
    print(f"CONTENT CREATION SYSTEM")
    print("=" * 70)
    print(f"\nTopic: {topic}")
    
    # Analyze tone if reference provided
    tone_guidelines = None
    if tone_reference:
        print(f"Tone Reference: {tone_reference[:100]}...")
        print("\nAnalyzing tone...")
        tone_analyzer = ToneAnalyzerTool()
        tone_guidelines = tone_analyzer.run(tone_reference)
        print("Tone analysis complete!")
    
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "=" * 70 + "\n")
    
    # Create agents
    print("Initializing agents...")
    research_agent = create_research_agent()
    writer_agent = create_writer_agent()
    editor_agent = create_editor_agent()
    print("Agents created: Research, Writer, Editor\n")
    
    # Create tasks
    print("Creating tasks...")
    research_task = create_research_task(research_agent, topic)
    
    # Enhanced writing task with tone guidelines
    if tone_guidelines:
        writing_task = create_writing_task_with_tone(writer_agent, topic, tone_guidelines)
    else:
        writing_task = create_writing_task(writer_agent, topic)
    
    editing_task = create_editing_task(editor_agent)
    print("Tasks created: Research, Writing, Editing\n")
    
    # Create crew with sequential process
    print("Assembling crew...\n")
    crew = Crew(
        agents=[research_agent, writer_agent, editor_agent],
        tasks=[research_task, writing_task, editing_task],
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
    print("Agents: Research, Writer, Editor")
    print("Custom Tool: Tone Analyzer")
    print("\n" + "=" * 70 + "\n")
    
    # Get topic from user
    topic = input("Enter the topic for your blog post: ").strip()
    
    if not topic:
        print("Error: Topic cannot be empty")
        return
    
    # Ask if user wants tone matching
    print("\nDo you want to match a specific writing tone?")
    print("You can provide:")
    print("  1. A URL to analyze (e.g., https://example.com/article)")
    print("  2. Sample text (paste a paragraph)")
    print("  3. Just press Enter to skip tone matching")
    
    tone_ref = input("\nTone reference (URL or text, or Enter to skip): ").strip()
    
    if tone_ref:
        print(f"\nGenerating content about: '{topic}'")
        print("With tone matching enabled")
    else:
        print(f"\nGenerating content about: '{topic}'")
        tone_ref = None
    
    print("This will take 5-10 minutes...\n")
    
    # Generate content
    result = create_content(topic, tone_ref)
    
    # Save output
    output_file = save_output(result, topic)
    
    print("\n" + "=" * 70)
    print("CONTENT CREATION COMPLETE")
    print("=" * 70)
    print(f"\nOutput saved to: {output_file}")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

if __name__ == "__main__":
    main()