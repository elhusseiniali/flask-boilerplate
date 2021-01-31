from boilerplate import db, login_manager, bcrypt
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from flask_validator import ValidateEmail


@login_manager.user_loader
def load_user(user_id):
    """Get the current logged-in User object.

    Parameters
    ----------
    user_id : [int]
        User ID.

    Returns
    -------
    [User]
        A User object (see boilerplate.models).
    """
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    """[User]
    Parameters
    ----------
    username: [string]
        Unique username.
    email: [email]
        Unique email.
    image_file: [string]
        File path for the chosen profile picture.
        Default image is default.jpg.
    _password: [string]
        Hashed password.
        Extra functions are there to hash the password then store it.

    Relationships
    -------------
    None.
    """
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)

    image_file = db.Column(db.String(30),
                           nullable=False,
                           default='default.jpg')

    _password = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return (f"User('{self.username}': '{self.email}')")

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = bcrypt.generate_password_hash(password)

    def verify_password(self, password):
        return bcrypt.check_password_hash(self._password, password)

    @classmethod
    def __declare_last__(cls):
        # check_deliverability can be set to True
        # after the developer updated the release on PyPI.
        # https://github.com/xeBuz/Flask-Validator/issues/79
        ValidateEmail(User.email,
                      allow_smtputf8=True,
                      check_deliverability=True,
                      throw_exception=True,
                      message="The e-mail is invalid.")
