import mysql.connector
from config import DB_CONFIG

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    
    # Check total emails
    cursor.execute('SELECT COUNT(*) as count FROM emails')
    total = cursor.fetchone()
    print(f'Total emails in database: {total["count"]}')
    
    # Check validation status distribution
    cursor.execute('SELECT validation_status, COUNT(*) as count FROM emails GROUP BY validation_status')
    results = cursor.fetchall()
    print('\nValidation status distribution:')
    for row in results:
        print(f'  {row["validation_status"]}: {row["count"]}')
    
    # Show sample emails
    cursor.execute('SELECT id, recipient, validation_status FROM emails LIMIT 5')
    samples = cursor.fetchall()
    print('\nSample emails:')
    for row in samples:
        print(f'  ID: {row["id"]}, Email: {row["recipient"]}, Status: {row["validation_status"]}')
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
