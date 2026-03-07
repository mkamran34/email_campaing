# Gunicorn Configuration File
# Location: /var/www/email-system/gunicorn.conf.py
#
# Usage:
#   gunicorn -c gunicorn.conf.py wsgi:app

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5001"
backlog = 2048
timeout = 120
keepalive = 5

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Server mechanics
daemon = False
pidfile = "/var/run/gunicorn-email-system.pid"
umask = 0
user = "www-data"
group = "www-data"
tmp_upload_dir = "/tmp"

# Server hooks
def on_starting(server):
    print("✓ Gunicorn server starting...")

def when_ready(server):
    print("✓ Gunicorn server ready. Spawning workers")

def on_exit(server):
    print("✓ Gunicorn server terminated")

# Logging
accesslog = "/var/log/email-system/gunicorn-access.log"
errorlog = "/var/log/email-system/gunicorn-error.log"
loglevel = os.getenv('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "email-system"

# SSL (optional - use with nginx as reverse proxy)
# keyfile = "/etc/ssl/private/your-key.key"
# certfile = "/etc/ssl/certs/your-cert.crt"
# ssl_version = "TLSv1_2"
# ciphers = 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256'
