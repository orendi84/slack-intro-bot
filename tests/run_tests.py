#!/usr/bin/env python3
"""
Test Runner for Slack Intro Bot

Comprehensive test suite runner with coverage reporting and detailed output.
"""

import unittest
import sys
import os
import subprocess
import time
from pathlib import Path

def run_tests():
    """Run all tests with detailed reporting"""
    print("🧪 Starting Slack Intro Bot Test Suite")
    print("=" * 50)
    
    # Add project root to Python path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = project_root / 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2,
        descriptions=True,
        failfast=False
    )
    
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    print(f"⏱️  Total time: {end_time - start_time:.2f} seconds")
    print(f"✅ Tests run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"🚨 Errors: {len(result.errors)}")
    print(f"⏭️  Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\n❌ Test Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n🚨 Test Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('\\n')[-2].strip()}")
    
    # Success/failure status
    if result.wasSuccessful():
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n💥 {len(result.failures + result.errors)} test(s) failed!")
        return 1

def run_coverage():
    """Run tests with coverage reporting"""
    try:
        import coverage
        print("📊 Running tests with coverage...")
        
        cov = coverage.Coverage()
        cov.start()
        
        exit_code = run_tests()
        
        cov.stop()
        cov.save()
        
        print("\n📈 Coverage Report:")
        cov.report()
        
        # Generate HTML report
        cov.html_report(directory='htmlcov')
        print(f"\n📄 HTML coverage report generated in 'htmlcov/' directory")
        
        return exit_code
        
    except ImportError:
        print("⚠️  Coverage not available. Install with: pip install coverage")
        return run_tests()

def run_specific_test(test_name):
    """Run a specific test module"""
    print(f"🎯 Running specific test: {test_name}")
    
    # Add project root to Python path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    # Load specific test
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(f'tests.{test_name}')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1

def lint_code():
    """Run code linting"""
    print("🔍 Running code linting...")
    
    try:
        # Run flake8 if available
        result = subprocess.run([
            'flake8', 
            'daily_intros.py', 
            'user_profile_search.py', 
            'mcp_adapter.py', 
            'config.py',
            '--max-line-length=120',
            '--ignore=E501,W503'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Code linting passed!")
            return 0
        else:
            print("❌ Code linting failed:")
            print(result.stdout)
            return 1
            
    except FileNotFoundError:
        print("⚠️  flake8 not available. Install with: pip install flake8")
        return 0

def main():
    """Main test runner entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'coverage':
            return run_coverage()
        elif command == 'lint':
            return lint_code()
        elif command == 'all':
            lint_result = lint_code()
            test_result = run_tests()
            return max(lint_result, test_result)
        elif command.startswith('test_'):
            return run_specific_test(command)
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: coverage, lint, all, test_<name>")
            return 1
    else:
        return run_tests()

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
