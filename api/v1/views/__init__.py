#!/usr/bin/python3
"""app_views module

Blueprint:
    - app_views (url_prefix = /api/v1)

### app_views
The following views are implemented on the app_views blueprint:
    - states
    - cities
    - amenities
    - users
    - places
    - reviews

Each view has its own routes and methods that can be found in
their own files.
"""
from flask import Blueprint

app_views = Blueprint("app_views", __name__, url_prefix="/api/v1")

from api.v1.views.index import *
from api.v1.views.states import *
from api.v1.views.cities import *
from api.v1.views.amenities import *
from api.v1.views.users import *
from api.v1.views.places import *
from api.v1.views.places_reviews import *
from api.v1.views.places_amenities import *
