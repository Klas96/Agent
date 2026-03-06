# Email Agent Deployment Instructions

## Quick Deploy

To deploy the email agent to production, run:

```bash
cd /home/klas/EmailAgent1
sudo ./deploy.sh
```

## What the Deployment Script Does

The `deploy.sh` script will:

1. **Backup existing data** - Creates a timestamped backup of the data directory
2. **Copy application files**:
   - `src/` - Source code
   - `templates/` - Template files
   - `config/` - Configuration files
   - `utils/` - Utility functions
   - `main.py` - Main entry point
   - `requirements.txt` - Python dependencies
   - `run_app.sh` - Startup script

3. **Update dependencies** - Installs/updates Python packages in the production virtual environment

4. **Verify installation** - Tests that core imports work correctly

5. **Restart services** - Restarts the PocketFlow service

## First-Time Installation

If this is the first time deploying, you may need to run the system installation first:

```bash
sudo ./install-system.sh
```

This will:
- Create the service user (`pocketflow`)
- Set up the production directory (`/opt/pocketflow`)
- Create the virtual environment
- Install system dependencies
- Create systemd service files
- Enable the service

## Service Management

After deployment, you can manage the services using:

```bash
# Check status
sudo ./manage_services.sh status

# Start services
sudo ./manage_services.sh start

# Stop services
sudo ./manage_services.sh stop

# Restart services
sudo ./manage_services.sh restart

# View logs
sudo ./manage_services.sh logs

# Check health
sudo ./manage_services.sh health
```

## Manual Service Commands

```bash
# Check service status
sudo systemctl status pocketflow

# View logs
sudo journalctl -u pocketflow -f

# Restart service
sudo systemctl restart pocketflow

# Enable on boot
sudo systemctl enable pocketflow
```

## Troubleshooting

### Service not found
If you get "service not found" errors, run the installation script first:
```bash
sudo ./install-system.sh
```

### Permission errors
Make sure the script is executable:
```bash
chmod +x deploy.sh
```

### Import errors after deployment
Check that dependencies are installed:
```bash
cd /opt/pocketflow
source venv/bin/activate
pip install -r requirements.txt
```

### Check logs for errors
```bash
sudo journalctl -u pocketflow -n 100
```

## Production Directory Structure

```
/opt/pocketflow/
├── src/              # Source code
├── templates/        # Templates
├── config/           # Configuration files
├── data/             # Database and data files
├── venv/             # Python virtual environment
├── main.py           # Main entry point
├── run_app.sh        # Startup script
└── requirements.txt  # Dependencies
```

## Environment Configuration

Make sure `/opt/pocketflow/.env` exists with your configuration:

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

# Database
DATABASE_URL=sqlite:///pocketflow.db
```

## Verification

After deployment, verify everything is working:

1. Check service status:
   ```bash
   sudo systemctl status pocketflow
   ```

2. Check logs for errors:
   ```bash
   sudo journalctl -u pocketflow -n 50
   ```


4. Verify imports:
   ```bash
   sudo -u pocketflow /opt/pocketflow/venv/bin/python -c "from src.pocketflow import flow_manager; print('OK')"
   ```
