#!/bin/bash

# Bulk Email System Setup Script
echo "Setting up Bulk Email System..."

# Backend Setup
echo "Setting up backend..."
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Please edit backend/.env with your settings"
fi

# Run migrations
python manage.py makemigrations
python manage.py migrate

echo "Backend setup complete!"

# Frontend Setup
echo "Setting up frontend..."
cd ../frontend

# Install dependencies
npm install

echo "Frontend setup complete!"

echo "Setup complete! Please:"
echo "1. Edit backend/.env with your Gmail settings"
echo "2. Start Redis server"
echo "3. Run 'cd backend && source venv/bin/activate && python manage.py runserver'"
echo "4. Run 'cd backend && source venv/bin/activate && celery -A email_system worker --loglevel=info'"
echo "5. Run 'cd frontend && npm start'"
echo "6. Open http://localhost:3000"
