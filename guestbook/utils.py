import os
import json
import datetime

from sqlalchemy.ext.declarative import DeclarativeMeta

import guestbook  # for path stuff


def absolute_path_in_app(relpath):
    """
    Return the given relative path made absolute, assuming that it's
    within the application package.

    NOTE there might be a better way to do this using Pyramid's asset
    packaging mechanisms.
    """
    app_root = os.path.abspath(os.path.dirname(guestbook.__file__))
    return os.path.abspath(os.path.join(app_root, relpath))


def to_json_filter(value):
    """
    Output the given value serialized as JSON using json.dumps.

    NOTE this is *not* XSS-safe and shouldn't be used in production!
    """
    return json.dumps(value, cls=ORMEncoder)


class ORMEncoder(json.JSONEncoder):
    """
    A custom JSON encoder for ORM objects -- uses the `__json__`
    method if one is defined.
    """
    def default(self, obj):
        if hasattr(obj, '__json__'):
            return obj.__json__()
