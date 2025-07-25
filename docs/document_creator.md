# Document Creator

The Document Creator is a LaTeX-based PDF generation system that creates professional reports and documents. It's integrated into the content creation path and can generate different types of reports based on user requests.

## Features

- **LaTeX Templates**: Professional PDF generation using LaTeX templates
- **Multiple Document Types**: Support for different report types
- **Intelligent Content Generation**: Uses LLM to generate structured content
- **Automatic Type Detection**: Determines document type based on user prompt
- **Clean PDF Output**: Professional formatting with proper sections and styling

## Supported Document Types

### 1. Business Report
- **Trigger Keywords**: business, financial, market, company, executive
- **Structure**: Executive Summary, Introduction, Analysis, Recommendations, Conclusion
- **Use Case**: Business analysis, market research, financial reports

### 2. Technical Report
- **Trigger Keywords**: technical, research, analysis, data, methodology
- **Structure**: Introduction, Methodology, Results, Discussion, Conclusion
- **Use Case**: Technical documentation, research papers, data analysis

### 3. General Report
- **Default Type**: Used when no specific type is detected
- **Structure**: Abstract, Main Content, Summary
- **Use Case**: General reports, articles, summaries

## Usage

### Through Email Interface
Users can request documents by sending emails with prompts like:
- "Create a business report about AI in healthcare"
- "Generate a technical report on renewable energy"
- "Write a report about climate change"

### Through API
```python
from pocketflow.core.types import ContentGenerationRequest, ContentType

request = ContentGenerationRequest(
    content_type=ContentType.DOCUMENT,
    prompt="Create a business report about market trends",
    duration=None
)

from pocketflow.services.document_service import DocumentService
doc_service = DocumentService()
pdf_path = doc_service.generate_document(request)
```

## Architecture

### Components

1. **DocumentService** (`src/pocketflow/services/document_service.py`)
   - Main service for PDF generation
   - Manages LaTeX templates
   - Handles content generation and compilation

2. **DocumentGeneratorNode** (`src/pocketflow/nodes/content/document_generator.py`)
   - Specialized node for document generation
   - Integrates with content generation flow
   - Handles routing and error management

3. **LaTeX Templates** (`templates/latex/`)
   - Professional templates for different document types
   - Consistent styling and formatting
   - Easy to customize and extend

### Flow Integration

The document creator is integrated into the content generation flow:

```
ConversationContext → Agent → ContentCreator → ContentParams → 
GenerateContent → DocumentGenerator → SendEmail
```

## Installation

### Prerequisites

1. **LaTeX Installation**
   ```bash
   # Run the installation script
   ./install_latex.sh
   
   # Or install manually:
   # Ubuntu/Debian: sudo apt-get install texlive-full
   # macOS: brew install --cask mactex
   # Windows: Install MiKTeX or TeX Live
   ```

2. **Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Testing

Run the test suite to verify functionality:
```bash
python test_document_creator.py
```

## Configuration

### Output Directory
Documents are generated in the configured content output directory:
```python
# In settings
CONTENT_OUTPUT_DIR = "./generated"
```

### Template Customization
LaTeX templates can be customized by editing files in `templates/latex/`:
- `report.tex` - General report template
- `business_report.tex` - Business report template
- `technical_report.tex` - Technical report template

## Error Handling

The document creator includes robust error handling:

1. **LaTeX Compilation Errors**: Logged and handled gracefully
2. **LLM Generation Failures**: Fallback content generation
3. **Template Errors**: Default template usage
4. **File System Issues**: Proper cleanup and error reporting

## Performance Considerations

- **LaTeX Compilation**: Can take 5-15 seconds depending on document complexity
- **LLM Generation**: Depends on content length and complexity
- **File Cleanup**: Automatic cleanup of auxiliary LaTeX files
- **Caching**: Consider implementing caching for repeated requests

## Future Enhancements

1. **Additional Templates**: More document types (proposals, manuals, etc.)
2. **Custom Styling**: User-configurable document styles
3. **Image Support**: Integration of charts and diagrams
4. **Multi-language**: Support for different languages
5. **Template Variables**: More flexible content substitution
6. **Batch Processing**: Generate multiple documents simultaneously

## Troubleshooting

### Common Issues

1. **LaTeX Not Found**
   ```
   Error: pdflatex command not found
   Solution: Install LaTeX using install_latex.sh
   ```

2. **Compilation Errors**
   ```
   Error: LaTeX compilation failed
   Solution: Check LaTeX installation and template syntax
   ```

3. **Content Generation Failures**
   ```
   Error: LLM call failed
   Solution: Check LLM service configuration and connectivity
   ```

### Debug Mode

Enable debug logging to troubleshoot issues:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Examples

### Business Report Example
**Prompt**: "Create a business report about the impact of AI on the software industry"

**Generated Structure**:
- Executive Summary
- Introduction
- Analysis of AI adoption trends
- Recommendations for companies
- Conclusion

### Technical Report Example
**Prompt**: "Generate a technical report on machine learning algorithms"

**Generated Structure**:
- Introduction to ML algorithms
- Methodology for analysis
- Results and performance metrics
- Discussion of findings
- Conclusion and future work 