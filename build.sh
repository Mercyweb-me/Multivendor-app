#!/bin/bash
set -e

echo "Building application..."

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

echo "Build complete!"
