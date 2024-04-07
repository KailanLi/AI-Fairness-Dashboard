from flask import Flask
from flask_session import Session

def init_app():
    """Construct core Flask application with embedded Dash app."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')
    app.secret_key = "!Eetkuadinh1l"

# Initialize Flask-Session
    Session(app)
    print(app.config['SECRET_KEY'])

    with app.app_context():
        # Import parts of our core Flask app
        from . import routes


        # Import Dash application
        from .plotlydash.dashboard import init_dashboard
        from .plotlydash.graphapp import init_graph_app
        init_dashboard(app)
        init_graph_app(app)
        return app