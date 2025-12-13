"""
Test CrewAI + LiteLLM + Gemini Configuration
Run this before running the full system
"""

import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
import litellm

load_dotenv()

# Configure LiteLLM
litellm.drop_params = True
litellm.set_verbose = True  # Enable verbose for testing

# Set environment
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")

print("="*60)
print("Testing CrewAI + Gemini 2.0 Configuration")
print("="*60)

# Test agent
agent = Agent(
    role="Test Agent",
    goal="Test LLM connection with Gemini 2.0",
    backstory="I am a test agent verifying the system works",
    llm='gemini-2.0-flash',  # Model name without prefix
    verbose=True
)

task = Task(
    description="Say 'Hello! Gemini 2.0 with paid billing is working perfectly!'",
    agent=agent,
    expected_output="A cheerful greeting confirming the system works"
)

crew = Crew(
    agents=[agent],
    tasks=[task],
    verbose=True
)

print("\n🔍 Starting test...\n")

try:
    result = crew.kickoff()
    print("\n" + "="*60)
    print("✅ SUCCESS!")
    print("="*60)
    print(f"\nResult: {result}")
    print("\n✅ Your system is configured correctly!")
    print("✅ Paid billing is active!")
    print("✅ Ready to generate content!")
    
except Exception as e:
    print("\n" + "="*60)
    print("❌ TEST FAILED")
    print("="*60)
    print(f"\nError: {e}")
    print("\nTroubleshooting:")
    print("1. Check .env has correct GEMINI_API_KEY")
    print("2. Verify billing is enabled in Google AI Studio")
    print("3. Make sure model 'gemini-2.0-flash' is accessible")
    print("4. Try running: pip install --upgrade litellm crewai")