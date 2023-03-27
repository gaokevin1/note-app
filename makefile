SHELL=./make-venv

# Name of the virtual environment to create
VENV_NAME := .venv

# Python command
PYTHON := python3

# Pip command
PIP := $(VENV_NAME)/bin/pip

# Flask application entry point
FLASK_APP := main.py

# Install dependencies
install:
	$(PYTHON) -m venv $(VENV_NAME)
	$(PIP) install -r requirements.txt

# Run the Flask development server
run:
	$(VENV_NAME)/bin/flask run

# Run tests
test:
	$(VENV_NAME)/bin/pytest tests/

# Clean up files
clean:
	rm -rf $(VENV_NAME) *.pyc __pycache__

.PHONY: install run test clean