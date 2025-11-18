"""
Test Cases for ContentCraft AI System
"""

import time
from datetime import datetime
from main import create_content, save_output

def run_test_case(test_num, topic, keyword=None, tone_ref=None):
    """Run a single test case and collect metrics"""
    
    print(f"\n{'='*70}")
    print(f"TEST CASE {test_num}")
    print(f"{'='*70}")
    print(f"Topic: {topic}")
    print(f"Keyword: {keyword if keyword else 'None'}")
    print(f"Tone Matching: {'Yes' if tone_ref else 'No'}")
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*70}\n")
    
    start_time = time.time()
    
    try:
        result = create_content(topic, tone_ref, keyword, enable_seo=True)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Save output
        output_file = save_output(result, f"test{test_num}_{topic}")
        
        # Collect metrics
        word_count = len(str(result).split())
        has_headers = '##' in str(result)
        has_seo = 'SEO ANALYSIS' in str(result)
        
        metrics = {
            'test_number': test_num,
            'topic': topic,
            'success': True,
            'duration_seconds': duration,
            'duration_minutes': duration / 60,
            'word_count': word_count,
            'has_headers': has_headers,
            'has_seo_analysis': has_seo,
            'output_file': output_file
        }
        
        print(f"\n{'='*70}")
        print(f"TEST CASE {test_num} - SUCCESS")
        print(f"{'='*70}")
        print(f"Duration: {duration/60:.1f} minutes")
        print(f"Word Count: {word_count}")
        print(f"Output: {output_file}")
        print(f"{'='*70}\n")
        
        return metrics
        
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n{'='*70}")
        print(f"TEST CASE {test_num} - FAILED")
        print(f"{'='*70}")
        print(f"Error: {str(e)}")
        print(f"{'='*70}\n")
        
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
    print("CONTENTCRAFT AI - TEST SUITE")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    test_cases = [
        {
            'topic': 'Benefits of meditation for beginners',
            'keyword': 'meditation',
            'tone_ref': None
        },
        {
            'topic': 'Introduction to Python programming',
            'keyword': 'Python programming',
            'tone_ref': None
        },
        {
            'topic': 'Healthy meal prep ideas for busy professionals',
            'keyword': 'meal prep',
            'tone_ref': None
        },
        {
            'topic': 'Small business marketing strategies',
            'keyword': 'marketing strategies',
            'tone_ref': None
        },
        {
            'topic': 'Home workout routines without equipment',
            'keyword': 'home workout',
            'tone_ref': None
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        metrics = run_test_case(
            i,
            test_case['topic'],
            test_case['keyword'],
            test_case['tone_ref']
        )
        results.append(metrics)
        
        # Pause between tests
        if i < len(test_cases):
            print("\nWaiting 30 seconds before next test...\n")
            time.sleep(30)
    
    # Generate summary report
    print("\n" + "="*70)
    print("TEST SUMMARY REPORT")
    print("="*70)
    
    successful_tests = [r for r in results if r['success']]
    failed_tests = [r for r in results if not r['success']]
    
    print(f"\nTotal Tests: {len(results)}")
    print(f"Successful: {len(successful_tests)}")
    print(f"Failed: {len(failed_tests)}")
    
    if successful_tests:
        avg_duration = sum(r['duration_seconds'] for r in successful_tests) / len(successful_tests)
        avg_words = sum(r['word_count'] for r in successful_tests) / len(successful_tests)
        
        print(f"\nAverage Duration: {avg_duration/60:.1f} minutes")
        print(f"Average Word Count: {avg_words:.0f} words")
    
    print("\nDetailed Results:")
    print("-" * 70)
    for r in results:
        status = "PASS" if r['success'] else "FAIL"
        print(f"Test {r['test_number']}: {status} - {r['topic'][:50]}")
        if r['success']:
            print(f"  Duration: {r['duration_minutes']:.1f}min | Words: {r['word_count']}")
        else:
            print(f"  Error: {r.get('error', 'Unknown')}")
    
    print("="*70)
    
    # Save results to file
    with open('test_results.txt', 'w') as f:
        f.write("CONTENTCRAFT AI - TEST RESULTS\n")
        f.write("="*70 + "\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Tests: {len(results)}\n")
        f.write(f"Successful: {len(successful_tests)}\n")
        f.write(f"Failed: {len(failed_tests)}\n\n")
        
        for r in results:
            f.write(f"\nTest {r['test_number']}: {r['topic']}\n")
            f.write(f"Status: {'SUCCESS' if r['success'] else 'FAILED'}\n")
            if r['success']:
                f.write(f"Duration: {r['duration_minutes']:.2f} minutes\n")
                f.write(f"Word Count: {r['word_count']}\n")
                f.write(f"Output: {r['output_file']}\n")
            else:
                f.write(f"Error: {r.get('error', 'Unknown')}\n")
    
    print("\nResults saved to: test_results.txt\n")

if __name__ == "__main__":
    run_all_tests()