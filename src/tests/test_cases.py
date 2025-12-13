"""
Comprehensive Test Cases for Content Creation System
Updated for Free LLM Stack (Gemini, Groq, Ollama)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import time
from datetime import datetime
from main import create_content_crew
from utils.metrics import get_metrics_collector
import json

def save_output(content, test_name):
    """Save test output to file"""
    output_dir = Path("output") / "tests"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{test_name}_{timestamp}.md"
    filepath = output_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# Test Output: {test_name}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("="*70 + "\n\n")
        f.write(str(content))
    
    return str(filepath)

def run_test_case(test_num, topic, audience, keywords=None, word_count=1000):
    """Run a single test case and collect metrics"""
    
    print(f"\n{'='*70}")
    print(f"TEST CASE {test_num}")
    print(f"{'='*70}")
    print(f"Topic: {topic}")
    print(f"Audience: {audience}")
    print(f"Word Count Target: {word_count}")
    if keywords:
        print(f"Keywords: {', '.join(keywords)}")
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*70}\n")
    
    start_time = time.time()
    
    try:
        # Create and run crew
        crew = create_content_crew(
            topic=topic,
            audience=audience,
            content_type="blog post",
            word_count=word_count,
            keywords=keywords
        )
        
        # Get metrics collector
        metrics_collector = get_metrics_collector()
        metrics_collector.start_generation()
        
        # Run the crew
        result = crew.kickoff()
        
        # Finalize metrics
        final_metrics = metrics_collector.finalize(topic, success=True)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Save output
        output_file = save_output(result, f"test{test_num}_{topic.replace(' ', '_')[:30]}")
        
        # Analyze result
        result_str = str(result)
        word_count_actual = len(result_str.split())
        has_headers = '##' in result_str or '#' in result_str
        has_keywords = all(kw.lower() in result_str.lower() for kw in (keywords or []))
        
        # Collect metrics
        metrics = {
            'test_number': test_num,
            'topic': topic,
            'audience': audience,
            'success': True,
            'duration_seconds': duration,
            'duration_minutes': duration / 60,
            'word_count_target': word_count,
            'word_count_actual': word_count_actual,
            'has_headers': has_headers,
            'keywords_included': has_keywords,
            'output_file': output_file,
            'llm_providers_used': final_metrics.llm_providers_used,
            'estimated_cost': final_metrics.estimated_cost
        }
        
        print(f"\n{'='*70}")
        print(f"TEST CASE {test_num} - ✅ SUCCESS")
        print(f"{'='*70}")
        print(f"Duration: {duration/60:.2f} minutes ({duration:.1f} seconds)")
        print(f"Word Count: {word_count_actual} (target: {word_count})")
        print(f"Has Headers: {'Yes' if has_headers else 'No'}")
        if keywords:
            print(f"Keywords Included: {'Yes' if has_keywords else 'No'}")
        print(f"LLM Providers Used: {', '.join(final_metrics.llm_providers_used.keys())}")
        print(f"Cost: ${final_metrics.estimated_cost:.2f} (FREE!)")
        print(f"Output: {output_file}")
        print(f"{'='*70}\n")
        
        # Print metrics report
        print(metrics_collector.generate_report())
        
        return metrics
        
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n{'='*70}")
        print(f"TEST CASE {test_num} - ❌ FAILED")
        print(f"{'='*70}")
        print(f"Error: {str(e)}")
        print(f"Duration before failure: {duration:.1f} seconds")
        print(f"{'='*70}\n")
        
        import traceback
        traceback.print_exc()
        
        return {
            'test_number': test_num,
            'topic': topic,
            'success': False,
            'duration_seconds': duration,
            'error': str(e)
        }

def run_all_tests():
    """Run all test cases"""
    
    print("\n" + "="*70)
    print("🧪 CONTENT CREATION SYSTEM - COMPREHENSIVE TEST SUITE")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Using: FREE LLM Stack (Gemini → Groq → Ollama)")
    print("="*70 + "\n")
    
    test_cases = [
        {
            'topic': 'Benefits of meditation for beginners',
            'audience': 'wellness enthusiasts and beginners',
            'keywords': ['meditation', 'mindfulness', 'stress relief'],
            'word_count': 800
        },
        {
            'topic': 'Introduction to Python programming',
            'audience': 'aspiring developers and students',
            'keywords': ['Python programming', 'coding', 'beginners'],
            'word_count': 1000
        },
        {
            'topic': 'Healthy meal prep ideas for busy professionals',
            'audience': 'working professionals',
            'keywords': ['meal prep', 'healthy eating', 'time management'],
            'word_count': 900
        },
        {
            'topic': 'Small business marketing strategies on a budget',
            'audience': 'small business owners and entrepreneurs',
            'keywords': ['marketing strategies', 'small business', 'budget marketing'],
            'word_count': 1200
        },
        {
            'topic': 'Home workout routines without equipment',
            'audience': 'fitness enthusiasts',
            'keywords': ['home workout', 'bodyweight exercises', 'fitness'],
            'word_count': 850
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        metrics = run_test_case(
            i,
            test_case['topic'],
            test_case['audience'],
            test_case.get('keywords'),
            test_case.get('word_count', 1000)
        )
        results.append(metrics)
        
        # Pause between tests to avoid rate limits
        if i < len(test_cases):
            wait_time = 10  # Reduced since we're using free APIs
            print(f"\n⏳ Waiting {wait_time} seconds before next test...\n")
            time.sleep(wait_time)
    
    # Generate summary report
    generate_summary_report(results)
    
    return results

def generate_summary_report(results):
    """Generate and save comprehensive summary report"""
    
    print("\n" + "="*70)
    print("📊 COMPREHENSIVE TEST SUMMARY REPORT")
    print("="*70)
    
    successful_tests = [r for r in results if r['success']]
    failed_tests = [r for r in results if not r['success']]
    
    print(f"\n📈 Overall Statistics:")
    print(f"  Total Tests: {len(results)}")
    print(f"  Successful: {len(successful_tests)} ({len(successful_tests)/len(results)*100:.1f}%)")
    print(f"  Failed: {len(failed_tests)} ({len(failed_tests)/len(results)*100:.1f}%)")
    
    if successful_tests:
        avg_duration = sum(r['duration_seconds'] for r in successful_tests) / len(successful_tests)
        avg_words = sum(r.get('word_count_actual', 0) for r in successful_tests) / len(successful_tests)
        total_cost = sum(r.get('estimated_cost', 0) for r in successful_tests)
        
        print(f"\n⏱️ Performance Metrics:")
        print(f"  Average Duration: {avg_duration/60:.2f} minutes ({avg_duration:.1f} seconds)")
        print(f"  Fastest Test: {min(r['duration_seconds'] for r in successful_tests):.1f}s")
        print(f"  Slowest Test: {max(r['duration_seconds'] for r in successful_tests):.1f}s")
        
        print(f"\n📝 Content Metrics:")
        print(f"  Average Word Count: {avg_words:.0f} words")
        print(f"  Total Content Generated: {sum(r.get('word_count_actual', 0) for r in successful_tests)} words")
        
        print(f"\n💰 Cost Analysis:")
        print(f"  Total Cost: ${total_cost:.2f}")
        print(f"  Average Cost per Test: ${total_cost/len(successful_tests):.4f}")
        print(f"  🎉 100% FREE using Gemini, Groq, and Ollama!")
        
        # LLM Provider Usage
        all_providers = {}
        for r in successful_tests:
            providers = r.get('llm_providers_used', {})
            for provider, count in providers.items():
                all_providers[provider] = all_providers.get(provider, 0) + count
        
        if all_providers:
            print(f"\n🤖 LLM Provider Usage:")
            for provider, count in all_providers.items():
                print(f"  {provider.upper()}: {count} calls")
    
    print("\n" + "-"*70)
    print("📋 Detailed Test Results:")
    print("-"*70)
    
    for r in results:
        status = "✅ PASS" if r['success'] else "❌ FAIL"
        print(f"\nTest {r['test_number']}: {status}")
        print(f"  Topic: {r['topic']}")
        
        if r['success']:
            print(f"  Duration: {r['duration_minutes']:.2f} min")
            print(f"  Words: {r.get('word_count_actual', 'N/A')} (target: {r.get('word_count_target', 'N/A')})")
            print(f"  Headers: {'Yes' if r.get('has_headers') else 'No'}")
            print(f"  Keywords: {'Yes' if r.get('keywords_included') else 'No'}")
            print(f"  Output: {r['output_file']}")
        else:
            print(f"  Error: {r.get('error', 'Unknown error')}")
            print(f"  Duration before failure: {r['duration_seconds']:.1f}s")
    
    print("\n" + "="*70)
    
    # Save results to JSON
    results_dir = Path("output") / "test_results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = results_dir / f"test_results_{timestamp}.json"
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(results),
            'successful': len(successful_tests),
            'failed': len(failed_tests),
            'results': results
        }, f, indent=2, default=str)
    
    print(f"\n💾 JSON results saved to: {json_file}")
    
    # Save human-readable report
    txt_file = results_dir / f"test_report_{timestamp}.txt"
    
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write("CONTENT CREATION SYSTEM - TEST REPORT\n")
        f.write("="*70 + "\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"LLM Stack: FREE (Gemini, Groq, Ollama)\n\n")
        
        f.write(f"SUMMARY\n")
        f.write("-"*70 + "\n")
        f.write(f"Total Tests: {len(results)}\n")
        f.write(f"Successful: {len(successful_tests)}\n")
        f.write(f"Failed: {len(failed_tests)}\n\n")
        
        if successful_tests:
            f.write(f"Average Duration: {avg_duration/60:.2f} minutes\n")
            f.write(f"Average Word Count: {avg_words:.0f} words\n")
            f.write(f"Total Cost: $0.00 (FREE!)\n\n")
        
        f.write(f"\nDETAILED RESULTS\n")
        f.write("-"*70 + "\n\n")
        
        for r in results:
            f.write(f"Test {r['test_number']}: {r['topic']}\n")
            f.write(f"Status: {'SUCCESS' if r['success'] else 'FAILED'}\n")
            
            if r['success']:
                f.write(f"Duration: {r['duration_minutes']:.2f} minutes\n")
                f.write(f"Word Count: {r.get('word_count_actual', 'N/A')}\n")
                f.write(f"Output: {r['output_file']}\n")
            else:
                f.write(f"Error: {r.get('error', 'Unknown')}\n")
            
            f.write("\n")
    
    print(f"📝 Text report saved to: {txt_file}")
    print("\n" + "="*70)
    
    # Final message
    if len(successful_tests) == len(results):
        print("\n🎉 All tests passed! System working perfectly.\n")
    elif len(successful_tests) >= len(results) * 0.8:
        print(f"\n✅ Most tests passed ({len(successful_tests)}/{len(results)}). System functional.\n")
    else:
        print(f"\n⚠️ Several tests failed ({len(failed_tests)}/{len(results)}). Review errors.\n")

def run_quick_test():
    """Run a single quick test for verification"""
    
    print("\n" + "="*70)
    print("🚀 QUICK TEST - Single Content Generation")
    print("="*70)
    
    metrics = run_test_case(
        1,
        topic="The benefits of remote work",
        audience="professionals and managers",
        keywords=["remote work", "productivity", "work from home"],
        word_count=600
    )
    
    if metrics['success']:
        print("\n✅ Quick test passed! System is working.")
        print("   Run 'python test_cases.py --full' for complete test suite.\n")
    else:
        print("\n❌ Quick test failed. Check error messages above.\n")
    
    return metrics['success']

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        # Quick test
        success = run_quick_test()
    else:
        # Full test suite
        results = run_all_tests()
        success = all(r['success'] for r in results)
    
    sys.exit(0 if success else 1)