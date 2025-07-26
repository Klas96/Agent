#!/usr/bin/env python3
"""
Test runner for PocketFlow.

This script runs the test suite and deploys if all tests pass.
"""

import sys
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime

class TestRunner:
    """Test runner with deployment capabilities."""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()
        
    def run_unit_tests(self):
        """Run unit tests for the investigation + report workflow."""
        print("=" * 60)
        print("🧪 Running Unit Tests")
        print("=" * 60)
        
        try:
            # Run the investigation + report workflow tests
            result = subprocess.run([
                sys.executable, "-m", "unittest", 
                "tests.test_investigation_report_workflow_simple",
                "-v"
            ], capture_output=True, text=True)
            
            self.test_results["unit_tests"] = {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr,
                "return_code": result.returncode
            }
            
            if result.returncode == 0:
                print("✅ Unit tests passed!")
                print(f"Output: {result.stdout}")
            else:
                print("❌ Unit tests failed!")
                print(f"Errors: {result.stderr}")
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Error running unit tests: {e}")
            self.test_results["unit_tests"] = {
                "success": False,
                "error": str(e)
            }
            return False
    
    def run_document_service_tests(self):
        """Run document service tests."""
        print("\n" + "=" * 60)
        print("📄 Running Document Service Tests")
        print("=" * 60)
        
        try:
            # Run document service tests
            result = subprocess.run([
                sys.executable, "tests/test_document_service_simple.py"
            ], capture_output=True, text=True)
            
            self.test_results["document_service_tests"] = {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr,
                "return_code": result.returncode
            }
            
            if result.returncode == 0:
                print("✅ Document service tests passed!")
                print(f"Output: {result.stdout}")
            else:
                print("❌ Document service tests failed!")
                print(f"Errors: {result.stderr}")
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Error running document service tests: {e}")
            self.test_results["document_service_tests"] = {
                "success": False,
                "error": str(e)
            }
            return False
    
    def run_latex_tests(self):
        """Run LaTeX compilation tests."""
        print("\n" + "=" * 60)
        print("📝 Running LaTeX Tests")
        print("=" * 60)
        
        try:
            # Test LaTeX installation
            result = subprocess.run([
                "pdflatex", "--version"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ LaTeX is installed and working")
                print(f"Version: {result.stdout.split('\n')[0]}")
                
                # Test template creation
                templates_dir = Path("templates/latex")
                if templates_dir.exists():
                    template_files = list(templates_dir.glob("*.tex"))
                    print(f"✅ Found {len(template_files)} LaTeX templates:")
                    for template in template_files:
                        print(f"   - {template.name}")
                    
                    self.test_results["latex_tests"] = {
                        "success": True,
                        "templates_found": len(template_files),
                        "template_names": [t.name for t in template_files]
                    }
                    return True
                else:
                    print("❌ Templates directory not found")
                    self.test_results["latex_tests"] = {
                        "success": False,
                        "error": "Templates directory not found"
                    }
                    return False
            else:
                print("❌ LaTeX not installed")
                self.test_results["latex_tests"] = {
                    "success": False,
                    "error": "LaTeX not installed"
                }
                return False
                
        except Exception as e:
            print(f"❌ Error running LaTeX tests: {e}")
            self.test_results["latex_tests"] = {
                "success": False,
                "error": str(e)
            }
            return False
    
    def deploy_to_production(self):
        """Deploy to production if all tests pass."""
        print("\n" + "=" * 60)
        print("🚀 Deploying to Production")
        print("=" * 60)
        
        try:
            # Check if all tests passed
            all_tests_passed = all([
                self.test_results.get("unit_tests", {}).get("success", False),
                self.test_results.get("document_service_tests", {}).get("success", False),
                self.test_results.get("latex_tests", {}).get("success", False)
            ])
            
            if not all_tests_passed:
                print("❌ Not all tests passed. Skipping deployment.")
                return False
            
            print("✅ All tests passed! Proceeding with deployment...")
            
            # Use the existing deploy script
            result = subprocess.run(["./deploy.sh"], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Deployment completed successfully!")
                print(f"Output: {result.stdout}")
            else:
                print("❌ Deployment failed!")
                print(f"Errors: {result.stderr}")
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Error during deployment: {e}")
            return False
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        print("\n" + "=" * 60)
        print("📋 Generating Test Report")
        print("=" * 60)
        
        end_time = time.time()
        duration = end_time - self.start_time
        
        # Calculate test statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result.get("success", False))
        failed_tests = total_tests - passed_tests
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": duration,
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            "test_results": self.test_results
        }
        
        # Save report to file
        with open("test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print(f"📊 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {report['test_summary']['success_rate']:.1f}%")
        print(f"   Duration: {duration:.2f} seconds")
        
        print(f"\n📄 Detailed report saved to: test_report.json")
        
        return report
    
    def run_all_tests(self):
        """Run all tests and deploy if successful."""
        print("🚀 PocketFlow Test Suite")
        print("=" * 60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test suites
        unit_tests_passed = self.run_unit_tests()
        document_tests_passed = self.run_document_service_tests()
        latex_tests_passed = self.run_latex_tests()
        
        # Deploy if all tests pass
        deployment_success = self.deploy_to_production()
        
        # Generate final report
        report = self.generate_test_report()
        
        # Print final status
        print("\n" + "=" * 60)
        print("🎯 Final Status")
        print("=" * 60)
        
        if all([unit_tests_passed, document_tests_passed, latex_tests_passed]):
            print("✅ ALL TESTS PASSED!")
            if deployment_success:
                print("✅ DEPLOYMENT SUCCESSFUL!")
                print("🎉 Investigation + Report Workflow is now live in production!")
            else:
                print("❌ DEPLOYMENT FAILED!")
                print("⚠️  Tests passed but deployment failed. Check deployment logs.")
        else:
            print("❌ SOME TESTS FAILED!")
            print("⚠️  Deployment skipped due to test failures.")
        
        return report


def main():
    """Main function to run all tests and deploy."""
    runner = TestRunner()
    report = runner.run_all_tests()
    
    # Exit with appropriate code
    if report["test_summary"]["success_rate"] == 100:
        print("\n🎉 SUCCESS: All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ FAILURE: Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 