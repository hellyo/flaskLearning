from functools import wraps
from flask import g
from .errors import forbidden

def permission_required(permission):
    def decrator(f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            if not g.current_user.can(permission_required):
                return forbidden('Insufficient permissions')
            return f(*args,**kwargs)
        return decorated_function
    return decrator