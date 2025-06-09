#!/bin/bash

# Check if python is installed
if ! command -v python3 &> /dev/null
then
    echo "Python3 is not installed. Please install Python3 first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null
then
    echo "pip3 is not installed. Installing pip..."
    sudo apt-get update
    sudo apt-get install -y python3-pip
fi

# Install required Python packages
echo "Installing Python packages from requirements.txt..."
pip3 install -r requirements.txt

echo "Setup completed."
