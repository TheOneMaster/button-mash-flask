from flask import Blueprint, redirect, url_for, render_template

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return render_template('index.jinja')

@main.route("/game")
def game():
    return render_template('game.jinja')