"""
Content Creation Agentic System
Main application entry point
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from crewai import Crew, Process
from dotenv import load_dotenv

# Import agents and tasks
from agents.content_agents import content_agents
from tasks.content_tasks import content_tasks

# Import tools
from tools.research_tool import research_tool
from tools.seo_optimizer import seo_optimizer
from tools.tone_analyzer import tone_analyzer

# Load environment variables
load_dotenv()

def create_content_crew(topic: str, audience: str = "general", 
                       content_type: str = "blog post", word_count: int = 1000,
                       keywords: list = None):
    """
    Create and configure the content creation crew
    
    Args:
        topic: Topic to create content about
        audience: Target audience
        content_type: Type of content (blog post, article, etc.)
        word_count: Target word count
        keywords: List of target keywords for SEO
    
    Returns:
        Configured Crew instance
    """
    
    print("\n" + "="*60)
    print("🚀 CONTENT CREATION AGENTIC SYSTEM")
    print("="*60)
    print(f"📝 Topic: {topic}")
    print(f"👥 Audience: {audience}")
    print(f"📄 Content Type: {content_type}")
    print(f"🔢 Word Count: {word_count}")
    if keywords:
        print(f"🔑 Keywords: {', '.join(keywords)}")
    print("="*60 + "\n")
    
    # Create agents with appropriate tools
    research_agent = content_agents.research_agent([research_tool])
    writer_agent = content_agents.writer_agent([tone_analyzer])
    editor_agent = content_agents.editor_agent([tone_analyzer])
    seo_agent = content_agents.seo_agent([seo_optimizer, tone_analyzer])
    
    # Create tasks
    research_task = content_tasks.research_task(research_agent, topic, audience)
    writing_task = content_tasks.writing_task(writer_agent, research_task, content_type, word_count)
    editing_task = content_tasks.editing_task(editor_agent, writing_task)
    seo_task = content_tasks.seo_optimization_task(seo_agent, editing_task, keywords)
    
    # Create crew
    crew = Crew(
        agents=[research_agent, writer_agent, editor_agent, seo_agent],
        tasks=[research_task, writing_task, editing_task, seo_task],
        process=Process.sequential,
        verbose=True
    )
    
    return crew

def create_content_with_controller(topic: str, audience: str = "general",
                                  content_type: str = "blog post", word_count: int = 1000,
                                  keywords: list = None):
    """
    Create content using the controller agent pattern
    
    Args:
        topic: Topic to create content about
        audience: Target audience
        content_type: Type of content
        word_count: Target word count
        keywords: Target keywords
    
    Returns:
        Configured Crew instance with controller
    """
    
    print("\n" + "="*60)
    print("🎯 CONTENT CREATION SYSTEM (CONTROLLER MODE)")
    print("="*60)
    print(f"📝 Topic: {topic}")
    print(f"👥 Audience: {audience}")
    print(f"📄 Content Type: {content_type}")
    print(f"🔢 Word Count: {word_count}")
    if keywords:
        print(f"🔑 Keywords: {', '.join(keywords)}")
    print("="*60 + "\n")
    
    # Create specialized agents
    research_agent = content_agents.research_agent([research_tool])
    writer_agent = content_agents.writer_agent([tone_analyzer])
    editor_agent = content_agents.editor_agent([tone_analyzer])
    seo_agent = content_agents.seo_agent([seo_optimizer, tone_analyzer])
    
    # Create controller agent
    controller = content_agents.controller_agent()
    
    # Create main task for controller
    main_task = content_tasks.complete_content_task(
        controller, topic, audience, content_type, word_count, keywords
    )
    
    # Create crew with hierarchical process
    crew = Crew(
        agents=[controller, research_agent, writer_agent, editor_agent, seo_agent],
        tasks=[main_task],
        process=Process.hierarchical,
        manager_llm=content_agents.llm,
        verbose=True
    )
    
    return crew

def main():
    """Main entry point"""
    
    # Example 1: Simple sequential workflow
    print("\n🔷 Example 1: Sequential Workflow\n")
    
    crew1 = create_content_crew(
        topic="The Future of Artificial Intelligence in Healthcare",
        audience="healthcare professionals and tech enthusiasts",
        content_type="blog post",
        word_count=1500,
        keywords=["AI in healthcare", "medical AI", "healthcare technology"]
    )
    
    try:
        result1 = crew1.kickoff()
        print("\n" + "="*60)
        print("✅ CONTENT CREATED SUCCESSFULLY (Sequential)")
        print("="*60)
        print("\n📄 Final Content:\n")
        print(result1)
        
        # Save output
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / "sequential_output.md", "w", encoding="utf-8") as f:
            f.write(str(result1))
        
        print(f"\n💾 Content saved to: {output_dir / 'sequential_output.md'}")
        
    except Exception as e:
        print(f"\n❌ Error in sequential workflow: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80 + "\n")
    
    # Example 2: Controller-based hierarchical workflow
    print("\n🔶 Example 2: Hierarchical Workflow (Controller-based)\n")
    
    crew2 = create_content_with_controller(
        topic="Climate Change Solutions for Sustainable Living",
        audience="environmentally conscious individuals",
        content_type="article",
        word_count=1200,
        keywords=["climate change", "sustainability", "green living"]
    )
    
    try:
        result2 = crew2.kickoff()
        print("\n" + "="*60)
        print("✅ CONTENT CREATED SUCCESSFULLY (Hierarchical)")
        print("="*60)
        print("\n📄 Final Content:\n")
        print(result2)
        
        # Save output
        with open(output_dir / "hierarchical_output.md", "w", encoding="utf-8") as f:
            f.write(str(result2))
        
        print(f"\n💾 Content saved to: {output_dir / 'hierarchical_output.md'}")
        
    except Exception as e:
        print(f"\n❌ Error in hierarchical workflow: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("✨ Content creation process completed!")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()