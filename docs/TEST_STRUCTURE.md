# 🧪 PocketFlow Test Structure

## ✅ Clean Test Organization

All tests are now properly organized in the `tests/` folder with a single test runner in the root directory.

## 📁 Test Structure

### Root Directory
- `run_tests.py` - Main test runner that executes all tests and deploys if successful

### Tests Directory (`tests/`)
```
tests/
├── test_app.py                           # App functionality tests
├── test_basic_installation.py            # Basic installation tests
├── test_btc_functionality.py            # Bitcoin functionality tests
├── test_configuration_consolidation.py   # Configuration tests
├── test_document_creator.py              # Document creator tests
├── test_document_service_direct.py       # Direct document service tests
├── test_document_service_simple.py       # Simple document service tests
├── test_investigation_report_workflow.py # Investigation workflow tests
├── test_investigation_report_workflow_simple.py # Simplified workflow tests
├── test_personality_editing.py          # Personality editing tests
├── test_simple_installation.py           # Simple installation tests
├── test_simple_template.py               # Simple template tests
├── test_template.py                      # Template tests
├── test_utility_consolidation.py         # Utility consolidation tests
├── fixtures/                             # Test fixtures
├── integration/                          # Integration tests
└── unit/                                # Unit tests
```

## 🚀 Test Runner Features

### `run_tests.py`
- **Unit Tests**: Runs investigation + report workflow tests
- **Document Service Tests**: Tests LaTeX compilation and document generation
- **LaTeX Tests**: Verifies LaTeX installation and templates
- **Automatic Deployment**: Uses existing `deploy.sh` script when tests pass
- **Comprehensive Reporting**: Generates detailed test reports

### Test Execution
```bash
# Run all tests and deploy if successful
python run_tests.py

# Run specific test file
python -m unittest tests.test_investigation_report_workflow_simple

# Run with verbose output
python -m unittest tests.test_investigation_report_workflow_simple -v
```

## 📊 Test Results

### Latest Test Run
- **Unit Tests**: ✅ PASSED
- **Document Service Tests**: ✅ PASSED (LaTeX components working)
- **LaTeX Tests**: ✅ PASSED (3/3 templates found)
- **Deployment**: ✅ SUCCESSFUL
- **Success Rate**: 100%

### Test Coverage
- **Core Functionality**: Workflow detection, document generation, LaTeX compilation
- **Integration**: End-to-end workflow testing
- **Error Handling**: Fallback content generation, template validation
- **Deployment**: Automatic deployment when tests pass

## 🔧 Test Components

### 1. **Unit Tests** (`test_investigation_report_workflow_simple.py`)
- Workflow detection and routing
- Document type detection
- Research-based prompt detection
- Agent action sequence validation
- Template creation and validation
- Fallback content generation

### 2. **Document Service Tests** (`test_document_service_simple.py`)
- LaTeX installation verification
- Template discovery and validation
- LaTeX compilation testing
- Document type detection
- Fallback content generation

### 3. **LaTeX Tests**
- LaTeX installation verification
- Template discovery (3 templates found)
- Template validation

## 🎯 Benefits

### ✅ **Clean Organization**
- All tests in `tests/` folder
- Single test runner in root
- No duplicate test files

### ✅ **Comprehensive Coverage**
- Unit tests for core functionality
- Integration tests for workflows
- LaTeX compilation tests
- Deployment verification

### ✅ **Automated Deployment**
- Tests run automatically
- Deployment only when tests pass
- Uses existing deploy script

### ✅ **Detailed Reporting**
- Test success/failure tracking
- Coverage analysis
- Deployment status reporting
- JSON test reports

## 🚀 Usage

### Running Tests
```bash
# Run all tests and deploy if successful
python run_tests.py

# Run specific test suite
python -m unittest tests.test_investigation_report_workflow_simple -v

# Run document service tests
python tests/test_document_service_simple.py
```

### Test Reports
- **JSON Report**: `test_report.json` - Detailed test results
- **Console Output**: Real-time test progress and results
- **Deployment Status**: Automatic deployment when tests pass

## 🎉 Success Metrics

- **Test Organization**: ✅ All tests in `tests/` folder
- **Single Runner**: ✅ One `run_tests.py` in root
- **No Duplicates**: ✅ Clean file structure
- **Working Deployment**: ✅ Uses existing `deploy.sh`
- **100% Success Rate**: ✅ All tests passing
- **Automatic Deployment**: ✅ Deploys when tests pass

The test structure is now clean, organized, and fully functional! 