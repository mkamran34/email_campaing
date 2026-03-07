web: gunicorn wsgi:app --workers 4 --bind 0.0.0.0:$PORT --timeout 120
release: python db_setup.py
