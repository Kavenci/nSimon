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
)
import configparser
import logging




# --[[ Blueprints ]]--
from routes.public.index import indexBlueprint
from routes.public.dashboard import dashboardBlueprint
from routes.public.profile import profileBlueprint
from routes.public.settings import settingsBlueprint
from routes.public.calendar import calendarBlueprint
from routes.public.classes import classesBlueprint

from routes.backend.login import loginBlueprint
from routes.backend.logout import logoutBlueprint
from routes.backend.support import supportBlueprint

from routes.backend.dashboard.getCalendar import getCalendarBlueprint
from routes.backend.dashboard.getDailyMessages import getDailyMessagesBlueprint
from routes.backend.dashboard.getTimetable import getTimetableBlueprint
from routes.backend.dashboard.getToday import getTodayBlueprint
from routes.backend.dashboard.getUserInfo import getUserInfoBlueprint
from routes.backend.dashboard.getWeather import getWeatherBlueprint

from routes.backend.classes.getClasses import getClassesBlueprint
from routes.backend.classes.getTaskRubric import getTaskRubricBlueprint
from routes.backend.classes.getResultInfo import getResultInfoBlueprint

from routes.backend.settings.getMusic import getMusicBlueprint
from routes.backend.settings.setMusic import setMusicBlueprint
from routes.backend.settings.getSessionSetting import getSessionSettingBlueprint
from routes.backend.settings.getTheme import getThemeBlueprint
from routes.backend.settings.setTheme import setThemeBlueprint

from routes.backend.profile.getCommendations import getCommendationsBlueprint
from routes.backend.profile.getDashboardData import getDashboardDataBlueprint
from routes.backend.profile.getStudentProfileDetails import getStudentProfileDetailsBlueprint
from routes.backend.profile.getStudentProfileImage import getStudentProfileImageBlueprint
from routes.backend.profile.getReports import getReportsBlueprint

from routes.backend.classes.showClass import showClassBlueprint
from routes.backend.classes.showTask import showTaskBlueprint



# --[[ Logs ]]--
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




# --[[ Config ]]--
config = configparser.ConfigParser()
config.read("config.ini")
flask_secret = config.get("Flask", "secret")




# --[[ Flask Setup ]]--
app = Flask(__name__)
app.secret_key = flask_secret




# --[[ Index Route ]]--
app.register_blueprint(indexBlueprint)

# --[[ Login Route ]]--
app.register_blueprint(loginBlueprint)

# --[[ Logout Route ]]--
app.register_blueprint(logoutBlueprint)

# --[[ Dashboard Route ]]--
app.register_blueprint(dashboardBlueprint)

# --[[ Profile Route ]]--
app.register_blueprint(profileBlueprint)

# --[[ Settings Route ]]--
app.register_blueprint(settingsBlueprint)

# --[[ Calendar Route ]]--
app.register_blueprint(calendarBlueprint)

# --[[ Classes Route ]]--
app.register_blueprint(classesBlueprint)
app.register_blueprint(showClassBlueprint)
app.register_blueprint(showTaskBlueprint)

# --[[ Dashboard APIs ]]--
app.register_blueprint(getCalendarBlueprint)
app.register_blueprint(getDailyMessagesBlueprint)
app.register_blueprint(getTimetableBlueprint)
app.register_blueprint(getTodayBlueprint)
app.register_blueprint(getUserInfoBlueprint)
app.register_blueprint(getWeatherBlueprint)

# --[[ Class APIs ]]--
app.register_blueprint(getClassesBlueprint)
app.register_blueprint(getTaskRubricBlueprint)
app.register_blueprint(getResultInfoBlueprint)

# --[[ Setting APIs ]]--
app.register_blueprint(getMusicBlueprint)
app.register_blueprint(setMusicBlueprint)
app.register_blueprint(getSessionSettingBlueprint)
app.register_blueprint(getThemeBlueprint)
app.register_blueprint(setThemeBlueprint)

# --[[ Profile APIs ]]--
app.register_blueprint(getCommendationsBlueprint)
app.register_blueprint(getDashboardDataBlueprint)
app.register_blueprint(getStudentProfileDetailsBlueprint)
app.register_blueprint(getStudentProfileImageBlueprint)
app.register_blueprint(getReportsBlueprint)

# --[[ Support API ]]--
app.register_blueprint(supportBlueprint)

# --[[ Start ]]--
#       --[[ PRODUCTION ]]--
if __name__ == "__main__":
    from waitress import serve
    logger.info("nSimon Started!")
    serve(app, host="0.0.0.0", port=8080)

#       --[[ TESTING ]]--
# if __name__ == "__main__":
#     app.run(debug=True, port=8080)
