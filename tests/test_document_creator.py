#!/usr/bin/env python3
"""
Test script for the document creator functionality.

This script tests the LaTeX-based document generation service.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pocketflow.core.types import ContentGenerationRequest, ContentType
from pocketflow.services.document_service import DocumentService
from pocketflow.config.settings import get_settings


def test_document_service():
    """Test the document service functionality."""
    print("Testing Document Service...")
    
    # Initialize settings
    settings = get_settings()
    print(f"Content output directory: {settings.CONTENT_OUTPUT_DIR}")
    
    # Create document service
    doc_service = DocumentService()
    
    # Test different document types
    test_cases = [
        {
            "prompt": "Create a business report about the impact of AI on the software industry",
            "expected_type": "business_report"
        },
        {
            "prompt": "Generate a technical report on machine learning algorithms",
            "expected_type": "technical_report"
        },
        {
            "prompt": "Write a report about climate change",
            "expected_type": "report"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Prompt: {test_case['prompt']}")
        print(f"Expected type: {test_case['expected_type']}")
        
        # Create content request
        request = ContentGenerationRequest(
            content_type=ContentType.DOCUMENT,
            prompt=test_case['prompt'],
            duration=None
        )
        
        # Generate document
        try:
            pdf_path = doc_service.generate_document(request)
            
            if pdf_path and os.path.exists(pdf_path):
                print(f"✅ Document generated successfully: {pdf_path}")
                print(f"   File size: {os.path.getsize(pdf_path)} bytes")
            else:
                print("❌ Document generation failed")
                
        except Exception as e:
            print(f"❌ Error generating document: {e}")
    
    print("\n--- Document Service Test Complete ---")


def test_content_service_integration():
    """Test the integration with the content service."""
    print("\nTesting Content Service Integration...")
    
    from pocketflow.services.content_service import ContentService
    
    content_service = ContentService()
    
    # Test document generation through content service
    request = ContentGenerationRequest(
        content_type=ContentType.DOCUMENT,
        prompt="Create a comprehensive report about renewable energy sources",
        duration=None
    )
    
    try:
        pdf_path = content_service.generate_content(request)
        
        if pdf_path and os.path.exists(pdf_path):
            print(f"✅ Content service document generation successful: {pdf_path}")
            print(f"   File size: {os.path.getsize(pdf_path)} bytes")
        else:
            print("❌ Content service document generation failed")
            
    except Exception as e:
        print(f"❌ Error in content service integration: {e}")


def check_latex_installation():
    """Check if LaTeX is installed and available."""
    print("\nChecking LaTeX installation...")
    
    try:
        result = subprocess.run(['pdflatex', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ LaTeX (pdflatex) is installed and available")
            print(f"   Version info: {result.stdout.split('\n')[0]}")
        else:
            print("❌ LaTeX (pdflatex) is not available")
            print("   Please install LaTeX to use the document creator")
    except FileNotFoundError:
        print("❌ LaTeX (pdflatex) is not installed")
        print("   Please install LaTeX to use the document creator")
        print("   On Ubuntu/Debian: sudo apt-get install texlive-full")
        print("   On macOS: brew install --cask mactex")
        print("   On Windows: Install MiKTeX or TeX Live")


if __name__ == "__main__":
    import subprocess
    
    print("Document Creator Test Suite")
    print("=" * 50)
    
    # Check LaTeX installation first
    check_latex_installation()
    
    # Test document service
    test_document_service()
    
    # Test content service integration
    test_content_service_integration()
    
    print("\nTest suite completed!") 