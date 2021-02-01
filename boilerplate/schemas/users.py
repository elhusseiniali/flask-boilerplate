from boilerplate.schemas import BaseSchema
from marshmallow import fields


class UserSchema(BaseSchema):
    __envelope__ = {"single": "user", "many": "users"}

    class Meta:
        ordered = True

    username = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.String(required=True)
    image_file = fields.String(required=False)
