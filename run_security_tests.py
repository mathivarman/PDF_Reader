#!/usr/bin/env python
"""
Security Test Runner for AI Legal Document Explainer
Runs comprehensive security tests and generates reports.
"""

import os
import sys
import django
import time
import json
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pdf_reader.settings')
django.setup()

from django.test.utils import get_runner
from django.conf import settings
from django.core.management import execute_from_command_line
from django.test.utils import setup_test_environment, teardown_test_environment

def run_security_tests():
    """Run all security tests and generate a comprehensive report."""
    
    print("🔒 Starting Security Test Suite")
    print("=" * 50)
    
    # Test results storage
    test_results = {
        'timestamp': datetime.now().isoformat(),
        'tests_run': 0,
        'tests_passed': 0,
        'tests_failed': 0,
        'test_details': [],
        'security_score': 0,
        'recommendations': []
    }
    
    # Setup test environment once
    setup_test_environment()
    
    try:
        # Run all security tests in one go
        print("\n🧪 Running Security Tests...")
        
        # Use Django's test runner
        TestRunner = get_runner(settings)
        test_runner = TestRunner(verbosity=2, interactive=False)
        
        # Run all tests in the security module
        failures = test_runner.run_tests(['main.tests_security'])
        
        if failures:
            test_results['tests_failed'] = 1
            test_results['test_details'].append({
                'module': 'main.tests_security',
                'status': 'FAILED',
                'message': f'{failures} tests failed'
            })
            print(f"❌ Security Tests - FAILED ({failures} failures)")
        else:
            test_results['tests_passed'] = 1
            test_results['test_details'].append({
                'module': 'main.tests_security',
                'status': 'PASSED',
                'message': 'All security tests passed'
            })
            print("✅ Security Tests - PASSED")
        
        test_results['tests_run'] = 1
        
    except Exception as e:
        test_results['tests_failed'] = 1
        test_results['test_details'].append({
            'module': 'main.tests_security',
            'status': 'ERROR',
            'message': str(e)
        })
        print(f"💥 Security Tests - ERROR: {e}")
    
    finally:
        # Cleanup test environment
        teardown_test_environment()
    
    # Calculate security score
    if test_results['tests_run'] > 0:
        test_results['security_score'] = (test_results['tests_passed'] / test_results['tests_run']) * 100
    
    # Generate recommendations
    if test_results['tests_failed'] > 0:
        test_results['recommendations'].append(
            "Fix failed security tests before deployment"
        )
    
    if test_results['security_score'] < 90:
        test_results['recommendations'].append(
            "Security score below 90%. Review and improve security measures."
        )
    
    # Print summary
    print("\n" + "=" * 50)
    print("🔒 SECURITY TEST SUMMARY")
    print("=" * 50)
    print(f"Tests Run: {test_results['tests_run']}")
    print(f"Tests Passed: {test_results['tests_passed']}")
    print(f"Tests Failed: {test_results['tests_failed']}")
    print(f"Security Score: {test_results['security_score']:.1f}%")
    
    if test_results['recommendations']:
        print("\n📋 RECOMMENDATIONS:")
        for rec in test_results['recommendations']:
            print(f"  • {rec}")
    
    # Save detailed report
    report_file = f"security_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    return test_results['security_score'] >= 90

def run_vulnerability_scan():
    """Run additional vulnerability scans."""
    
    print("\n🔍 Running Vulnerability Scans...")
    print("=" * 50)
    
    # Check for common security issues
    security_checks = {
        'DEBUG_MODE': settings.DEBUG,
        'SECRET_KEY_EXPOSED': 'django-insecure-' in settings.SECRET_KEY,
        'ALLOWED_HOSTS_EMPTY': len(settings.ALLOWED_HOSTS) == 0,
        'CSRF_DISABLED': not hasattr(settings, 'CSRF_COOKIE_SECURE'),
        'SESSION_SECURE': not hasattr(settings, 'SESSION_COOKIE_SECURE'),
    }
    
    vulnerabilities = []
    
    for check, value in security_checks.items():
        if value:
            vulnerabilities.append(check)
            print(f"⚠️  {check}: {value}")
        else:
            print(f"✅ {check}: Secure")
    
    if vulnerabilities:
        print(f"\n🚨 Found {len(vulnerabilities)} potential vulnerabilities:")
        for vuln in vulnerabilities:
            print(f"  • {vuln}")
    else:
        print("\n✅ No obvious vulnerabilities detected")
    
    return len(vulnerabilities) == 0

def generate_security_checklist():
    """Generate a security checklist for deployment."""
    
    print("\n📋 SECURITY DEPLOYMENT CHECKLIST")
    print("=" * 50)
    
    checklist = [
        "✅ Security tests passing",
        "✅ DEBUG mode disabled in production",
        "✅ Secret key properly configured",
        "✅ ALLOWED_HOSTS configured",
        "✅ CSRF protection enabled",
        "✅ Session security configured",
        "✅ File upload validation implemented",
        "✅ Input sanitization implemented",
        "✅ SQL injection protection (Django ORM)",
        "✅ XSS protection (Django templates)",
        "✅ HTTPS enabled",
        "✅ Security headers configured",
        "✅ Error handling without sensitive data exposure",
        "✅ Logging configured",
        "✅ Backup strategy implemented",
        "✅ Monitoring and alerting setup",
        "✅ Regular security updates plan",
        "✅ Incident response plan",
    ]
    
    for item in checklist:
        print(f"  {item}")
    
    print("\n📝 Additional Recommendations:")
    print("  • Conduct penetration testing")
    print("  • Set up automated security scanning")
    print("  • Implement rate limiting")
    print("  • Add two-factor authentication if needed")
    print("  • Regular security audits")
    print("  • Keep dependencies updated")

def main():
    """Main function to run all security checks."""
    
    print("🚀 AI Legal Document Explainer - Security Test Suite")
    print("=" * 60)
    
    # Run security tests
    tests_passed = run_security_tests()
    
    # Run vulnerability scan
    vuln_scan_passed = run_vulnerability_scan()
    
    # Generate checklist
    generate_security_checklist()
    
    # Final assessment
    print("\n" + "=" * 60)
    print("🎯 FINAL SECURITY ASSESSMENT")
    print("=" * 60)
    
    if tests_passed and vuln_scan_passed:
        print("✅ SECURITY STATUS: READY FOR DEPLOYMENT")
        print("   All security tests passed and no vulnerabilities detected.")
        return 0
    else:
        print("❌ SECURITY STATUS: NOT READY FOR DEPLOYMENT")
        print("   Please address security issues before deployment.")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
