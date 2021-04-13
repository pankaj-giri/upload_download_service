from flask import Blueprint, Flask
from views.api import api
import os


def create_app():
    app = Flask(__name__)

    # config_ = create_config(os.getenv('FLASK_CONFIG') or 'default')
    # app.config.from_object(config_)
    app.register_blueprint(api)

    return app

app = create_app()

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000)