"""
WSGI entry point for production deployment with Gunicorn or other WSGI servers.
This file is used by production servers to run the Flask application.

Usage:
    gunicorn wsgi:app
    gunicorn wsgi:app --workers 4 --bind 0.0.0.0:5001
"""

import os
import logging
from dashboard import app
from config import PRODUCTION

# Configure logging for production
if PRODUCTION:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('email_system.log'),
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    logger.info(f"Starting application on port {port} (Production: {PRODUCTION})")
    app.run(host='0.0.0.0', port=port)
