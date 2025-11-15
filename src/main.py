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

# Load environment variables
load_dotenv()
os.environ["OPENAI_MODEL_NAME"] = "gpt-4o-mini"

def create_content(topic):
    """
    Main function to orchestrate content creation
    
    Args:
        topic: The topic to write about
        
    Returns:
        The final polished blog post
    """
    
    print("\n" + "=" * 70)
    print(f"CONTENT CREATION SYSTEM")
    print("=" * 70)
    print(f"\nTopic: {topic}")
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
    print("\n" + "=" * 70 + "\n")
    
    # Get topic from user
    topic = input("Enter the topic for your blog post: ").strip()
    
    if not topic:
        print("Error: Topic cannot be empty")
        return
    
    print(f"\nGenerating content about: '{topic}'")
    print("This will take 5-10 minutes...\n")
    
    # Generate content
    result = create_content(topic)
    
    # Save output
    output_file = save_output(result, topic)
    
    print("\n" + "=" * 70)
    print("CONTENT CREATION COMPLETE")
    print("=" * 70)
    print(f"\nOutput saved to: {output_file}")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

if __name__ == "__main__":
    main()