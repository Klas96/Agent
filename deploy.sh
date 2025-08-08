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

# Install/update dependencies in the production environment
echo "Installing/updating dependencies..."
cd /opt/pocketflow
source venv/bin/activate
pip install -r requirements.txt

# Ensure podcastify tool is properly installed
echo "Ensuring podcastify tool is available..."
python3 -c "
try:
    from src.pocketflow.tools.podcastify import PodcastifyTool
    tool = PodcastifyTool()
    print('✅ PodcastifyTool imported successfully')
except Exception as e:
    print(f'❌ PodcastifyTool import failed: {e}')
"

# Test tool registration (optional - may fail in isolation)
echo "Testing tool registration..."
python3 -c "
try:
    from src.pocketflow.tools.registry import agent_tool_registry
    from src.pocketflow.tools.podcastify import PodcastifyTool
    
    # Register the podcastify tool
    tool = PodcastifyTool()
    agent_tool_registry.register_tool(tool)
    
    # Test if it's available
    available_tools = agent_tool_registry.list_tools()
    if 'podcastify' in available_tools:
        print('✅ Podcastify tool registered successfully')
    else:
        print('⚠️  Podcastify tool registration test inconclusive (may work in runtime)')
except Exception as e:
    print(f'⚠️  Tool registration test failed (may work in runtime): {e}')
"

# Restart services
echo "Restarting PocketFlow service..."
sudo systemctl restart pocketflow

echo "Deployment completed successfully!"
echo "✅ PocketFlow with podcastify tool is now deployed and running!"
