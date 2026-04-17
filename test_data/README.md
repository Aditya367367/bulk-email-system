# Test Data for Bulk Email System

This directory contains sample Excel files for testing the bulk email system.

## Files Available

### 1. sample_emails_5.xlsx
- **Records**: 5 test email recipients
- **Use Case**: Quick testing and development
- **File Size**: ~5 KB

### 2. sample_emails_20.xlsx
- **Records**: 20 test email recipients  
- **Use Case**: Medium-scale testing
- **File Size**: ~6 KB

### 3. sample_emails_100.xlsx
- **Records**: 100 test email recipients (maximum allowed)
- **Use Case**: Full system testing at daily limit
- **File Size**: ~10 KB

## Data Format

Each Excel file contains the following required columns:

| Column | Description | Example |
|--------|-------------|---------|
| name | Recipient's full name | John Smith |
| email | Email address | john.smith@example.com |
| license_number | License certificate number | LC-2024-001 |
| validity_from | License start date | 2024-01-15 |
| premises_type | Type of premises | Retail/Restaurant/Office |
| category | Business category | Food Service/General/Medical |
| address | Full address | 123 Main St, New York, NY 10001 |

## Email Addresses Used

All test emails use example.com domains:
- `@example.com` for basic tests
- `@test.com` for medium tests  
- `@maxtest.com` for full capacity tests

**Note**: These are test email addresses and will not receive actual emails. For real email testing, replace with valid email addresses.

## Usage

1. Start the Django backend: `python manage.py runserver`
2. Start the React frontend: `npm start`
3. Upload any of these Excel files through the web interface
4. Test the email sending functionality

## Daily Limit

The system is configured to send maximum 100 emails per day. The `sample_emails_100.xlsx` file tests this limit.
