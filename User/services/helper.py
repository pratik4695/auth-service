import json
import re
import secrets
import string

# from oauth2_provider.views import TokenView

from django.conf import settings

PROFANE_WORDS_LIST = settings.PROFANE_WORDS_LIST



# def get_password_oauth_token(request, **kwargs):
#     """
#     This function will generate the oauth token from password grant type
#     :param user_name: contain email as username
#     :param password: can be raw password as well hash password
#     :param client_id: application client_id
#     :return: will return token dictionary and status code
#     """
#     client_id = request.data.get("client_id", None)
#     if client_id is None:
#         raise ValueError("client_id is Missing")
#     request.data["grant_type"] = "password"
#     request.data.update(kwargs)
#     # Changed content-type, because its required for oauth-provider
#     request.META["CONTENT_TYPE"] = "application/x-www-form-urlencoded"
#     url, header, body, status = TokenView().create_token_response(request)
#     return json.loads(body), status


def is_email_or_mobile(input_value):
    # assert isinstance(input_value, str), "input_value should be a string or unicode"
    if not input_value:
        return None
    if re.match('[^@]+@[^@]+\.[^@]+', input_value):
        return "email"
    elif re.match('\d{10}', input_value):
        return "mobile"
    else:
        return None


def contains_profane(word: str, is_email=False):
    word = word.lower().strip()
    if is_email:
        words = set(x for x in word.split('@'))
    else:
        words = set(x for x in word.split())
        words.add(word)

    profane_set = set(x for x in PROFANE_WORDS_LIST)

    matched_words = profane_set.intersection(words)
    if len(matched_words):
        return True
    return False


def generate_random_password(length: int) -> str:
    res = ''.join(secrets.choice(string.ascii_letters + string.digits)
                  for i in range(length))
    return res
