import os

from flask import Flask


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="dev",
        # store the database in the instance folder
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
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

    # register the database commands
    from . import db

    db.init_app(app)

    @app.route("/submit/<identifier>")
    def submit(identifier):
        identifier = int(identifier)
        database = db.get_db()
        cur = database.execute("SELECT id, works FROM xss WHERE id = ?", (identifier,))
        obj = cur.fetchone()
        if obj is not None:
            if obj[1]:
                database.execute("UPDATE xss SET repeated_execution = true WHERE id = ?", (identifier,))
            else:
                database.execute("UPDATE xss SET works = true WHERE id = ?", (identifier,))
        else:
            database.execute("INSERT INTO xss (id, payload, attacked_path, impact, works) VALUES (?, ?, ?, ?)", (identifier, 'unknown payload', 'unknown path', 'unknown impact', True))
        database.commit()
        db.close_db(database)
        return

    @app.route("/results")
    def results():
        database = db.get_db()
        cur = database.execute("SELECT * FROM xss")
        result = "Entries: \n"
        for row in cur.fetchall():
            result += f"{row[0], row[1], row[2], row[3]}\n"
        return result
    return app

if __name__ == "__main__":
    create_app().run()
