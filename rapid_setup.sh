#!/bin/bash

echo "🔧 Setting Up the Development Environment"

echo "1. Creating and Activating a Virtual Environment..."
python3 -m venv .venv >>/dev/null
source .venv/bin/activate 

echo "2. Installing Dependencies..."
pip install -r requirements.txt >>/dev/null

echo "✅ Setup Complete!"
