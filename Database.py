import mysql.connector
from mysql.connector import pooling
from configparser import ConfigParser
import bcrypt
from cryptography.fernet import Fernet
import logging
from io import BytesIO
from PIL import Image
import Simon
import requests
import json


# LOGS
logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


def read_db_config(filename="config.ini", section="database"):
    parser = ConfigParser()
    parser.read(filename)
    db_config = {}

    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db_config[item[0]] = item[1]
    else:
        raise Exception(f"{section} not found in the {filename} file")

    return db_config


def read_encryption_key(filename="config.ini", section="encryption"):
    parser = ConfigParser()
    parser.read(filename)

    if parser.has_section(section):
        return parser.get(section, "encryption_key")
    else:
        raise Exception(f"{section} not found in the {filename} file")


db_config = read_db_config()
encryption_key = read_encryption_key()

fernet = Fernet(encryption_key)


def encrypt_cookie(cookie):
    return fernet.encrypt(cookie.encode("utf-8")).decode("utf-8")


def decrypt_cookie(encrypted_cookie):
    return fernet.decrypt(encrypted_cookie.encode("utf-8")).decode("utf-8")


def hash_password(password):
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password


def verify_password(hashed_password, password):
    # Verify if the entered password matches the hashed password
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password)


# User Management
def databaseCheckUser(username, password):
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, password, cookie FROM users WHERE username = %s",
            (username,),
        )
        result = cursor.fetchone()

        if result is not None:
            db_username, db_password, cookie = result
            if verify_password(db_password, password):
                cookie = decrypt_cookie(cookie)
                return 200, cookie
            else:
                return 403
        else:
            return 404
    except mysql.connector.Error as e:
        logger.error(f"Error checking user in the database: {e}")
        return 404
    finally:
        cursor.close()
        conn.close()


def databaseFindUser(username):
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, password, cookie FROM users WHERE username = %s",
            (username,),
        )
        result = cursor.fetchone()

        if result is not None:
            return 200
        else:
            return 404
    except mysql.connector.Error as e:
        logger.error(f"Error checking user in the database: {e}")
        return 404
    finally:
        cursor.close()
        conn.close()


def databaseAddUser(username, password, cookie):
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()
        hashed_password = hash_password(password)
        encrypted_cookie = encrypt_cookie(cookie)
        cursor.execute(
            "INSERT INTO users (username, password, cookie, studentImage, theme, showMusicLessons, showSessionNames, showChangelog, notifications, notes, sharedTimetables) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                username,
                hashed_password,
                encrypted_cookie,
                "",
                "light",
                "true",
                "false",
                "true",
                "{}",
                "{}",
                "{}",
            ),
        )
        conn.commit()
        logger.info(f"User '{username}' added to the database.")
        cursor.execute("UPDATE statistics SET users = users + 1")
        conn.commit()
    except mysql.connector.Error as e:
        logger.error(f"Error adding user to the database: {e}")
    finally:
        cursor.close()
        conn.close()


# Images
def databaseCheckImage(username):
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT studentImage FROM users WHERE username = %s", (username,)
        )
        result = cursor.fetchone()

        if result is not None:
            image_data = result[0]
            if image_data:
                try:
                    # Attempt to open the image
                    image = Image.open(BytesIO(image_data))
                    return image_data
                except Exception as e:
                    # Handle any exception and log it
                    logger.error(f"Error opening image: {e}")
                    return None  # Invalid or unrecognized image data
            else:
                return None  # Empty image data
        else:
            return None  # Image not found in the database
    except mysql.connector.Error as e:
        logger.error(f"Error checking image in the database: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def databaseAddImage(username, cookie):
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT studentImage FROM users WHERE username = %s", (username,)
        )
        result = cursor.fetchone()

        cookies = {"adAuthCookie": cookie}
        image_url = Simon.getSimonStudentImageURL(cookie)

        if image_url:
            cookies = {"adAuthCookie": cookie}
            image_data = requests.get(image_url, cookies=cookies).content

            cursor.execute(
                "UPDATE users SET studentImage = %s WHERE username = %s",
                (image_data, username),
            )
            conn.commit()
            return image_data

    except mysql.connector.Error as e:
        logger.error(f"Error storing image in the database: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


# Settings
def databaseGetTheme(username):
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT theme FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        theme = result[0] if result else None

        return theme

    except mysql.connector.Error as e:
        logger.error(f"Error storing image in the database: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def databaseChangeTheme(username, theme):
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET theme = %s WHERE username = %s", (theme, username)
        )
        conn.commit()

        return 200

    except mysql.connector.Error as e:
        logger.error(f"Error storing theme in the database: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def databaseGetMusic(username):
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT showMusicLessons FROM users WHERE username = %s", (username,)
        )
        result = cursor.fetchone()

        music = result[0] if result else "true"

        return music

    except mysql.connector.Error as e:
        logger.error(f"Error finding showMusicLessons setting in the database: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def databaseChangeMusic(username, music):
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET showMusicLessons = %s WHERE username = %s",
            (music, username),
        )
        conn.commit()

        return 200

    except mysql.connector.Error as e:
        logger.error(f"Error storing music setting in the database: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def databaseGetSession(username):
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT showSessionNames FROM users WHERE username = %s", (username,)
        )
        result = cursor.fetchone()

        sessionName = result[0] if result else "true"

        return sessionName

    except mysql.connector.Error as e:
        logger.error(f"Error finding Session setting in the database: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def databaseChangeSession(username, sessionName):
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET showSessionNames = %s WHERE username = %s",
            (sessionName, username),
        )
        conn.commit()

        return 200

    except mysql.connector.Error as e:
        logger.error(f"Error storing Session setting in the database: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def databaseGetChangelog(username):
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT showChangelog FROM users WHERE username = %s", (username,)
        )
        result = cursor.fetchone()

        changelog = result[0] if result else "true"

        return changelog

    except mysql.connector.Error as e:
        logger.error(f"Error finding showChangelog setting in the database: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def databaseChangeChangelog(username, changelog):
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET showChangelog = %s WHERE username = %s",
            (changelog, username),
        )
        conn.commit()

        return 200

    except mysql.connector.Error as e:
        logger.error(f"Error storing changelog setting in the database: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


# Notes
def databaseGetNotes(username):
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT notes FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        notes = result[0] if result else "{}"

        return json.loads(notes)

    except mysql.connector.Error as e:
        logger.error(f"Error find user notes in the database: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def databaseChangeNotes(username, notes):
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET notes = %s WHERE username = %s",
            (json.dumps(notes), username),
        )
        conn.commit()

        return 200

    except mysql.connector.Error as e:
        logger.error(f"Error storing notes in the database: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def databaseGetSharedTimetables(username):
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT sharedTimetables FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        sharedTimetables = result[0] if result else "{}"

        return json.loads(sharedTimetables)

    except mysql.connector.Error as e:
        logger.error(f"Error find user sharedTimetables in the database: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def databaseChangeSharedTimetables(username, newData):
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET sharedTimetables = %s WHERE username = %s",
            (json.dumps(newData), username),
        )
        conn.commit()

        return 200

    except mysql.connector.Error as e:
        logger.error(f"Error storing sharedTimetables in the database: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def databaseCreateShare(code, shareData):
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO shares (code, dataInfo) VALUES (%s, %s)",
            (
                code,
                json.dumps(shareData),
            ),
        )
        conn.commit()
        conn.commit()
    except mysql.connector.Error as e:
        logger.error(f"Error adding share to the database: {e}")
    finally:
        cursor.close()
        conn.close()

def databaseGetShareData(code):
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT dataInfo FROM shares WHERE code = %s", (code,)
        )
        result = cursor.fetchone()

        returnData = result[0] if result else 404

        return returnData

    except mysql.connector.Error as e:
        return 404
    finally:
        cursor.close()
        conn.close()




# Create a connection pool
db_pool = pooling.MySQLConnectionPool(pool_name="main_pool", pool_size=10, **db_config)


