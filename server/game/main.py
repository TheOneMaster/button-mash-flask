from flask import Blueprint, render_template

from . import events

game_blueprint = Blueprint("game", __name__, static_folder='static', template_folder='templates')

@game_blueprint.route('/game')
def game():
    return render_template('game.jinja')
