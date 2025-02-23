import os
import psycopg2
from flask import Flask
from config import *


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="dev"
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

    @app.route("/submit/<identifier>")
    def submit(identifier):
        identifier = int(identifier)
        cursor = conn.cursor()
        cursor.execute("SELECT id, works FROM xss_eval WHERE id = %s", (identifier,))
        obj = cursor.fetchone()
        if obj is not None:
            if obj[1]:
                cursor.execute("UPDATE xss_eval SET repeated_execution = true WHERE id = %s", (identifier,))
            else:
                cursor.execute("UPDATE xss_eval SET works = true WHERE id = %s", (identifier,))
        else:
            cursor.execute("INSERT INTO xss_eval (id, payload, attacked_path, works) VALUES (%s, %s, %s)", (identifier, 'unknown payload', 'unknown path', True))
        conn.commit()
        return "OK"

    @app.route("/results")
    def results():
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM xss_eval")
        result = "Entries: \n"
        for row in cursor.fetchall():
            result += f"{row[0], row[1], row[2], row[3]}\n"
        return result
    return app

if __name__ == "__main__":
    create_app().run()
