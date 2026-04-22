#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Upgrading pip and installing core build dependencies..."
pip install --upgrade pip setuptools wheel

echo "Installing requirements..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running migrations..."
python manage.py migrate
