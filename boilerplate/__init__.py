from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from boilerplate.config import BaseConfig


db = SQLAlchemy()
bcrypt = Bcrypt()

login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'


#   Below import is necessary, even if the linter complains about it.
#   This is because the linter cannot distinguish between imports in a script
#   and imports in a package. The order of the imports is also important.
#   These two imports *had* to happen after initializing db.
from boilerplate.models import User

from flask_admin import Admin
from boilerplate.admin_views import UserView


admin = Admin(name='boilerplate Admin', template_mode='bootstrap3')
# Add administrative views here
admin.add_view(UserView(User, db.session))


# Image dimensions
MAX_HEIGHT = 400
MAX_WIDTH = 400


def create_app(config_class=BaseConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    admin.init_app(app)

    from boilerplate.api.users.views import users
    from boilerplate.api.main.routes import main

    from boilerplate.api.errors.handlers import errors

    from boilerplate.api import blueprint as api
    app.register_blueprint(api, url_prefix='/api/1')

    app.register_blueprint(main)
    app.register_blueprint(errors)

    app.register_blueprint(users)

    return app
