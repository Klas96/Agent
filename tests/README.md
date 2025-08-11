# PocketFlow Tests

This directory contains comprehensive tests for the PocketFlow application, including database migration tests, PostgreSQL connectivity tests, and dashboard functionality tests.

## Test Files

### `test_postgresql.py`
Tests PostgreSQL database connectivity and basic operations:
- ✅ PostgreSQL connection and version check
- ✅ Table existence verification
- ✅ Basic CRUD operations
- ✅ DatabaseService integration

### `test_migration.py`
Tests database migration from SQLite to PostgreSQL:
- ✅ SQLite database structure and data verification
- ✅ PostgreSQL database structure and data verification
- ✅ Data integrity checks
- ✅ Database compatibility testing

### `test_dashboard.py`
Tests the dashboard application functionality:
- ✅ Dashboard import and app creation
- ✅ Route registration and accessibility
- ✅ Database integration
- ✅ API endpoint verification

### `run_tests.py`
Test runner script that executes all tests and provides a comprehensive summary.

## Running Tests

### Run All Tests
```bash
python3 tests/run_tests.py
```

### Run Individual Tests
```bash
# PostgreSQL tests
python3 tests/test_postgresql.py

# Migration tests
python3 tests/test_migration.py

# Dashboard tests
python3 tests/test_dashboard.py
```

## Test Environment

The tests automatically set up the required environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `EMAIL_HOST`: Localhost for testing
- `EMAIL_USERNAME`: Test email
- `EMAIL_PASSWORD`: Test password

## Test Results

### Expected Output
```
🧪 PocketFlow Test Suite
============================================================

============================================================
Running test_postgresql.py...
============================================================
✓ Connected to PostgreSQL successfully
✓ PostgreSQL version: PostgreSQL 16.9...
✓ Found tables: ['greenlist', 'job_executions', 'scheduled_jobs', 'users']
✓ Successfully created and read user: test@example.com (Test User)
✓ PostgreSQL test completed successfully!
✓ DatabaseService initialized successfully
✓ Retrieved 2 users from database
✓ Retrieved 0 scheduled jobs
✓ DatabaseService test completed successfully!

🎉 All tests passed!

============================================================
📊 Test Results Summary
============================================================
test_postgresql.py: ✅ PASSED
test_migration.py: ✅ PASSED
test_dashboard.py: ✅ PASSED

============================================================
🎉 All tests passed!
```

## Test Coverage

### Database Tests
- ✅ PostgreSQL connectivity
- ✅ Table creation and structure
- ✅ Data insertion and retrieval
- ✅ DatabaseService functionality
- ✅ Migration compatibility

### Dashboard Tests
- ✅ Flask app creation
- ✅ Route registration
- ✅ API endpoints
- ✅ Database integration
- ✅ Import path resolution

### Migration Tests
- ✅ SQLite to PostgreSQL migration
- ✅ Data integrity verification
- ✅ Schema compatibility
- ✅ Service compatibility

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running tests from the project root directory
2. **Database Connection**: Verify PostgreSQL is running and accessible
3. **Environment Variables**: Tests automatically set required environment variables
4. **Path Issues**: Tests handle both development and production paths

### Debug Mode
To run tests with more verbose output, modify the test runner to include debug information.

## Adding New Tests

1. Create a new test file in the `tests/` directory
2. Follow the naming convention: `test_*.py`
3. Include proper error handling and clear success/failure messages
4. Add the test file to the list in `run_tests.py`
5. Ensure tests are executable: `chmod +x tests/test_*.py`

## Test Dependencies

- `psycopg2-binary`: PostgreSQL adapter
- `sqlite3`: Built-in SQLite support
- `pocketflow`: Main application package
- `flask`: Dashboard framework

## Continuous Integration

These tests can be integrated into CI/CD pipelines to ensure:
- Database migrations work correctly
- PostgreSQL connectivity is maintained
- Dashboard functionality is preserved
- No regressions are introduced 