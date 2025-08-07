#!/bin/bash

# Test Current Features Script for PocketFlow
# This script runs comprehensive tests on all current features

echo "🧪 PocketFlow Current Features Test Suite"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the PocketFlow project root directory"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: Virtual environment not detected"
    echo "   Consider activating your virtual environment first"
    echo ""
fi

# Run the comprehensive test suite
echo "🔍 Running comprehensive current features test..."
echo ""

# Run the test runner
python3 tests/test_current_features_runner.py

# Check the exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Current features test completed successfully!"
    echo ""
    echo "📋 Summary:"
    echo "   - All core features tested"
    echo "   - Service availability verified"
    echo "   - Flow functionality checked"
    echo "   - Node availability confirmed"
    echo ""
    echo "🎉 PocketFlow is ready for use!"
else
    echo ""
    echo "❌ Some tests failed. Please check the output above."
    echo ""
    echo "🔧 Troubleshooting tips:"
    echo "   - Check that all dependencies are installed"
    echo "   - Verify that configuration files are set up"
    echo "   - Ensure services are running (if applicable)"
    echo "   - Review the test output for specific errors"
    echo ""
    exit 1
fi

echo ""
echo "📚 For more detailed testing, you can also run:"
echo "   python3 tests/test_current_features.py"
echo "   python3 -m pytest tests/test_current_features.py -v"
echo "" 