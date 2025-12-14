import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from tools.title_generator import generate_titles, get_best_title

# Test 1: Professional tone
print("TEST 1: Professional Tone")
print("="*60)
result = generate_titles("AI in Healthcare", "professional", 5)
print(result)

print("\n\n")

# Test 2: Casual tone
print("TEST 2: Casual Tone")
print("="*60)
result = generate_titles("Best Coffee Shops in Boston", "casual", 5)
print(result)

print("\n\n")

# Test 3: Technical tone
print("TEST 3: Technical Tone")
print("="*60)
result = generate_titles("Machine Learning Algorithms", "technical", 5)
print(result)

print("\n\n")

# Test 4: Quick best title
print("TEST 4: Get Best Title Only")
print("="*60)
best = get_best_title("Content Marketing Strategies", "professional")
print(f"Best title: {best}")