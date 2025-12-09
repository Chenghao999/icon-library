#!/bin/bash

echo "Icon Manager Local Run Script (Linux/macOS)"
echo "------------------------"

# Create necessary directory structure
echo "Creating necessary directory structure..."
mkdir -p static/icons/Uncategorized templates data

# Check if pip is installed, if not prompt to install Python
echo "Checking Python environment..."
pip --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Error: pip not found, please install Python 3.6 or higher first"
    echo "Recommended to install Python 3.10 or 3.11 for best compatibility"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP 'Python \K\d+\.\d+')
echo "Detected Python version: $PYTHON_VERSION"

# Install required dependencies
echo "Installing Python dependencies..."
echo "If the installation process is slow, please be patient..."
pip install -r requirements.txt --user

if [ $? -ne 0 ]; then
    echo "Dependency installation failed!"
    echo "Please try the following solutions:"
    echo "1. Ensure you have network connection"
    echo "2. Try running this script with administrator privileges: sudo ./run-local.sh"
    echo "3. If still failing, you can try installing Flask alone: pip install flask --user"
    echo "4. Then run: python app.py (basic functionality may still be available even if some dependencies aren't installed)"
    echo "----------------------------------------"
    echo "Press 1 to continue installation (retry), press 2 to skip dependency installation and run the app directly"
    read -n 1 -p "Please select [1-2]: " choice
    echo
    
    if [ "$choice" = "1" ]; then
        # Try using a different pip command
        echo "Trying pip3..."
        pip3 install -r requirements.txt --user
        
        if [ $? -ne 0 ]; then
            echo "Installation with pip3 also failed! Trying with Tsinghua mirror..."
            pip install -r requirements.txt --user -i https://pypi.tuna.tsinghua.edu.cn/simple
        fi
    elif [ "$choice" != "2" ]; then
        echo "Invalid choice, exiting script"
        exit 1
    fi
fi

# Set environment variables
echo "Setting environment variables..."
export FLASK_APP=app.py
export FLASK_ENV=development
export SECRET_KEY=icon_manager_secret_key
export ICON_STORAGE_PATH=./static/icons

echo "Starting Icon Manager..."
echo "----------------------------------------"
echo "Access URL: http://localhost:5000"
echo "----------------------------------------"
echo "Tips:"
echo "- Please open the above address in your browser to access Icon Manager"
echo "- To stop the application, press Ctrl+C"
echo "----------------------------------------"

# Run application directly with Python
python3 app.py

if [ $? -ne 0 ]; then
    echo "Application failed to start!"
    echo "Possible reasons:"
    echo "1. Port 5000 is already in use"
    echo "2. Missing dependencies"
    echo "3. Permission issues"
    echo "Please try changing the port with the following command:"
    echo "FLASK_RUN_PORT=5001 python3 app.py"
fi

echo "Application stopped"
