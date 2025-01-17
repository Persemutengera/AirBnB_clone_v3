#!/usr/bin/python3
"""
initialize the models package
"""

import os


if os.environ.get('HBNB_TYPE_STORAGE') == "db":
    from models.engine import db_storage
    storage = db_storage.DBStorage()
else:
    from models.engine import file_storage
    storage = file_storage.FileStorage()
storage.reload()
