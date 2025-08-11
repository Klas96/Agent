#!/usr/bin/env python3
"""
Direct test for the document service functionality.

This script tests the LaTeX-based document generation service directly.
"""

import sys
import os
import subprocess
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_document_service_direct():
    """Test the document service directly without importing the full package."""
    print("Testing Document Service Directly...")
    
    try:
        # Import only the document service
        from pocketflow.services.document_service import DocumentService
        
        # Create document service
        doc_service = DocumentService()
        print("✅ DocumentService created successfully")
        
        # Test template creation
        templates_dir = Path("templates/latex")
        if templates_dir.exists():
            print("✅ Templates directory exists")
            
            # Check for template files
            template_files = list(templates_dir.glob("*.tex"))
            print(f"   Found {len(template_files)} template files:")
            for template in template_files:
                print(f"   - {template.name}")
            
            # Test document type detection
            test_prompts = [
                ("Create a business report about AI", "business_report"),
                ("Generate a technical report on ML", "technical_report"),
                ("Write a report about climate", "report")
            ]
            
            for prompt, expected_type in test_prompts:
                detected_type = doc_service._determine_document_type(prompt)
                status = "✅" if detected_type == expected_type else "❌"
                print(f"{status} '{prompt}' -> {detected_type} (expected: {expected_type})")
            
            # Test template path resolution
            for doc_type in ["business_report", "technical_report", "report"]:
                template_path = doc_service._get_template_path(doc_type)
                if template_path.exists():
                    print(f"✅ Template found for {doc_type}: {template_path.name}")
                else:
                    print(f"❌ Template missing for {doc_type}")
            
            return True
        else:
            print("❌ Templates directory not found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing document service: {e}")
        return False

def test_latex_compilation_with_service():
    """Test LaTeX compilation using the document service."""
    print("\nTesting LaTeX compilation with Document Service...")
    
    try:
        from pocketflow.services.document_service import DocumentService
        
        # Create a simple content request
        class MockContentRequest:
            def __init__(self, prompt):
                self.prompt = prompt
                self.content_type = "document"
                self.duration = None
        
        # Create document service
        doc_service = DocumentService()
        
        # Test with a simple prompt
        request = MockContentRequest("Test document generation")
        
        # Generate document
        pdf_path = doc_service.generate_document(request)
        
        if pdf_path and os.path.exists(pdf_path):
            print("✅ Document generation successful")
            print(f"   PDF created: {pdf_path}")
            print(f"   File size: {os.path.getsize(pdf_path)} bytes")
            return True
        else:
            print("❌ Document generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in document generation: {e}")
        return False

def test_fallback_content():
    """Test fallback content generation."""
    print("\nTesting fallback content generation...")
    
    try:
        from pocketflow.services.document_service import DocumentService
        
        doc_service = DocumentService()
        
        # Test fallback content for different document types
        test_cases = [
            ("business_report", "Business analysis"),
            ("technical_report", "Technical analysis"),
            ("report", "General report")
        ]
        
        for doc_type, prompt in test_cases:
            content = doc_service._create_fallback_content(prompt, doc_type)
            print(f"✅ Fallback content for {doc_type}:")
            print(f"   Title: {content.get('title', 'N/A')}")
            print(f"   Abstract: {content.get('abstract', 'N/A')[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in fallback content generation: {e}")
        return False

if __name__ == "__main__":
    print("Document Creator Direct Test Suite")
    print("=" * 50)
    
    # Test document service directly
    service_ok = test_document_service_direct()
    
    # Test LaTeX compilation with service
    compilation_ok = test_latex_compilation_with_service()
    
    # Test fallback content
    fallback_ok = test_fallback_content()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Document Service: {'✅ PASS' if service_ok else '❌ FAIL'}")
    print(f"LaTeX Compilation: {'✅ PASS' if compilation_ok else '❌ FAIL'}")
    print(f"Fallback Content: {'✅ PASS' if fallback_ok else '❌ FAIL'}")
    
    if all([service_ok, compilation_ok, fallback_ok]):
        print("\n🎉 All tests passed! Document creator is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
    
    print("\nTest suite completed!") 