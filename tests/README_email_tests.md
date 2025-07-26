# Email Tests

This directory contains test scripts for troubleshooting and testing the PocketFlow email system.

## Test Files

### `test_email_config.py`
Tests the email configuration and connectivity.
- Verifies email settings are properly configured
- Tests connection to the email server
- Checks if unread emails can be fetched

**Usage:**
```bash
python tests/test_email_config.py
```

### `test_email_fetch_all.py`
Lists all emails in the inbox with details.
- Shows total number of emails
- Shows number of unread emails
- Lists the 10 most recent emails with details

**Usage:**
```bash
python tests/test_email_fetch_all.py
```

### `test_imap_flags.py`
Checks IMAP flags for recent emails.
- Shows the read/unread status of recent emails
- Displays IMAP flags for debugging

**Usage:**
```bash
python tests/test_imap_flags.py
```

### `test_mark_emails_unread.py`
Marks recent emails as unread for testing.
- Marks the 3 most recent emails as unread
- Useful for testing the email processing system

**Usage:**
```bash
python tests/test_mark_emails_unread.py
```

### `test_force_unread.py`
Force marks emails as unread using multiple IMAP methods.
- Uses multiple IMAP commands to ensure emails are marked as unread
- More reliable than the basic version

**Usage:**
```bash
python tests/test_force_unread.py
```

## Troubleshooting Email Issues

If you're not receiving email responses from the PocketFlow agent:

1. **Check if emails are being processed:**
   ```bash
   python tests/test_email_config.py
   ```

2. **Check if there are unread emails:**
   ```bash
   python tests/test_email_fetch_all.py
   ```

3. **If all emails are marked as read, mark some as unread for testing:**
   ```bash
   python tests/test_force_unread.py
   ```

4. **Send a new email to `agent@klasholmgren.se` and wait for processing**

## Email System Status

The email system is working correctly if:
- ✅ Email configuration test passes
- ✅ Email service can connect to server
- ✅ Unread emails are detected and processed
- ✅ Emails are marked as read after processing

## Common Issues

- **No unread emails**: All emails have been processed and marked as read
- **Connection errors**: Check email server settings and credentials
- **Authentication errors**: Verify email username and password 