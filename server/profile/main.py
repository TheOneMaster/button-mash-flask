from flask import Blueprint, render_template
from flask_login import login_required

profile_blueprint = Blueprint('profile', __name__,
                              static_folder='static', template_folder='templates',
                              url_prefix='/profile')

@profile_blueprint.route('/')
@login_required
def cur_user_profile():
    return render_template('self.jinja')
