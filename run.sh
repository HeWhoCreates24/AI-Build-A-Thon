#!/bin/bash
# Quick start script for Crisis Detection System

echo "======================================================================"
echo "                    CRISIS DETECTION SYSTEM"
echo "                         Quick Start"
echo "======================================================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "No virtual environment found. Running setup..."
    python3 setup.py
    
    if [ $? -ne 0 ]; then
        echo "❌ Setup failed. Please check errors above."
        exit 1
    fi
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# Verify system
echo ""
echo "Verifying system components..."
python3 verify.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ System verification failed. Please fix issues above."
    exit 1
fi

# Ask user what to run
echo ""
echo "======================================================================"
echo "What would you like to run?"
echo "======================================================================"
echo "1. Full system (crisis_detection/main.py)"
echo "2. Demo (demo.py)"
echo "3. Test NLP model (crisis_detection/core/demo_nlp.py)"
echo "4. Test OCR (crisis_detection/core/demo_ocr.py)"
echo "5. Test Risk Engine (crisis_detection/core/demo_risk.py)"
echo "6. Exit"
echo ""
read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        echo ""
        echo "Starting full system..."
        python3 crisis_detection/main.py
        ;;
    2)
        echo ""
        echo "Running demo..."
        python3 demo.py
        ;;
    3)
        echo ""
        echo "Testing NLP model..."
        python3 crisis_detection/core/demo_nlp.py
        ;;
    4)
        echo ""
        echo "Testing OCR..."
        python3 crisis_detection/core/demo_ocr.py
        ;;
    5)
        echo ""
        echo "Testing Risk Engine..."
        python3 crisis_detection/core/demo_risk.py
        ;;
    6)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "======================================================================"
echo "Execution complete!"
echo "======================================================================"
