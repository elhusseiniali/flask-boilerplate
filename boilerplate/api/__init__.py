from flask import Blueprint
from flask_restx import Api

from boilerplate.api.users.routes import api as users


blueprint = Blueprint('api', __name__)
api = Api(blueprint)

api.add_namespace(users)
