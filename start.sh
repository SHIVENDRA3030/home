#!/bin/bash

echo "========================================================"
echo "      HomeValue AI - Setup and Run Script (Mac/Linux)"
echo "========================================================"
echo ""

echo "[1/4] Checking for virtual environment..."
if [ ! -d "venv" ]; then
    echo "Creating new Python virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment found!"
fi

echo ""
echo "[2/4] Activating virtual environment..."
source venv/bin/activate

echo ""
echo "[3/4] Installing / Updating Python dependencies..."
pip install -r requirements.txt --quiet
echo "Dependencies are up to date!"

echo ""
echo "[4/4] Starting the HomeValue AI Backend Server..."
echo "The app will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop the server."
echo ""
python app/app.py
