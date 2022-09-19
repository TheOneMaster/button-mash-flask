from flask import Blueprint, render_template, send_from_directory

main = Blueprint("main", __name__, static_folder='static')

@main.route("/")
def home():
    return render_template('index.jinja')

@main.route("/game")
def game():
    return render_template('game.jinja')

@main.route("/humans.txt")
def humans():
    return send_from_directory(main.static_folder, 'humans.txt')
