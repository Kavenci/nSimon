# --[[ Imports ]]--
from flask import (
    Flask,
    request,
    jsonify,
    redirect,
    render_template,
    url_for,
    make_response,
    flash,
    Blueprint,
    current_app,
)
import Database as Database
import Simon as Simon





# --[[ Blueprint Setup ]]--
setMusicBlueprint = Blueprint('setMusicBlueprint', __name__)




# --[[ Route ]]--
@setMusicBlueprint.route("/api/setMusic", methods=["POST"])
def setMusic():
    username = request.cookies.get("username")
    music = request.json.get(
        "music"
    )

    if music not in ["true", "false"]:
        return "Invalid theme", 400

    result = Database.databaseChangeMusic(username, music)

    if result == 200:
        return "Music updated", 200
    else:
        return "Failed to update Music Choice", 500