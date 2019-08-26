import flask_rest_api

class Api(flask_rest_api.Api):
    def setup_api(self, app):
        with app.app_context():
            api.init_app(app)

api = Api()
