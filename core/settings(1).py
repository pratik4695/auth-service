import os
import sys
from os.path import isfile

import yaml
from django.core.exceptions import ImproperlyConfigured


if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    from collections.abc import MutableMapping
else:
    from collections import MutableMapping


def flatten(d, parent_key="", sep="."):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


class AppSettings:
    _possible_config_paths = {
        "{}/config/config.yml".format(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "/etc/app/config/config.yml"
    }
    _possible_secret_paths = {
        "{}/config/secrets.yml".format(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "/etc/app/secret/secrets.yml"
    }

    def __init__(self):
        print("Initialised settings", flush=True)
        self.config = flatten(self._read_config())
        self.secrets = flatten(self._read_secret())

    def _read_config(self):
        file_location = None
        for _ in self._possible_config_paths:
            if isfile(_):
                file_location = _
                break
        if not file_location:
            raise ImproperlyConfigured("Missing config file.")
        fp = open(file_location)
        contents = fp.read()
        fp.close()
        return yaml.load(contents, Loader=yaml.SafeLoader)

    def _read_secret(self):
        file_location = None
        for _ in self._possible_secret_paths:
            if isfile(_):
                file_location = _
                break
        if not file_location:
            raise ImproperlyConfigured("Missing secret file.")
        fp = open(file_location)
        contents = fp.read()
        fp.close()
        return yaml.load(contents, Loader=yaml.SafeLoader)

    def get(self, key: str, mandatory: bool = False, default=None):
        if mandatory and not self.config.get(key) and not self.secrets.get(key):
            raise ImproperlyConfigured("Missing required settings {}".format(key))
        return self.config.get(key) or self.secrets.get(key) or default

    @staticmethod
    def get_env(key: str, mandatory: bool = False, default=None):
        if mandatory and not os.environ.get(key):
            raise ImproperlyConfigured("Missing required environment variable: {}".format(key))
        return os.environ.get(key) or default
