#!/bin/bash
# Quick setup script for email system

echo "================================"
echo "Email System - Quick Setup"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✓ Python3 found: $(python3 --version)"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""

# Setup environment file
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your database and SMTP credentials"
    echo ""
fi

echo ""
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Edit .env with your database and SMTP settings"
echo "2. Run: python db_setup.py       (to create database tables)"
echo "3. Run: python insert_samples.py (optional, for testing)"
echo "4. Run: python email_sender.py --once  (to send emails once)"
echo "5. Or:  python email_sender.py --schedule 09:00  (daily scheduler)"
echo ""
