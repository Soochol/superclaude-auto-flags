#!/usr/bin/env python3
"""
Simple runner for the learning progression test
간단한 학습 진행 테스트 실행기
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from learning_progression_test import run_comprehensive_learning_test
    
    print("🚀 Starting SuperClaude Learning System Comprehensive Test")
    print("   This test simulates 25 user interactions over time to verify:")
    print("   • Pattern Recognition Learning")
    print("   • User Preference Adaptation") 
    print("   • Context Awareness Improvement")
    print("   • Confidence Calibration Enhancement")
    print("   • Feedback Processing Effectiveness")
    print("   • Data Persistence and Integrity")
    print("   • Cold vs Warm System Performance")
    print()
    
    # Run the comprehensive test
    result = run_comprehensive_learning_test()
    
    if result:
        print("\n✅ Test completed successfully!")
        test_passed = result.get('test_summary', {}).get('test_passed', False)
        total_score = result.get('test_summary', {}).get('total_score', 0)
        
        print(f"Final Score: {total_score:.3f}/1.000")
        print(f"Test Result: {'PASS' if test_passed else 'FAIL'}")
        
        if test_passed:
            print("\n🎉 The SuperClaude learning system demonstrates effective learning capabilities!")
        else:
            print("\n⚠️ The learning system needs improvement in some areas.")
    else:
        print("\n❌ Test failed to complete properly.")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all required dependencies are installed:")
    print("  • numpy")
    print("  • sqlite3 (built-in)")
    print("  • json (built-in)")
    
except Exception as e:
    print(f"❌ Test execution error: {e}")
    import traceback
    traceback.print_exc()