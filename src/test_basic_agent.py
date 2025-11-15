import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool

# Load environment variables
load_dotenv()

# Set model to gpt-4o-mini
os.environ["OPENAI_MODEL_NAME"] = "gpt-4o-mini"

# Verify API keys
print("Checking API keys...")
openai_key = os.getenv('OPENAI_API_KEY')
serper_key = os.getenv('SERPER_API_KEY')

if not openai_key:
    print("ERROR: OPENAI_API_KEY not found")
    exit()
if not serper_key:
    print("ERROR: SERPER_API_KEY not found")
    exit()

print("API keys loaded successfully")
print("Using model: gpt-4o-mini\n")

# Initialize search tool
print("Initializing web search tool...")
search_tool = SerperDevTool()

# Create researcher agent
print("Creating research agent...\n")
researcher = Agent(
    role='Research Specialist',
    goal='Find accurate information about any topic',
    backstory='Expert researcher who verifies information from multiple sources',
    tools=[search_tool],
    verbose=True
)

# Create task
research_task = Task(
    description='Research: What is CrewAI and how does it work? Provide a beginner-friendly explanation.',
    expected_output='A 150-word summary explaining CrewAI',
    agent=researcher
)

# Create and run crew
print("Starting research agent...")
print("=" * 70 + "\n")

crew = Crew(
    agents=[researcher],
    tasks=[research_task],
    verbose=True
)

result = crew.kickoff()

print("\n" + "=" * 70)
print("FINAL RESULT:")
print("=" * 70)
print(result)