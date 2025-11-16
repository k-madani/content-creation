from tools.tone_analyzer import ToneAnalyzerTool

# Initialize tool
tone_analyzer = ToneAnalyzerTool()

# Test with sample text
sample_text = """
Docker is a platform that makes it easy to build, ship, and run applications. 
You can think of it like a shipping container for your code. Just as shipping 
containers revolutionized global trade by standardizing how goods are transported, 
Docker containers standardize how applications are packaged and deployed. 
What's really cool is that your app will run the same way on your laptop, 
your colleague's computer, and in production. No more "works on my machine" problems!
"""

print("Testing Tone Analyzer Tool")
print("=" * 70)
print("\nAnalyzing sample text...\n")

result = tone_analyzer.run(sample_text)
print(result)

print("\n" + "=" * 70)
print("Test Complete!")