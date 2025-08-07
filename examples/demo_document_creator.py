#!/usr/bin/env python3
"""
Demonstration of the Document Creator functionality.

This script shows how the LaTeX-based document generation works.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def create_simple_document():
    """Create a simple document using the document service."""
    print("Creating a simple document...")
    
    try:
        # Import the document service directly
        from pocketflow.services.document_service import DocumentService
        
        # Create document service
        doc_service = DocumentService()
        
        # Create a mock content request
        class MockContentRequest:
            def __init__(self, prompt):
                self.prompt = prompt
                self.content_type = "document"
                self.duration = None
        
        # Test different document types
        test_cases = [
            {
                "prompt": "Create a business report about the impact of AI on the software industry",
                "type": "business_report",
                "description": "Business Report"
            },
            {
                "prompt": "Generate a technical report on machine learning algorithms and their applications",
                "type": "technical_report", 
                "description": "Technical Report"
            },
            {
                "prompt": "Write a comprehensive report about climate change and renewable energy solutions",
                "type": "report",
                "description": "General Report"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- Test Case {i}: {test_case['description']} ---")
            print(f"Prompt: {test_case['prompt']}")
            
            # Create request
            request = MockContentRequest(test_case['prompt'])
            
            # Generate document
            pdf_path = doc_service.generate_document(request)
            
            if pdf_path and os.path.exists(pdf_path):
                print(f"✅ Document generated successfully!")
                print(f"   PDF: {pdf_path}")
                print(f"   Size: {os.path.getsize(pdf_path)} bytes")
                
                # Check document type detection
                detected_type = doc_service._determine_document_type(test_case['prompt'])
                print(f"   Detected type: {detected_type}")
                print(f"   Expected type: {test_case['type']}")
                
                if detected_type == test_case['type']:
                    print("   ✅ Type detection correct")
                else:
                    print("   ❌ Type detection incorrect")
                    
            else:
                print("❌ Document generation failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating document: {e}")
        return False

def show_template_info():
    """Show information about available templates."""
    print("\n" + "=" * 50)
    print("Available LaTeX Templates")
    print("=" * 50)
    
    templates_dir = Path("templates/latex")
    if templates_dir.exists():
        template_files = list(templates_dir.glob("*.tex"))
        
        for template in template_files:
            print(f"\n📄 {template.name}")
            
            # Read template content to show structure
            with open(template, 'r') as f:
                content = f.read()
                
            if "business_report" in template.name:
                print("   Type: Business Report")
                print("   Sections: Executive Summary, Introduction, Analysis, Recommendations, Conclusion")
            elif "technical_report" in template.name:
                print("   Type: Technical Report") 
                print("   Sections: Introduction, Methodology, Results, Discussion, Conclusion")
            else:
                print("   Type: General Report")
                print("   Sections: Abstract, Main Content, Summary")
            
            print(f"   Size: {os.path.getsize(template)} bytes")
    else:
        print("❌ Templates directory not found")

def show_usage_examples():
    """Show usage examples for the document creator."""
    print("\n" + "=" * 50)
    print("Usage Examples")
    print("=" * 50)
    
    examples = [
        {
            "type": "Business Report",
            "prompt": "Create a business report about the impact of AI on the software industry",
            "keywords": "business, financial, market, company, executive"
        },
        {
            "type": "Technical Report", 
            "prompt": "Generate a technical report on machine learning algorithms",
            "keywords": "technical, research, analysis, data, methodology"
        },
        {
            "type": "General Report",
            "prompt": "Write a report about climate change and renewable energy",
            "keywords": "general topics, no specific keywords"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['type']}")
        print(f"   Prompt: {example['prompt']}")
        print(f"   Keywords: {example['keywords']}")

def main():
    """Main demonstration function."""
    print("Document Creator Demonstration")
    print("=" * 50)
    
    # Show template information
    show_template_info()
    
    # Show usage examples
    show_usage_examples()
    
    # Create sample documents
    print("\n" + "=" * 50)
    print("Creating Sample Documents")
    print("=" * 50)
    
    success = create_simple_document()
    
    if success:
        print("\n🎉 Document creator demonstration completed successfully!")
        print("\nThe document creator is now ready to be integrated into the content generation flow.")
        print("Users can request documents by sending emails with prompts like:")
        print("- 'Create a business report about AI in healthcare'")
        print("- 'Generate a technical report on renewable energy'") 
        print("- 'Write a report about climate change'")
    else:
        print("\n❌ Document creator demonstration failed.")
        print("Please check the error messages above.")

if __name__ == "__main__":
    main() 