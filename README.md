# PocketFlow

An AI-powered email processing and content generation system with Bitcoin payment integration.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the main application
python main.py

# Start the web control panel
python -m src.pocketflow.web.app

# Run tests
python run_tests.py
```

## 📚 Documentation

All documentation is located in the `docs/` folder:

- **[Documentation Home](docs/index.md)** - Main documentation
- **[Investigation + Report Workflow](docs/README_investigation_report_workflow.md)** - Enhanced workflow documentation
- **[Document Creator](docs/README_document_creator.md)** - LaTeX-based document generation
- **[Test Structure](docs/TEST_STRUCTURE.md)** - Test organization and usage
- **[Deployment Summary](docs/DEPLOYMENT_SUMMARY.md)** - Latest deployment details
- **[Architecture Diagram](docs/architecture_diagram.md)** - System architecture overview

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
├── main.py                      # Main application entry point
├── run_tests.py                 # Test runner
├── deploy.sh                    # Deployment script
├── docs/                        # Documentation
│   ├── index.md                # Main documentation
│   ├── README_*.md             # Feature documentation
│   └── ...                     # Other docs
├── tests/                       # Test files
│   ├── test_*.py               # Test suites
│   └── ...                     # Test fixtures
├── src/pocketflow/             # Main source code
│   ├── core/                   # Core types and models
│   ├── flows/                  # Flow implementations
│   ├── nodes/                  # Node implementations
│   ├── services/               # External service integrations
│   ├── web/                    # Web control panel
│   ├── agents/                 # AI agent implementations
│   ├── config/                 # Configuration management
│   └── utils/                  # Utility functions
├── templates/                   # LaTeX templates
├── data/                        # Database and data files
├── generated/                   # Generated content output
├── config/                      # Configuration files
└── requirements.txt             # Dependencies
```

## 🎯 Key Features

### 🤖 AI-Powered Email Processing
- **Intelligent Email Routing**: Automatically detects and routes emails based on content
- **Token-Based Access Control**: Users require tokens for premium features
- **Bitcoin Payment Integration**: Seamless payment processing for token purchases
- **Multi-Flow Architecture**: Supports different workflows for different user types

### 📧 Email Services
- **Email Monitoring**: Continuous email monitoring and processing
- **Automatic Responses**: AI-generated email responses
- **Thread Management**: Intelligent conversation threading
- **Attachment Handling**: Process and generate attachments

### 🎨 Content Generation
- **Audio Generation**: Create podcasts, songs, and sound content
- **Image Generation**: Generate images from text descriptions
- **Document Creation**: LaTeX-based document generation
- **Multi-format Output**: Support for various content formats

### 🔍 Research & Investigation
- **Web Search Integration**: Automated web research capabilities
- **Topic Investigation**: Deep-dive research workflows
- **Report Generation**: Automated report creation from research

### 💰 Payment System
- **Bitcoin Integration**: Direct Bitcoin payment processing
- **Token Management**: User token tracking and management
- **Payment Verification**: Automated payment confirmation
- **Greenlist System**: Whitelist management for trusted users

### 🖥️ Web Control Panel
- **Admin Dashboard**: Comprehensive system monitoring
- **User Management**: Add, edit, and manage users
- **Payment Tracking**: Monitor Bitcoin transactions
- **System Statistics**: Real-time system metrics

## 🚀 Recent Updates

- ✅ Enhanced investigation + report workflow
- ✅ Professional LaTeX document generation
- ✅ Comprehensive test coverage
- ✅ Automated deployment pipeline
- ✅ Bitcoin payment integration
- ✅ Web control panel
- ✅ Multi-flow architecture
- ✅ Token-based access control

## 🔧 Configuration

The system uses environment variables for configuration. Create a `.env` file with:

```env
# Email Configuration
EMAIL_HOST=your-email-host
EMAIL_PORT=587
EMAIL_USERNAME=your-email
EMAIL_PASSWORD=your-password

# LLM Configuration
OLLAMA_HOST=192.168.1.7
OLLAMA_PORT=11434
OLLAMA_MODEL=llama3:latest

# Bitcoin Configuration
ELECTRUM_HOST=localhost
ELECTRUM_PORT=50001

# Database
DATABASE_URL=sqlite:///pocketflow.db

# Security
SECRET_KEY=your-secret-key
TOKEN_PRICE_USD=0.01
```

## 📖 More Information

For detailed documentation, see the `docs/` folder or visit the [main documentation](docs/index.md).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python run_tests.py`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 