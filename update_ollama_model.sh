#!/bin/bash
# Update OLLAMA_MODEL in production .env file

set -e

echo "Updating OLLAMA_MODEL in production .env..."

# Update production .env
sudo sed -i 's/OLLAMA_MODEL=llama3.1/OLLAMA_MODEL=llama3:latest/' /opt/pocketflow/.env

echo "✅ Updated /opt/pocketflow/.env"
echo ""
echo "Current setting:"
grep OLLAMA_MODEL /opt/pocketflow/.env

echo ""
echo "⚠️  You may need to restart the pocketflow service for the change to take effect:"
echo "   sudo systemctl restart pocketflow"
