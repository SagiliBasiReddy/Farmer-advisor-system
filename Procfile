release: echo "Agro Advisor starting..."
web: gunicorn --bind 0.0.0.0:$PORT --workers 1 --worker-class sync --timeout 120 --max-requests 1000 app:app
