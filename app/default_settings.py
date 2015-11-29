DEBUG = False
TESTING = False
SQLALCHEMY_DATABASE_URI = 'sqlite:///tmp/test.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

MAX_MATCHES_PER_PAGE = 100
MATCHES_FOLDER = 'matches'

LOG_PATH = 'errors.log'

# Steam backend url
STEAM_API_BACKEND_URL = 'https://partner.steam-api.com:443/'

# https://partner.steamgames.com/documentation/auth#client_to_backend_webapi
PUBLISHER_WEBAPI_KEY = ''
