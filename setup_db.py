import sys
import os
sys.path.insert(0, '/home/bracemarket/email-system')
os.environ['FLASK_ENV'] = 'production'
from dotenv import load_dotenv
load_dotenv('/home/bracemarket/email-system/.env')

# Import and run
from db_setup import setup_database
setup_database()
print("✓ Database initialized")