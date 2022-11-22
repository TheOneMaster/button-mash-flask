from flask_assets import Bundle

template_bundle = Bundle("client-JS/template.js",
                         filters="jsmin", output="gen/template.js")

game_bundle = Bundle("game/SettingsOption.js",
                     "game/gameTypes.js",
                     "game/classes.js",
                     filters="jsmin", depends="game/*.js", output="gen/game.js")
