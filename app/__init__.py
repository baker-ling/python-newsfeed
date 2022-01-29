from flask import Flask
from app.routes import dashboard, home

def create_app(test_config=None):
    app = Flask(__name__, static_url_path='/')
    app.url_map.strict_slashes = False
    app.config.from_mapping(
        SECRET_KEY='BDBs_secret_key'
    )

    @app.route('/hello')
    def hello():
        return 'hello world'

    # register routes
    app.register_blueprint(home)
    app.register_blueprint(dashboard)

    return app