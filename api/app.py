from flask import Flask, redirect, url_for, request
from alchemical.flask import Alchemical
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_mail import Mail
from apifairy import APIFairy
from config import Config
from flask_migrate import Migrate

# Deine bestehenden Initialisierungen
db = Alchemical()
ma = Marshmallow()
cors = CORS()
mail = Mail()
apifairy = APIFairy()

# Migrate-Objekt erstellen
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # extensions
    from api import models
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)  # Flask-Migrate initialisieren

    if app.config['USE_CORS']:  # pragma: no branch
        cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    mail.init_app(app)
    apifairy.init_app(app)

    # blueprints
    from api.errors import errors
    app.register_blueprint(errors)
    from api.tokens import tokens
    app.register_blueprint(tokens, url_prefix='/api')
    from api.users import users
    app.register_blueprint(users, url_prefix='/api')
    from api.posts import posts
    app.register_blueprint(posts, url_prefix='/api')
    from api.fake import fake
    app.register_blueprint(fake)
    from api.scan import scan
    app.register_blueprint(scan, url_prefix='/api')
    from api.scan_stream import scan_stream
    app.register_blueprint(scan_stream, url_prefix='/api')
    from .scan_runtime import scan_runtime
    app.register_blueprint(scan_runtime, url_prefix='/api')
    from api.scan_import import scan_data
    app.register_blueprint(scan_data, url_prefix='/api')
    from api.scan_deauth import scan_deauth
    app.register_blueprint(scan_deauth, url_prefix="/api")
    from api.clear_database import clear_db
    app.register_blueprint(clear_db, url_prefix="/api")
    from api.download_file import download_file_bp
    app.register_blueprint(download_file_bp, url_prefix='/api')

    # define the shell context
    @app.shell_context_processor
    def shell_context():  # pragma: no cover
        ctx = {'db': db}
        for attr in dir(models):
            model = getattr(models, attr)
            if hasattr(model, '__bases__') and \
                    db.Model in getattr(model, '__bases__'):
                ctx[attr] = model
        return ctx

    @app.route('/')
    def index():  # pragma: no cover
        return redirect(url_for('apifairy.docs'))

    @app.after_request
    def after_request(response):
        # Werkzeug sometimes does not flush the request body so we do it here
        request.get_data()
        return response

    return app
