#!/bin/bash
# Deploy PocketFlow investigation + report workflow

echo "Deploying PocketFlow investigation + report workflow..."

# Copy files to production
sudo cp -r src/ /opt/pocketflow/
sudo cp -r templates/ /opt/pocketflow/
sudo cp -r tests/ /opt/pocketflow/

# Set permissions
sudo chown -R pocketflow:pocketflow /opt/pocketflow/
sudo chmod -R 755 /opt/pocketflow/

# Restart services
sudo systemctl restart pocketflow

echo "Deployment completed successfully!"
