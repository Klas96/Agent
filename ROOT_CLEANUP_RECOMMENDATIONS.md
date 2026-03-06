# Root Directory Cleanup Recommendations

## Overview
The PocketFlow root directory contains many files that should be organized or removed to improve project structure and maintainability.

## 🗂️ Files to MOVE

### Documentation Files → `/docs`
- `SIMPLIFIED_DONATION_PLAN.md` → `docs/migration_plans/`
- `ELECTRUM_DEPRECATION_PLAN.md` → `docs/migration_plans/`
- `DONATION_ONLY_COMPLETE_MIGRATION.md` → `docs/migration_plans/`
- `DONATION_ONLY_IMPLEMENTATION_SUMMARY.md` → `docs/migration_plans/`
- `DONATION_ONLY_MIGRATION_PLAN.md` → `docs/migration_plans/`
- `PODCASTIFY_SETUP_SUMMARY.md` → `docs/podcastify/`
- `PODCASTIFY_TOOL_DOCS.md` → `docs/podcastify/`
- `PODCASTIFY_INTEGRATION.md` → `docs/podcastify/`

### Utility Scripts → `/scripts/utilities`
- `check_payment.py`
- `payment_monitor.py`
- `mark_emails_unread.py`
- `check_recent_emails.py`
- `find_btc_address_in_dbs.py`
- `update_db_schema.py`
- `add_btc_addresses_to_prod.py`
- `remove_btc_address_from_db.py`

### Service Files → `/scripts/services`
- `pocketflow-payment-monitor.service`

### Example Files → `/examples`
- `agent_integration_example.py`
- `demo_document_creator.py`

### Test Files → `/tests`
- `test_donation_only_system.py`
- `test_flow_routing.py`
- `test_user_extraction.py`
- `test_electrum_direct.py`
- `test_real_user.py`
- `test_personality_fix.py`
- `test_btc_price.py`
- `test_current_features.sh`

### Data Files → `/data`
- `pocketflow.db` → `data/`

## 🗑️ Files to REMOVE

### Debug Files
- `debug_personality_web.py`
- `debug_personality.py`
- `debug_users_route.py`

### Temporary/Coverage Files
- `.coverage`
- `test_document.pdf`
- `current_events_flow.py`

### Podcastify Files (if not actively used)
- `agent_podcastify_tool.py`
- `podcastify_agent_example.py`
- `test_podcastify_tool.py`
- `podcastify_tool.py`
- `podcastify_workflow.py`
- `test_podcastify_integration.py`

## 📊 Impact Analysis

### Before Cleanup
- **Root files**: ~60+ files
- **Mixed concerns**: Documentation, tests, scripts, examples all in root
- **Poor organization**: Difficult to find specific files
- **Maintenance burden**: Hard to distinguish between active and obsolete files

### After Cleanup
- **Root files**: ~20 core files
- **Clear separation**: Each file type in appropriate directory
- **Better discoverability**: Easy to find specific file types
- **Reduced maintenance**: Clear distinction between active and legacy files

## 🎯 Core Files to Keep in Root

### Essential Project Files
- `README.md`
- `main.py`
- `setup.py`
- `requirements.txt`
- `requirements-no-torch.txt`
- `pytest.ini`
- `.gitignore`
- `LICENSE`

### Core Scripts
- `run_app.sh`
- `install-system.sh`
- `install_latex.sh`
- `update.sh`
- `manage_services.sh`
- `deploy.sh`
- `uninstall.sh`

### Configuration
- `.cursorrules`
- `.cursor/`

## 🚀 Execution

Run the cleanup script to automatically organize files:

```bash
./cleanup_root_directory.sh
```

## ⚠️ Important Notes

1. **Backup first**: Consider backing up the entire project before running cleanup
2. **Review podcastify files**: Ensure podcastify functionality is not actively used before removal
3. **Update references**: Check for any hardcoded paths that might break after moving files
4. **Test after cleanup**: Run tests to ensure nothing is broken by the reorganization

## 📈 Benefits

1. **Improved navigation**: Easier to find specific files
2. **Better organization**: Clear separation of concerns
3. **Reduced clutter**: Root directory becomes much cleaner
4. **Easier maintenance**: Clear distinction between active and legacy code
5. **Professional appearance**: Better project structure for contributors 