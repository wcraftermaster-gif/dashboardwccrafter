#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

# Descargar Tailwind CLI para Linux si no existe ya (cache entre builds)
if [ ! -f ./tailwindcss-linux ]; then
  curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/download/v4.3.3/tailwindcss-linux-x64
  mv tailwindcss-linux-x64 tailwindcss-linux
  chmod +x ./tailwindcss-linux
fi

./tailwindcss-linux -i ./static/css/input.css -o ./static/css/main.css --minify

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py create_admin