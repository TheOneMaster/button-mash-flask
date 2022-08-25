from functools import wraps
from flask import redirect, url_for
from flask_login import current_user

def no_login(location: str):
    """
    Decorator used to mark which locations are only available when the user is not logged in. Select location to redirect to.
    
    .. code-block:: python

        @no_login("main.home")
        def login():
            ...        
    """
    
    def decorator(fn):
        @wraps(fn)
        
        def wrap(*args, **kwargs):
            
            if current_user.is_authenticated:
                return redirect(url_for(location))
            
            return fn(*args, **kwargs)
        
        return wrap
    
    return decorator 