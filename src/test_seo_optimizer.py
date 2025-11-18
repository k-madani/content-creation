from tools.seo_optimizer import SEOOptimizerTool

seo = SEOOptimizerTool()

sample_content = """
# Docker Containerization Guide

Docker is a powerful platform for containerization. Learn Docker basics here.

## What is Docker?

Docker allows you to package applications with dependencies. Many developers use Docker daily.

## Why Use Docker?

Docker provides portability and consistency. Teams use Docker for deployment worldwide.

## Getting Started

To start with Docker, install it first. Then create your first Docker container.

Docker makes development easier. Docker simplifies deployment processes significantly.
"""

print("Testing SEO Optimizer with Error Handling")
print("="*70)

# Test 1: With keyword
print("\nTest 1: With target keyword 'Docker'")
result = seo.run(sample_content, "Docker")
print(result)

# Test 2: Without keyword
print("\n" + "="*70)
print("\nTest 2: Without target keyword")
result = seo.run(sample_content)
print(result)

# Test 3: Error handling (too short)
print("\n" + "="*70)
print("\nTest 3: Error handling (short text)")
result = seo.run("Too short")
print(result)

print("\n" + "="*70)
print("All tests completed!")