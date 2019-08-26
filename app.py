from flask import Flask

from core.database import setup_database
from core.api import api





def create_app():
    app = Flask(__name__, static_folder="static")
    app.config.from_pyfile("flask.cfg")

    setup_database(app)

    api.setup_api(app)

    import orm.imports.api

    print(app.url_map)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run()#host="0.0.0.0", port=8080)
