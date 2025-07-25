#!/bin/bash
# Install LaTeX dependencies for document creator

echo "Installing LaTeX dependencies for PocketFlow Document Creator..."

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v apt-get &> /dev/null; then
        echo "Installing LaTeX on Ubuntu/Debian..."
        sudo apt-get update
        sudo apt-get install -y texlive-full
    elif command -v yum &> /dev/null; then
        echo "Installing LaTeX on CentOS/RHEL..."
        sudo yum install -y texlive-scheme-full
    elif command -v pacman &> /dev/null; then
        echo "Installing LaTeX on Arch Linux..."
        sudo pacman -S --noconfirm texlive-most
    else
        echo "Unsupported Linux distribution. Please install LaTeX manually."
        exit 1
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "Installing LaTeX on macOS..."
    if command -v brew &> /dev/null; then
        brew install --cask mactex
    else
        echo "Homebrew not found. Please install Homebrew first or install LaTeX manually."
        exit 1
    fi
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    # Windows
    echo "For Windows, please install MiKTeX or TeX Live manually:"
    echo "  - MiKTeX: https://miktex.org/download"
    echo "  - TeX Live: https://www.tug.org/texlive/"
    exit 1
else
    echo "Unsupported operating system. Please install LaTeX manually."
    exit 1
fi

echo "LaTeX installation completed!"
echo "You can now use the document creator to generate PDF reports."

# Test LaTeX installation
echo "Testing LaTeX installation..."
if command -v pdflatex &> /dev/null; then
    echo "✅ LaTeX (pdflatex) is now available"
    pdflatex --version | head -1
else
    echo "❌ LaTeX installation may have failed. Please check manually."
fi 