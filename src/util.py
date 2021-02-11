import datetime as dt
import platform
import re
from pprint import pprint

import pyperclip
import toml
from requests_oauthlib import OAuth1Session

# tweet取得系定数
USE_USER_OAUTH = False
CONSUMER_KEY = ""
CONSUMER_SECRET = ""
ACCESS_TOKEN = ""
ACCESS_TOKEN_SECRET = ""
TWEET_LIMIT = 0
DEFAULT_INTERVAL = 9999999
INTERVAL_PATTERN = []
SUPPORT_MULTIBYTE = None
TWEET_ID_BUFFER = 0
GLOBAL_PARAMS = "global"
STANDARD_SEARCH_API_TOKENS = "APIkeys"
ID_EXTRACTION_PATTERN = re.compile(".*(?P<ID>[A-F0-9]{8}) :")

# 表示系定数
MAIN_WIN_WIDTH = 80
TOP_PART_HEIGHT = 4
MIDDLE_PART_HEIGHT = 11
BOTTOM_PART_HEIGHT = 4
MAIN_WIN_HEIGHT = TOP_PART_HEIGHT + MIDDLE_PART_HEIGHT + BOTTOM_PART_HEIGHT

IS_WINDOWS = True if platform.system() == "Windows" else False

TOML_FILE_NAME = "config.toml"

JST = dt.timezone(dt.timedelta(hours=9))
configs = toml.load(TOML_FILE_NAME)


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


def get_user_access_token():

    global ACCESS_TOKEN, ACCESS_TOKEN_SECRET, configs

    request_token_url = "https://api.twitter.com/oauth/request_token"
    base_authorization_url = "https://api.twitter.com/oauth/authorize"
    access_token_url = "https://api.twitter.com/oauth/access_token"

    # oauth tokenを申請するためのトークンを取る
    oauth = OAuth1Session(CONSUMER_KEY, client_secret=CONSUMER_SECRET)
    fetch_response = oauth.fetch_request_token(request_token_url)

    resource_owner_key = fetch_response.get("oauth_token")
    resource_owner_secret = fetch_response.get("oauth_token_secret")

    authorization_url = oauth.authorization_url(base_authorization_url)
    pyperclip.copy(authorization_url)
    print("認証ページのURLをコピーしました。ブラウザでペーストして認証を行ってください")
    verifier = input("PINコードを入力してください:")

    oauth = OAuth1Session(
        CONSUMER_KEY,
        client_secret=CONSUMER_SECRET,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier,
    )
    oauth_tokens = oauth.fetch_access_token(access_token_url)
    print(oauth_tokens)

    ACCESS_TOKEN = oauth_tokens.get("oauth_token")
    ACCESS_TOKEN_SECRET = oauth_tokens.get("oauth_token_secret")
    configs["APIkeys"]["Accsess_Token"] = ACCESS_TOKEN
    configs["APIkeys"]["Accsess_Token_Secret"] = ACCESS_TOKEN_SECRET
    toml.dump(configs, open(TOML_FILE_NAME, mode="w"))
    configs = toml.load(TOML_FILE_NAME)


def setup():
    # 一般設定読み込み
    global TWEET_LIMIT, SUPPORT_MULTIBYTE, DEFAULT_INTERVAL, TWEET_ID_BUFFER, INTERVAL_PATTERN, USE_USER_OAUTH

    TWEET_LIMIT = configs.get(GLOBAL_PARAMS).get("Tweet_limit")
    SUPPORT_MULTIBYTE = configs.get(GLOBAL_PARAMS).get("Support_Muiltibyte")
    INTERVAL_PATTERN = configs.get(GLOBAL_PARAMS).get("Interval_pattern")
    DEFAULT_INTERVAL = INTERVAL_PATTERN[1]
    TWEET_ID_BUFFER = configs.get(GLOBAL_PARAMS).get("Tweet_id_buffer")

    # APIキーの設定読み込み
    global CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET

    standardAPI_token = configs.get(STANDARD_SEARCH_API_TOKENS)

    if USE_USER_OAUTH:
        ACCESS_TOKEN = standardAPI_token.get("Accsess_Token")
        ACCESS_TOKEN_SECRET = standardAPI_token.get("Accsess_Token_Secret")
    else:
        CONSUMER_KEY = standardAPI_token.get("API_Key")
        CONSUMER_SECRET = standardAPI_token.get("API_Key_Secret")


def token_check():
    RATE_LIMIT_URL = "https://api.twitter.com/1/account/settings.json"

    session = OAuth1Session(
        CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
    )
    res = session.get(RATE_LIMIT_URL)
    if res.status_code == 200:
        return True
    else:
        return False


def get_rescue_ID(tweet_text: str):
    try:
        found_id = re.match(ID_EXTRACTION_PATTERN, tweet_text).group("ID")
    except AttributeError:
        return (False, None)
    else:
        return (True, found_id)


def format_string_for_addstr(string4print: str):
    if SUPPORT_MULTIBYTE:
        return string4print
    else:
        return " ".join(list(string4print)) + " "


def gbss_addstr(window, y, x, string, attr=0):
    window.addstr(y, x, format_string_for_addstr(string), attr)


setup()

if __name__ == "__main__":
    print(CONSUMER_KEY)
    print(CONSUMER_SECRET)
    print(ACCESS_TOKEN)
    print(ACCESS_TOKEN_SECRET)
    print(TWEET_LIMIT)
    print(SUPPORT_MULTIBYTE)
    print(DEFAULT_INTERVAL)
