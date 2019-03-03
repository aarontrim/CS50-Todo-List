export FLASK_APP=application.py
export SECRET_KEY=e9375ecd-fe3e-4027-b027-0f5cfa91a17b
# export FLASK_DEBUG=1
# flask run --host 0.0.0.0
# flask shell
venv/bin/gunicorn --certfile=/etc/letsencrypt/live/todo.aarontrim.com/fullchain.pem --keyfile=/etc/letsencrypt/live/todo.aarontrim.com/privkey.pem -b 0.0.0.0:443 application:app
