# Bulk Email System

A full-stack bulk email system with Django REST Framework backend and React frontend for sending personalized license certificates via email.

## Features

- **Frontend**: React.js with Tailwind CSS
- **Backend**: Django REST Framework
- **Background Jobs**: Celery with Redis
- **Email Service**: Gmail SMTP (Google Workspace with App Password)
- **PDF Generation**: Dynamic HTML to PDF with static image pages
- **Real-time Updates**: Polling-based status tracking
- **Daily Limits**: 100 emails per day with quota management

## Project Structure

```
email bulk system/
|-- backend/
|   |-- email_system/
|   |   |-- __init__.py
|   |   |-- settings.py
|   |   |-- urls.py
|   |   |-- wsgi.py
|   |   |-- celery.py
|   |-- emails/
|   |   |-- __init__.py
|   |   |-- models.py
|   |   |-- views.py
|   |   |-- urls.py
|   |   |-- serializers.py
|   |   |-- admin.py
|   |   |-- apps.py
|   |   |-- tasks.py
|   |   |-- pdf_utils.py
|   |-- templates/
|   |   |-- license_certificate.html
|   |-- static/
|   |   |-- images/
|   |   |   |-- page2.jpg
|   |   |   |-- page3.jpg
|   |   |   |-- page4.jpg
|   |-- manage.py
|   |-- requirements.txt
|   |-- .env.example
|-- frontend/
|   |-- src/
|   |   |-- components/
|   |   |   |-- FileUpload.js
|   |   |   |-- ProgressTracker.js
|   |   |   |-- StatusCards.js
|   |   |   |-- JobHistory.js
|   |   |-- App.js
|   |   |-- index.js
|   |   |-- index.css
|   |-- package.json
|   |-- tailwind.config.js
|   |-- postcss.config.js
|   |-- public/
```

## Prerequisites

- Python 3.8+
- Node.js 14+
- Redis server
- Gmail account with App Password
- wkhtmltopdf (for PDF generation)

## Setup Instructions

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and configure
cp .env.example .env
# Edit .env with your settings
```

### 2. Configure Environment Variables

Edit the `.env` file in the backend directory:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True

# Gmail SMTP Settings
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password-here

# Celery/Redis Settings
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 3. Gmail App Password Setup

1. Enable 2-factor authentication on your Gmail account
2. Go to Google Account settings > Security > App passwords
3. Generate a new app password for "Mail"
4. Use this password in the `GMAIL_APP_PASSWORD` environment variable

### 4. Database Setup

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 5. Start Redis Server

```bash
# On macOS (using Homebrew)
brew services start redis

# On Ubuntu/Debian
sudo systemctl start redis-server

# On Windows (using WSL)
sudo service redis-server start
```

### 6. Start Backend Services

```bash
# Terminal 1: Start Django development server
python manage.py runserver

# Terminal 2: Start Celery worker
celery -A email_system worker --loglevel=info

# Terminal 3: Start Celery beat (for periodic tasks)
celery -A email_system beat --loglevel=info
```

### 7. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## Usage

```bash
redis-server --save '' --appendonly no --port 6379

./venv/bin/celery -A email_system worker --loglevel=info
```

### 1. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- Django Admin: http://localhost:8000/admin

### 2. Excel File Format

Your Excel file must contain these exact columns:

| Column | Description |
|--------|-------------|
| ref_no | Reference number shown on the PDF |
| name | Recipient's full name |
| email | Recipient's email address |
| company_name | Company or organization name |
| address_line1 | First line of address |
| address_line2 | Second line of address |

**Important**: Maximum 100 rows per file.

### 3. Sending Emails

1. Upload an Excel file using the drag-drop interface
2. The system validates the file and checks daily limits
3. Click "Start Email Sending" to begin processing
4. For each row, the system generates the PDF, attaches it to an HTML email, and sends it to the `email` value
5. The worker waits 7 seconds between each email
6. Monitor progress in real-time and check failed logs for any issues

## API Endpoints

- `POST /api/upload/` - Upload Excel file
- `POST /api/start/<job_id>/` - Start email sending
- `GET /api/status/<job_id>/` - Get job status
- `GET /api/daily-limit/` - Get daily email limit
- `GET /api/jobs/` - Get recent jobs

## Features Details

### PDF Generation

- First page: Dynamic HTML template with recipient data
- Pages 2-4: Static JPEG images
- Automatic PDF merging and compression
- Temporary file cleanup after sending

### Email Sending

- Gmail SMTP with App Password authentication
- HTML email body plus PDF attachment for each recipient
- 7-second delay between emails (anti-spam)
- Daily limit enforcement (100 emails)
- Automatic retry on failures
- Detailed error logging

### Real-time Updates

- 3-second polling interval for job status
- Live progress tracking
- Failed email notifications
- Daily quota updates

## Troubleshooting

### Common Issues

1. **PDF Generation Errors**
   - Install wkhtmltopdf: `sudo apt-get install wkhtmltopdf` (Ubuntu)
   - Check static image paths in `pdf_utils.py`

2. **Email Sending Failures**
   - Verify Gmail App Password
   - Check SMTP settings in `.env`
   - Ensure Redis is running

3. **Celery Task Issues**
   - Start Redis server before Celery
   - Check Celery logs for errors
   - Verify broker URL configuration

4. **Frontend Build Issues**
   - Clear node_modules and reinstall: `rm -rf node_modules package-lock.json && npm install`
   - Tailwind CSS warnings are normal and resolve on build

### Logs and Monitoring

- Django logs: Check terminal output
- Celery logs: Monitor worker terminal
- Email records: Available in Django admin
- Failed emails: Shown in frontend and admin

## Security Considerations

- Use environment variables for sensitive data
- Enable Django's CSRF protection in production
- Use HTTPS in production
- Regular cleanup of temporary PDF files
- Monitor email sending limits

## Performance Optimization

- Celery processes emails asynchronously
- PDF generation is optimized for speed
- Database queries use bulk operations
- Frontend uses efficient polling

## License

This project is for educational and internal use only.


# author
Name:-Aditya chauhan
Email:- "Suryachauhan367367@gmail.com",
Url:-"https://github.com/Aditya367367",
Linkedin:- "https://www.linkedin.com/in/aditya-chauhan-1b1a95228/",
    