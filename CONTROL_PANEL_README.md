# PocketFlow Control Panel

A web-based control panel for managing users, tokens, Bitcoin addresses, and system configuration for PocketFlow.

## 🚀 Features

### User Management
- **Add Users**: Create new users with email and initial tokens
- **Edit Users**: Modify token balances and user information
- **View Users**: Detailed user information and statistics
- **Delete Users**: Remove users from the system (safety protected)

### System Overview
- **Dashboard**: Real-time system statistics and status
- **User Statistics**: Total users, tokens, and payments
- **System Status**: Service health monitoring
- **Recent Activity**: User activity tracking

### Access Control
- **Greenlist Management**: Manage email/domain whitelist
- **User Types**: Active vs Tokenless user management
- **Token Management**: Add/remove tokens for users

### Bitcoin Integration
- **BTC Address Management**: View user Bitcoin addresses
- **Payment Tracking**: Monitor payment history
- **Transaction Records**: Detailed payment information

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- PocketFlow system installed
- Virtual environment (recommended)

### Quick Start

1. **Navigate to PocketFlow directory**:
   ```bash
   cd /path/to/pocketflow
   ```

2. **Run the control panel**:
   ```bash
   ./run_control_panel.sh
   ```

3. **Access the web interface**:
   ```
   http://localhost:5000/admin
   ```

### Manual Installation

1. **Install dependencies**:
   ```bash
   pip install flask flask-cors
   ```

2. **Set environment variables**:
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
   export CONTROL_PANEL_HOST="0.0.0.0"
   export CONTROL_PANEL_PORT="5000"
   ```

3. **Run the control panel**:
   ```bash
   python control_panel.py
   ```

## 📊 Usage

### Dashboard
The dashboard provides an overview of your PocketFlow system:
- **System Statistics**: Total users, tokens, payments
- **Quick Actions**: Add users, manage greenlist
- **System Status**: Service health indicators
- **Recent Activity**: User activity timeline

### User Management

#### Adding Users
1. Click "Add User" button
2. Enter email address
3. Set initial token amount
4. Add optional notes
5. Click "Create User"

#### Editing Users
1. Find user in the users table
2. Click the edit (pencil) icon
3. Modify token amount
4. Click "Save Changes"

#### Viewing User Details
1. Click the view (eye) icon
2. See detailed user information:
   - Token balance
   - Bitcoin addresses
   - Payment history
   - Account creation date

### Greenlist Management
- **Add Emails**: Whitelist specific email addresses
- **Add Domains**: Whitelist entire domains
- **View Entries**: See all whitelisted entries
- **Remove Entries**: Remove from whitelist

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CONTROL_PANEL_HOST` | `0.0.0.0` | Host to bind to |
| `CONTROL_PANEL_PORT` | `5000` | Port to listen on |
| `CONTROL_PANEL_DEBUG` | `false` | Enable debug mode |

### Example Configuration
```bash
export CONTROL_PANEL_HOST="127.0.0.1"
export CONTROL_PANEL_PORT="8080"
export CONTROL_PANEL_DEBUG="true"
```

## 🔒 Security

### Access Control
- **Local Access**: By default, only accessible from localhost
- **Network Access**: Set `CONTROL_PANEL_HOST="0.0.0.0"` for network access
- **Firewall**: Ensure proper firewall configuration

### User Safety
- **Token Protection**: Cannot reduce tokens below 0 via web interface
- **Deletion Protection**: User deletion requires confirmation
- **Audit Trail**: All actions are logged

## 📱 API Endpoints

### User Management
- `GET /admin/api/users` - List all users
- `POST /admin/users/add` - Create new user
- `POST /admin/users/{email}/edit` - Edit user
- `POST /admin/users/{email}/delete` - Delete user

### System Statistics
- `GET /admin/api/stats` - Get system statistics

### Greenlist Management
- `POST /admin/greenlist/add` - Add to greenlist

## 🎨 Interface Features

### Modern UI
- **Responsive Design**: Works on desktop and mobile
- **Bootstrap 5**: Modern, clean interface
- **Font Awesome**: Professional icons
- **Real-time Updates**: Live statistics and status

### User Experience
- **Intuitive Navigation**: Easy-to-use sidebar
- **Modal Dialogs**: Clean forms and confirmations
- **Loading States**: Visual feedback for actions
- **Error Handling**: Clear error messages

### Data Tables
- **Sortable Columns**: Click headers to sort
- **Search Functionality**: Find users quickly
- **Pagination**: Handle large user lists
- **Responsive Tables**: Mobile-friendly

## 🚨 Troubleshooting

### Common Issues

#### Control Panel Won't Start
```bash
# Check if Flask is installed
python -c "import flask"

# Install if missing
pip install flask flask-cors
```

#### Database Connection Issues
```bash
# Check database path
ls -la data/pocketflow.db

# Recreate if needed
rm data/pocketflow.db
python -c "from src.pocketflow.services.database_service import database_service"
```

#### Permission Issues
```bash
# Make script executable
chmod +x run_control_panel.sh

# Check file permissions
ls -la control_panel.py
```

### Debug Mode
Enable debug mode for detailed error information:
```bash
export CONTROL_PANEL_DEBUG="true"
./run_control_panel.sh
```

### Logs
Check system logs for detailed information:
```bash
# Application logs
tail -f logs/pocketflow.log

# System logs
journalctl -u pocketflow -f
```

## 🔄 Integration

### With PocketFlow System
The control panel integrates seamlessly with the main PocketFlow system:
- **Shared Database**: Uses the same SQLite database
- **Service Integration**: Leverages existing services
- **Configuration**: Uses PocketFlow settings
- **Logging**: Integrated logging system

### Production Deployment
For production use:
1. **Reverse Proxy**: Use nginx or Apache
2. **SSL Certificate**: Enable HTTPS
3. **Authentication**: Add login system
4. **Monitoring**: Set up health checks

## 📈 Future Enhancements

### Planned Features
- **User Authentication**: Login system for admin access
- **Advanced Analytics**: Detailed usage statistics
- **Bulk Operations**: Import/export user data
- **API Documentation**: Swagger/OpenAPI docs
- **Real-time Notifications**: WebSocket updates

### Customization
- **Themes**: Customizable color schemes
- **Plugins**: Extensible functionality
- **Webhooks**: External integrations
- **Export Options**: CSV, JSON, PDF reports

## 🤝 Contributing

### Development Setup
1. Clone the repository
2. Install development dependencies
3. Run in debug mode
4. Make changes and test

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Write docstrings
- Add tests for new features

## 📄 License

This control panel is part of the PocketFlow project and follows the same license terms.

---

**PocketFlow Control Panel** - Manage your PocketFlow system with ease! 🚀 