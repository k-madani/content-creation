"""
Basic Agent Test - Updated for Free LLM Stack
Tests single agent with free research tools
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

# Import free research tool
from tools.research_tool import research_tool

# Load environment variables
load_dotenv()

def test_with_gemini():
    """Test agent with Gemini"""
    print("\n" + "="*70)
    print("TEST 1: AGENT WITH GEMINI")
    print("="*70)
    
    # Check Gemini API key
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        print("❌ GEMINI_API_KEY not found in .env")
        return False
    
    print("✅ Gemini API key found")
    
    # Initialize Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=gemini_key,
        temperature=0.7
    )
    
    # Create researcher agent
    print("Creating research agent with Gemini...")
    researcher = Agent(
        role='Research Specialist',
        goal='Find accurate information about any topic using free research tools',
        backstory='Expert researcher who gathers information from Wikipedia and web sources',
        tools=[research_tool],
        llm=llm,
        verbose=True
    )
    
    # Create task
    research_task = Task(
        description='Research: What is CrewAI and how does it work? Provide a beginner-friendly explanation.',
        expected_output='A 150-200 word summary explaining CrewAI and its key features',
        agent=researcher
    )
    
    # Create and run crew
    print("\n🚀 Starting research with Gemini...\n")
    
    crew = Crew(
        agents=[researcher],
        tasks=[research_task],
        verbose=True
    )
    
    try:
        result = crew.kickoff()
        
        print("\n" + "="*70)
        print("✅ GEMINI TEST - SUCCESS")
        print("="*70)
        print(result)
        print("="*70)
        return True
        
    except Exception as e:
        print("\n" + "="*70)
        print("❌ GEMINI TEST - FAILED")
        print("="*70)
        print(f"Error: {str(e)}")
        print("="*70)
        return False

def test_with_groq():
    """Test agent with Groq"""
    print("\n" + "="*70)
    print("TEST 2: AGENT WITH GROQ")
    print("="*70)
    
    # Check Groq API key
    groq_key = os.getenv('GROQ_API_KEY')
    if not groq_key:
        print("❌ GROQ_API_KEY not found in .env")
        return False
    
    print("✅ Groq API key found")
    
    # Initialize Groq LLM
    llm = ChatGroq(
        api_key=groq_key,
        model="llama-3.3-70b-versatile",
        temperature=0.7
    )
    
    # Create researcher agent
    print("Creating research agent with Groq...")
    researcher = Agent(
        role='Research Specialist',
        goal='Find accurate information about any topic',
        backstory='Expert researcher who verifies information from multiple sources',
        tools=[research_tool],
        llm=llm,
        verbose=True
    )
    
    # Create task
    research_task = Task(
        description='Research: What are the benefits of using agentic AI systems? List 3-5 key benefits.',
        expected_output='A clear list of 3-5 benefits with brief explanations',
        agent=researcher
    )
    
    # Create and run crew
    print("\n🚀 Starting research with Groq...\n")
    
    crew = Crew(
        agents=[researcher],
        tasks=[research_task],
        verbose=True
    )
    
    try:
        result = crew.kickoff()
        
        print("\n" + "="*70)
        print("✅ GROQ TEST - SUCCESS")
        print("="*70)
        print(result)
        print("="*70)
        return True
        
    except Exception as e:
        print("\n" + "="*70)
        print("❌ GROQ TEST - FAILED")
        print("="*70)
        print(f"Error: {str(e)}")
        print("="*70)
        return False

def test_research_tool():
    """Test the free research tool directly"""
    print("\n" + "="*70)
    print("TEST 3: FREE RESEARCH TOOL")
    print("="*70)
    
    try:
        print("\n🔍 Testing research tool with query: 'artificial intelligence'")
        result = research_tool._run("artificial intelligence", max_results=3)
        
        print("\n📊 Research Results:")
        print(result[:500] + "..." if len(result) > 500 else result)
        
        print("\n" + "="*70)
        print("✅ RESEARCH TOOL TEST - SUCCESS")
        print("="*70)
        return True
        
    except Exception as e:
        print("\n" + "="*70)
        print("❌ RESEARCH TOOL TEST - FAILED")
        print("="*70)
        print(f"Error: {str(e)}")
        print("="*70)
        return False

def main():
    """Run all basic agent tests"""
    print("\n" + "="*70)
    print("🧪 BASIC AGENT TESTS - FREE LLM STACK")
    print("="*70)
    print("Testing: Gemini, Groq, Free Research Tools")
    print("="*70)
    
    results = {}
    
    # Test 1: Gemini
    results['gemini'] = test_with_gemini()
    
    # Test 2: Groq
    results['groq'] = test_with_groq()
    
    # Test 3: Research Tool
    results['research_tool'] = test_research_tool()
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name.upper()}")
    
    total = len(results)
    passed = sum(results.values())
    
    print("-"*70)
    print(f"Results: {passed}/{total} tests passed")
    print("="*70)
    
    if passed == total:
        print("\n🎉 All tests passed! Basic agent system working correctly.\n")
    else:
        print("\n⚠️ Some tests failed. Check your API keys and configuration.\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)