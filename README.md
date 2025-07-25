# PocketFlow

A minimalist LLM framework for Agents, Task Decomposition, RAG, and more.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python run_tests.py

# Start the application
python -m pocketflow.web.app
```

## 📚 Documentation

All documentation is located in the `docs/` folder:

- **[Documentation Home](docs/index.md)** - Main documentation
- **[Investigation + Report Workflow](docs/README_investigation_report_workflow.md)** - Enhanced workflow documentation
- **[Document Creator](docs/README_document_creator.md)** - LaTeX-based document generation
- **[Test Structure](docs/TEST_STRUCTURE.md)** - Test organization and usage
- **[Deployment Summary](docs/DEPLOYMENT_SUMMARY.md)** - Latest deployment details

## 🧪 Testing

```bash
# Run all tests and deploy if successful
python run_tests.py

# Run specific test suite
python -m unittest tests.test_investigation_report_workflow_simple -v
```

## 📁 Project Structure

```
PocketFlow/
├── README.md                    # This file
├── run_tests.py                 # Test runner
├── deploy.sh                    # Deployment script
├── docs/                        # Documentation
│   ├── index.md                # Main documentation
│   ├── README_*.md             # Feature documentation
│   └── ...                     # Other docs
├── tests/                       # Test files
│   ├── test_*.py               # Test suites
│   └── ...                     # Test fixtures
├── src/                         # Source code
│   └── pocketflow/             # Main package
├── templates/                   # LaTeX templates
└── requirements.txt             # Dependencies
```

## 🎯 Key Features

- **Investigation + Report Workflow**: Two-step process for research-based document generation
- **LaTeX Document Generation**: Professional PDF output with templates
- **Intelligent Agent Routing**: Automatic workflow detection
- **Comprehensive Testing**: 100% test success rate with automated deployment

## 🚀 Recent Updates

- ✅ Enhanced investigation + report workflow
- ✅ Professional LaTeX document generation
- ✅ Comprehensive test coverage
- ✅ Automated deployment pipeline
- ✅ Clean project organization

## 📖 More Information

For detailed documentation, see the `docs/` folder or visit the [main documentation](docs/index.md). 