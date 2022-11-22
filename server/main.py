from flask import Blueprint, send_from_directory, redirect, url_for

main = Blueprint("main", __name__, static_folder='static')

@main.route("/")
def home():
    return redirect(url_for('game.game'))

@main.route("/humans.txt")
def humans():
    return send_from_directory(main.static_folder, 'humans.txt')
