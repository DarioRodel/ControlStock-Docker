#!/bin/bash

# Espera a que la base de datos esté lista
/wait-for-it.sh db:3306 --timeout=60 --strict -- echo "Database is up"

# Ejecuta las migraciones
python manage.py migrate

# Ejecuta el script de inicialización (Python, no SQL)
python manage.py shell < init_django.py

# Arranca el servidor
python manage.py runserver 0.0.0.0:8000
