from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_caching import Cache
import  config

configuration = config.Config()

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()
cache = Cache()

def create_app():
    app = Flask(__name__)
    cache = Cache()
    app.config.from_object(configuration)


    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app,db)
    login_manager.init_app(app)
    cache.init_app(app)



    login_manager.login_view = 'routes.login'
    login_manager.login_message_category = 'info'
    cache = Cache(app, config={'CACHE_TYPE': 'simple',
                               'CACHE_DEFAULT_TIMEOUT': 300})

    from app.routes import routes
    app.register_blueprint(routes)

    return app
