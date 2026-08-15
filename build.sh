#!/usr/bin/env bash
pip install -r requirements.txt
chmod +x ./tailwindcss-linux
./tailwindcss-linux -i ./static/css/input.css -o ./static/css/main.css --minify
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py create_admin