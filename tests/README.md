# Email Threading Tests

This directory contains comprehensive tests for the email threading functionality in PocketFlow.

## Test Files

### `test_email_threading.py`
Unit tests for email threading functionality:

- **Empty Subject Threading**: Tests that emails with empty subjects are handled correctly for proper threading
- **Subject with 'Re:' Prefix**: Tests that subjects with existing "Re:" prefixes are cleaned and re-added correctly
- **References Chain Building**: Tests that the References header builds proper chains for multi-reply conversations
- **Message-ID Format**: Tests that Message-IDs are generated with the correct format and domain
- **Error Handling**: Tests graceful handling of missing or invalid data
- **EmailService Integration**: Tests that the EmailService sets all threading headers correctly

### `test_email_integration.py`
Integration tests for the complete email flow:

- **Complete Tokenless Email Flow**: Tests the full flow from receiving an email to sending a threaded reply
- **Complete Regular Email Flow**: Tests the full flow for registered users
- **EmailService Integration**: Tests the EmailService with real threading headers
- **Subject Email Threading**: Tests threading with emails that have subjects
- **Error Handling**: Tests error handling in the complete flow

## Running the Tests

### Prerequisites
```bash
# Activate virtual environment
source venv/bin/activate

# Install pytest (if not already installed)
pip install pytest
```

### Run All Email Tests
```bash
python -m pytest tests/test_email_*.py -v
```

### Run Specific Test Files
```bash
# Run only threading tests
python -m pytest tests/test_email_threading.py -v

# Run only integration tests
python -m pytest tests/test_email_integration.py -v
```

### Run Specific Test Methods
```bash
# Run a specific test method
python -m pytest tests/test_email_threading.py::TestEmailThreading::test_tokenless_send_email_node_empty_subject_threading -v

# Run tests with specific markers
python -m pytest -m threading -v
```

## Test Coverage

The tests cover the following key aspects of email threading:

### Threading Headers
- `In-Reply-To`: Points to the original message ID
- `References`: Builds a chain of message IDs for the conversation
- `Subject`: Handles empty subjects and "Re:" prefixes correctly
- `Message-ID`: Generates unique message IDs with proper format

### Email Nodes
- `TokenlessSendEmailNode`: For non-registered users
- `SendEmailNode`: For registered users
- `EmailService`: Core email sending functionality

### Edge Cases
- Empty subjects (like your original emails)
- Existing "Re:" prefixes in various formats
- Missing message IDs
- Invalid email data
- References chains for multi-reply conversations

## Key Findings

The tests verify that:

1. **Empty subjects are preserved** for proper threading in Gmail
2. **"Re:" prefixes are handled correctly** without duplication
3. **References chains are built properly** for conversation threading
4. **Message-IDs are unique** and use the correct domain
5. **Error handling is graceful** for missing or invalid data

## Configuration

Tests use mock settings and don't require real email credentials. The `pytest.ini` file configures:

- Test discovery patterns
- Verbose output
- Warning suppression
- Custom markers for test organization

## Contributing

When adding new email threading functionality:

1. Add unit tests to `test_email_threading.py`
2. Add integration tests to `test_email_integration.py`
3. Ensure all tests pass before committing
4. Update this README if adding new test categories 