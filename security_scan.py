#!/usr/bin/env python3
"""
Security Scanning Script for Slack Intro Bot

This script performs comprehensive security checks on the codebase.
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

def run_security_scan():
    """Run comprehensive security scan"""
    print("🔒 Starting comprehensive security scan...")
    print("=" * 60)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'scans': {}
    }
    
    # 1. Bandit security scan
    print("\n📋 Running Bandit security scan...")
    try:
        result = subprocess.run([
            'bandit', '-r', '.', '-f', 'json', '-ll'
        ], capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            print("✅ Bandit scan completed - no high/critical issues found")
            results['scans']['bandit'] = {'status': 'passed', 'output': result.stdout}
        else:
            print("⚠️  Bandit found security issues:")
            print(result.stdout)
            results['scans']['bandit'] = {'status': 'issues_found', 'output': result.stdout}
    except Exception as e:
        print(f"❌ Bandit scan failed: {e}")
        results['scans']['bandit'] = {'status': 'failed', 'error': str(e)}
    
    # 2. Safety dependency scan
    print("\n📦 Running Safety dependency scan...")
    try:
        result = subprocess.run([
            'safety', 'scan', '-r', 'requirements.txt'
        ], capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            print("✅ Safety scan completed - no vulnerabilities found")
            results['scans']['safety'] = {'status': 'passed', 'output': result.stdout}
        else:
            print("⚠️  Safety found vulnerabilities:")
            print(result.stdout)
            results['scans']['safety'] = {'status': 'vulnerabilities_found', 'output': result.stdout}
    except Exception as e:
        print(f"❌ Safety scan failed: {e}")
        results['scans']['safety'] = {'status': 'failed', 'error': str(e)}
    
    # 3. File permissions check
    print("\n📁 Checking file permissions...")
    permission_issues = []
    sensitive_files = [
        'config.py',
        'daily_intros.py',
        'user_profile_search.py',
        'mcp_adapter.py',
        'security_config.py'
    ]
    
    for file_path in sensitive_files:
        if os.path.exists(file_path):
            stat = os.stat(file_path)
            mode = oct(stat.st_mode)[-3:]
            if mode != '644' and mode != '755':
                permission_issues.append(f"{file_path}: {mode}")
    
    if permission_issues:
        print("⚠️  File permission issues found:")
        for issue in permission_issues:
            print(f"   {issue}")
        results['scans']['permissions'] = {'status': 'issues_found', 'issues': permission_issues}
    else:
        print("✅ File permissions are secure")
        results['scans']['permissions'] = {'status': 'passed'}
    
    # 4. Check for hardcoded secrets
    print("\n🔐 Scanning for hardcoded secrets...")
    secret_patterns = [
        r'password\s*=\s*["\'][^"\']+["\']',
        r'api[_-]?key\s*=\s*["\'][^"\']+["\']',
        r'token\s*=\s*["\'][^"\']+["\']',
        r'secret\s*=\s*["\'][^"\']+["\']',
        r'slack[_-]?token\s*=\s*["\'][^"\']+["\']',
        r'bot[_-]?token\s*=\s*["\'][^"\']+["\']'
    ]
    
    import re
    secret_issues = []
    
    for file_path in Path('.').rglob('*.py'):
        if file_path.name.startswith('.') or 'test' in str(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for pattern in secret_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        secret_issues.append(f"{file_path}: {match}")
        except Exception:
            continue
    
    if secret_issues:
        print("⚠️  Potential hardcoded secrets found:")
        for issue in secret_issues:
            print(f"   {issue}")
        results['scans']['secrets'] = {'status': 'issues_found', 'issues': secret_issues}
    else:
        print("✅ No hardcoded secrets detected")
        results['scans']['secrets'] = {'status': 'passed'}
    
    # 5. Environment file check
    print("\n🌍 Checking environment configuration...")
    env_issues = []
    
    if os.path.exists('.env'):
        env_issues.append(".env file exists in repository - should be in .gitignore")
    
    if not os.path.exists('.env.example'):
        env_issues.append(".env.example file missing - should provide template")
    
    if env_issues:
        print("⚠️  Environment configuration issues:")
        for issue in env_issues:
            print(f"   {issue}")
        results['scans']['environment'] = {'status': 'issues_found', 'issues': env_issues}
    else:
        print("✅ Environment configuration is secure")
        results['scans']['environment'] = {'status': 'passed'}
    
    # 6. Security configuration test
    print("\n🛡️  Testing security configuration...")
    try:
        from security_config import get_security_manager
        security = get_security_manager()
        
        # Test input validation
        test_input = {
            'first_name': 'Test User',
            'message_text': 'Hello <script>alert("xss")</script> world!'
        }
        sanitized = security.validate_and_sanitize_input(test_input)
        
        if '<script>' not in sanitized['message_text']:
            print("✅ Security configuration working - XSS protection active")
            results['scans']['security_config'] = {'status': 'passed'}
        else:
            print("⚠️  Security configuration issue - XSS protection not working")
            results['scans']['security_config'] = {'status': 'issues_found'}
    except Exception as e:
        print(f"❌ Security configuration test failed: {e}")
        results['scans']['security_config'] = {'status': 'failed', 'error': str(e)}
    
    # Save results
    results_file = 'security-scan-results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📊 Security scan completed. Results saved to {results_file}")
    
    # Summary
    total_scans = len(results['scans'])
    passed_scans = sum(1 for scan in results['scans'].values() if scan['status'] == 'passed')
    
    print(f"\n📈 Security Scan Summary:")
    print(f"   Total scans: {total_scans}")
    print(f"   Passed: {passed_scans}")
    print(f"   Issues found: {total_scans - passed_scans}")
    
    if passed_scans == total_scans:
        print("🎉 All security checks passed!")
        return 0
    else:
        print("⚠️  Some security issues were found. Please review the results above.")
        return 1

if __name__ == "__main__":
    sys.exit(run_security_scan())
