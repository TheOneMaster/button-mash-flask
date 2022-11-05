from flask import Blueprint, render_template

from . import events

game = Blueprint("game", __name__, static_folder='static', template_folder='templates')

@game.route('/game')
def game_route():
    return render_template('game.jinja')
