import psycopg2

conn = psycopg2.connect(
        host="localhost",
        port="8080",
        database="xss_db",
        user="xss",
        password="xss"
)

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a command: this creates a new table
cur.execute(open("flaskr/schema.sql", "r").read())

conn.commit()

cur.close()
conn.close()