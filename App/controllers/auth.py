from flask_jwt_extended import create_access_token
from App.models import User

def authenticate(username, password):
    user = User.query.filter_by(username=username).one_or_none()
    if user and user.check_password(password):
        return user
    return None

def jwt_authenticate(username, password):
    user = User.query.filter_by(username=username).one_or_none()
    if user and user.check_password(password):
        # Notice the indentation here! This line is inside the 'if'
        return create_access_token(identity=str(username))
    return None

def setup_jwt(app):
    from flask_jwt_extended import JWTManager
    jwt = JWTManager(app)
    return jwt