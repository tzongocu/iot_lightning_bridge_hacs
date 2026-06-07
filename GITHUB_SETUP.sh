#!/bin/bash
# GitHub Setup Guide for IOT Lightning Bridge HACS

# This script will help you initialize the repository and push to GitHub

echo "=========================================="
echo "IOT Lightning Bridge HACS - GitHub Setup"
echo "=========================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    echo "   Ubuntu/Debian: sudo apt-get install git"
    echo "   macOS: brew install git"
    exit 1
fi

echo "✅ Git is installed"
echo ""

# Initialize git repository
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    git config user.name "Your Name"
    git config user.email "your.email@example.com"
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already initialized"
fi

echo ""
echo "=========================================="
echo "NEXT STEPS:"
echo "=========================================="
echo ""
echo "1. CREATE REPOSITORY ON GITHUB:"
echo "   - Go to https://github.com/new"
echo "   - Repository name: iot_lightning_bridge_hacs"
echo "   - Description: Bridge oficial pentru integrarea dispozitivelor IOT Lightning în Home Assistant via MQTT"
echo "   - Choose: Public"
echo "   - DO NOT initialize with README, .gitignore, or license (we already have these)"
echo "   - Click 'Create repository'"
echo ""
echo "2. CONFIGURE REMOTE (replace YOUR_USERNAME):"
echo "   git remote add origin https://github.com/YOUR_USERNAME/iot_lightning_bridge_hacs.git"
echo ""
echo "3. ADD ALL FILES:"
echo "   git add ."
echo ""
echo "4. COMMIT:"
echo "   git commit -m 'Initial commit: IOT Lightning Bridge HACS integration'"
echo ""
echo "5. PUSH TO GITHUB (replace main if using different branch):"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "=========================================="
