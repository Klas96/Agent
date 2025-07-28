# Current Features Test Suite

This directory contains comprehensive tests for all current PocketFlow features. The tests are designed to verify that all core functionality is working correctly.

## Test Files

### `test_current_features.py`
Comprehensive unit tests for all current features:

- **Core Abstractions**: Tests Node and Flow base classes
- **Flow Manager**: Tests flow selection and management
- **Services**: Tests all service classes (Email, LLM, Content, etc.)
- **Flows**: Tests all available flows (Email Processing, Content Generation, etc.)
- **Nodes**: Tests all available nodes
- **Email Functionality**: Tests email threading and processing
- ✅ Email threading (In-Reply-To, References headers)
- ✅ Email sending with proper headers
- ✅ Tokenless user email handling
- ✅ Tokened user email handling

### `test_current_features_runner.py`
Dedicated test runner with detailed reporting:

- **Feature Status Tracking**: Tracks which features are working
- **Comprehensive Reporting**: Provides detailed status reports
- **Category Grouping**: Groups features by type (Core, Flows, Services, etc.)
- **Success Rate Calculation**: Shows overall system health

## Current Features Tested

### Core Features
- ✅ Node abstraction (pocketflow.Node)
- ✅ Flow abstraction (pocketflow.Flow)
- ✅ Shared state management
- ✅ Flow routing and transitions

### Email Processing
- ✅ Email fetching and processing
- ✅ Email threading (In-Reply-To, References headers)
- ✅ Email sending with proper headers
- ✅ Tokenless user email handling
- ✅ Tokened user email handling

### Content Generation
- ✅ Music generation
- ✅ Document creation (PDF, DOCX, TXT, MD)
- ✅ Image generation
- ✅ Text content creation
- ✅ Content parameter handling

### Investigation & Research
- ✅ Web search functionality
- ✅ Research topic investigation
- ✅ Information gathering
- ✅ Search result processing

### Payment Processing
- ✅ Bitcoin address generation
- ✅ Bitcoin price fetching
- ✅ Payment calculation
- ✅ Token management
- ✅ User balance tracking

### Services
- ✅ EmailService - Email processing and threading
- ✅ LLMService - Language model interactions
- ✅ ContentService - Content generation
- ✅ DocumentService - Document creation and management
- ✅ BitcoinService - Bitcoin payment processing
- ✅ WebSearchService - Web search and research
- ✅ DatabaseService - User and data management

### Flows
- ✅ Email Processor Flow - Full email processing
- ✅ Tokenless User Flow - New user handling
- ✅ Content Generation Flow - Specialized content creation
- ✅ Investigation Flow - Research and investigation
- ✅ Payment Processing Flow - Payment handling

## Running the Tests

### Quick Test (Recommended)
```bash
# From project root
./test_current_features.sh
```

### Detailed Test Suite
```bash
# Run comprehensive test suite
python tests/test_current_features_runner.py

# Run unit tests with pytest
python -m pytest tests/test_current_features.py -v

# Run specific test categories
python -m pytest tests/test_current_features.py::TestCurrentFeatures::test_email_service_functionality -v
```

### Individual Feature Tests
```bash
# Test email functionality
python tests/test_email_integration.py

# Test Bitcoin functionality
python tests/test_btc_functionality.py

# Test document service
python tests/test_document_service_simple.py
```

## Test Results Interpretation

### Feature Status Report
The test runner provides a detailed report showing:

```
📊 Current Features Status Report
============================================================

Core Features:
  ✅ core_node
  ✅ core_flow

Flows:
  ✅ flow_email_processor
  ✅ flow_tokenless_user
  ✅ flow_content_generation
  ✅ flow_investigation
  ✅ flow_payment_processing

Services:
  ✅ email_service
  ✅ llm_service
  ✅ content_service
  ✅ document_service
  ✅ bitcoin_service
  ✅ websearch_service
  ✅ database_service

🎯 Overall Status: 15/15 features working (100.0%)
🎉 Excellent! Most features are working correctly.
```

### Success Rate Categories
- **90%+**: Excellent - Most features working correctly
- **70-89%**: Good - Most core features working
- **50-69%**: Fair - Some features need attention
- **<50%**: Poor - Many features need fixing

## Test Categories

### Unit Tests
- Individual component testing
- Mocked external dependencies
- Fast execution
- Detailed error reporting

### Integration Tests
- End-to-end flow testing
- Real service interactions
- Complete workflow validation
- Error handling verification

### Feature Tests
- Specific feature validation
- User scenario testing
- Performance verification
- Edge case handling

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure you're in the project root
   cd /path/to/PocketFlow
   
   # Activate virtual environment
   source venv/bin/activate
   ```

2. **Missing Dependencies**
   ```bash
   # Install requirements
   pip install -r requirements.txt
   ```

3. **Configuration Issues**
   ```bash
   # Check environment variables
   python tests/test_app.py
   ```

4. **Service Connection Issues**
   ```bash
   # Test individual services
   python tests/test_ollama_setup.py
   python tests/test_email_config.py
   ```

### Debug Mode
```bash
# Run with verbose output
python tests/test_current_features_runner.py --verbose

# Run specific test with debug
python -m pytest tests/test_current_features.py::TestCurrentFeatures::test_email_service_functionality -v -s
```

## Contributing

When adding new features:

1. **Add Unit Tests**: Create tests in `test_current_features.py`
2. **Update Runner**: Add feature tests to `test_current_features_runner.py`
3. **Update Documentation**: Document new features here
4. **Test Integration**: Ensure new features work with existing flows

### Test Naming Convention
- `test_[feature_name]_functionality` - Core feature tests
- `test_[service_name]_service` - Service-specific tests
- `test_[flow_name]_flow` - Flow-specific tests
- `test_[integration_name]_integration` - Integration tests

## Continuous Integration

The current features test suite is designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Test Current Features
  run: |
    python tests/test_current_features_runner.py
    python -m pytest tests/test_current_features.py -v
```

## Performance Metrics

The test suite tracks:
- **Test Execution Time**: How long tests take to run
- **Feature Coverage**: Percentage of features tested
- **Success Rate**: Percentage of tests passing
- **Error Categories**: Types of failures encountered

## Maintenance

### Regular Updates
- Update tests when adding new features
- Review test coverage quarterly
- Update documentation with new features
- Monitor test performance and reliability

### Test Data
- Use realistic test data
- Avoid hardcoded credentials
- Mock external services appropriately
- Clean up test artifacts

---

For more information about specific features, see the main documentation in `docs/`. 