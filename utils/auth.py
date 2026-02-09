from functools import wraps
from flask import session, redirect, url_for
from werkzeug.security import check_password_hash

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "admin_id" not in session:
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated
