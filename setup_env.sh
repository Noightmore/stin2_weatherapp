#!/bin/bash

# Variables
VENV_NAME="stin2_weather_app"
PYTHON_VERSION="3.11"

# Create Python virtual environment
python${PYTHON_VERSION} -m venv ${VENV_NAME}

# Activate virtual environment
source ${VENV_NAME}/bin/activate

# Upgrade pip to the latest version
pip install --upgrade pip

# Install packages from requirements.txt
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "requirements.txt not found."
fi

# Install nbstripout and set up git hook
pip install nbstripout
nbstripout --install

echo "✅ Virtual environment '${VENV_NAME}' setup completed, including nbstripout."
