from flask import Flask

from watchman.blueprints.client import clientRoutes
from watchman.blueprints.dashboard import dashboardRoutes

def create_app(settings_override=None):

    app = Flask(__name__, static_folder='../public', static_url_path='')

    if settings_override:
        app.config.update(settings_override)

    app.register_blueprint(clientRoutes)
    app.register_blueprint(dashboardRoutes)

    @app.route("/")
    def ping():
        return "Watchman Running!!"

    return app

app = create_app()