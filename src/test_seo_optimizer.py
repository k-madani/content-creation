from tools.seo_optimizer import SEOOptimizerTool

# Initialize tool
seo_optimizer = SEOOptimizerTool()

# Sample blog post
sample_post = """
# Docker Containerization: A Beginner's Guide

Docker is a platform that makes it easy to build, ship, and run applications. 
You can think of it like a shipping container for your code.

## What is Docker?

Just as shipping containers revolutionized global trade by standardizing how goods are transported, 
Docker containers standardize how applications are packaged and deployed. What's really cool is that 
your app will run the same way on your laptop, your colleague's computer, and in production.

## Why Use Docker?

Docker containers are lightweight and portable. They include everything your application needs to run. 
This means no more "works on my machine" problems. Docker has become essential for modern development.

## Getting Started

To start with Docker, you first need to install it on your system. Then you can create your first 
container using simple commands. Docker makes deployment easy and reliable.

## Conclusion

Docker containerization is a game-changer for developers. It simplifies deployment and ensures 
consistency across environments. Start learning Docker today!
"""

print("Testing SEO Optimizer Tool")
print("=" * 70)
print("\nAnalyzing blog post for SEO...\n")

# Test without target keyword
result = seo_optimizer.run(sample_post)
print(result)

print("\n" + "=" * 70)
print("\nNow testing WITH target keyword...")
print("=" * 70 + "\n")

# Test with target keyword
result_with_keyword = seo_optimizer.run(sample_post, target_keyword="Docker")
print(result_with_keyword)

print("\n" + "=" * 70)
print("Test Complete!")