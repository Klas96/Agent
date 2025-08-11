# PostgreSQL Migration Guide

## Overview

This document describes the successful migration from SQLite to PostgreSQL for the PocketFlow application.

## Migration Summary

### ✅ **Completed Successfully**

1. **PostgreSQL Installation & Setup**
   - Installed PostgreSQL 16.9 on Ubuntu
   - Created `pocketflow` database
   - Created `pocketflow` user with password `pocketflow_password`
   - Granted necessary permissions

2. **Database Schema Migration**
   - Created tables: `users`, `scheduled_jobs`, `job_executions`, `greenlist`
   - Migrated existing data from SQLite (0 users, 0 greenlist entries)
   - All tables created with proper PostgreSQL syntax

3. **Application Updates**
   - Updated `DatabaseService` to support both SQLite and PostgreSQL
   - Added `psycopg2-binary` dependency
   - Updated default `DATABASE_URL` to use PostgreSQL
   - Modified service files to include PostgreSQL environment variable

4. **Service Configuration**
   - Updated both `pocketflow.service` and `dashboard.service`
   - Added `DATABASE_URL` environment variable
   - Services successfully restarted with PostgreSQL

## Database Connection Details

### Connection String
```
postgresql://pocketflow:pocketflow_password@localhost:5432/pocketflow
```

### Database Tables
- **users**: User management (email, name, personality, timestamps)
- **scheduled_jobs**: Job scheduling configuration
- **job_executions**: Job execution history and results
- **greenlist**: Email/domain whitelist

## Environment Variables

### Required Environment Variable
```bash
DATABASE_URL=postgresql://pocketflow:pocketflow_password@localhost:5432/pocketflow
```

### Service Configuration
Both services now include:
```ini
Environment=DATABASE_URL=postgresql://pocketflow:pocketflow_password@localhost:5432/pocketflow
```

## Dependencies

### Added to requirements.txt
```
psycopg2-binary==2.9.10
```

## Migration Scripts

### `migrate_to_postgresql.py`
- Migrates data from SQLite to PostgreSQL
- Handles missing tables gracefully
- Supports all existing table structures

### `test_postgresql.py`
- Tests PostgreSQL connectivity
- Verifies table creation and basic operations
- Confirms database service functionality

## Service Status

### Current Running Services
- ✅ **PocketFlow Email Processing Agent** (`pocketflow.service`)
- ✅ **Dashboard** (`dashboard.service`)

### Service URLs
- Dashboard: http://192.168.1.7:5001
- PostgreSQL: localhost:5432

## Benefits of PostgreSQL Migration

1. **Scalability**: Better performance for concurrent operations
2. **Reliability**: ACID compliance and better data integrity
3. **Features**: Advanced SQL features, JSON support, full-text search
4. **Backup**: Built-in backup and recovery tools
5. **Monitoring**: Better monitoring and performance tuning capabilities

## Rollback Plan

If needed, you can rollback to SQLite by:

1. Update `DATABASE_URL` to: `sqlite:///pocketflow.db`
2. Restart services: `sudo systemctl restart pocketflow.service dashboard.service`

## Maintenance

### Database Backup
```bash
# Create backup
pg_dump -U pocketflow -h localhost pocketflow > backup.sql

# Restore backup
psql -U pocketflow -h localhost pocketflow < backup.sql
```

### Database Monitoring
```bash
# Check database size
sudo -u postgres psql -d pocketflow -c "SELECT pg_size_pretty(pg_database_size('pocketflow'));"

# Check table sizes
sudo -u postgres psql -d pocketflow -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
```

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure pocketflow user has proper permissions
2. **Connection Refused**: Check if PostgreSQL service is running
3. **Table Not Found**: Run migration script to create tables

### Useful Commands

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check service logs
sudo journalctl -u pocketflow.service -f
sudo journalctl -u dashboard.service -f

# Test database connection
python3 test_postgresql.py
```

## Migration Date
**Completed**: August 11, 2025

## Migration Status
**✅ COMPLETE** - All systems operational with PostgreSQL 