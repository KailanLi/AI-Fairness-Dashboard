"""Flask config."""
import os
from os import environ, path

basedir = os.path.abspath(os.path.dirname(__file__))



class Config:
    """Flask configuration variables."""

    # General Config
    FLASK_APP = "wsgi.py"
    FLASK_ENV = environ.get("FLASK_ENV")
    # $env:SECRET_KEY="123"
    SECRET_KEY = environ.get("SECRET_KEY")

    # Assets
    LESS_BIN = environ.get("LESS_BIN")
    ASSETS_DEBUG = environ.get("ASSETS_DEBUG")
    LESS_RUN_IN_DEBUG = environ.get("LESS_RUN_IN_DEBUG")

    # Static Assets
    STATIC_FOLDER = "static"
    TEMPLATES_FOLDER = "templates"
    COMPRESSOR_DEBUG = environ.get("COMPRESSOR_DEBUG")
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.path.join(basedir, 'session_files')  # Directory to store session files
    SESSION_PERMANENT = False  # Session data should be deleted when the browser closes
    SESSION_USE_SIGNER = True  # Sign the session cookie for added security
    SESSION_KEY_PREFIX = 'session:'  # Prefix for storing session data
    SESSION_FILE_THRESHOLD = 10  # Maximum number of items to store before the session starts removing the oldest