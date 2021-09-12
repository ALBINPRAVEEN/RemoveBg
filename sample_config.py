import os

class Config(object):
    # get a token from @BotFather
    TG_BOT_TOKEN = os.environ.get("TOKEN", None)
    # required for running on Heroku
    URL = os.environ.get("URL", "")
    PORT = int(os.environ.get("PORT", 5000))
    # get a token from ChatBase.com for analytics
    CBTOKEN = os.environ.get('CBTOKEN', None)
    # Python3 ReQuests CHUNK SIZE
    CHUNK_SIZE = 10281
    # ReMove.BG API Key
    REM_BG_API_KEY = os.environ.get("REM_BG_API_KEY", None)
    # temporary download location
    DOWNLOAD_LOCATION = os.environ.get("DOWNLOAD_LOCATION", "./DOWNLOADS")
