#!/bin/bash

# Task Manager Application Launcher
# This script provides a quick way to start the application

echo "Task Manager - Application Launcher"
echo "----------------------------------"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "[SETUP] Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "[SETUP] Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "[SETUP] Installing dependencies..."
pip install -r requirements.txt

# Reset database and seed it with fresh data
echo "[SETUP] Resetting and seeding the database..."
python3 reset_db.py

# Run the application
echo ""
echo "[START] Starting application..."
echo "[INFO] The application will be available at: http://localhost:5001"
echo "[INFO] You can view debug information at: http://localhost:5001/app-debug"
echo "[INFO] Press Ctrl+C to stop the server when you're done"
echo ""
python3 app.py