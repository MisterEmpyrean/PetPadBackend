# TEST environment configuration (use when doing unit tests)
import os

SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
SQLALCHEMY_TRACK_MODIFICATIONS = False
ERROR_404_HELP = False
