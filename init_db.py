import psycopg2
from config import *

conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
)

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a command: this creates a new table
cur.execute(open("flaskr/schema.sql", "r").read())

conn.commit()

cur.close()
conn.close()