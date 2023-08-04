#!/usr/bin/python3
"""Default views

Routes:
    - /status => methods=[GET]
    - /stats => methods=[GET]

"""

from api.v1.views import app_views
from flask import jsonify

from models import storage
from models.amenity import Amenity
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User

classes = {
    "amenity": Amenity,
    "city": City,
    "place": Place,
    "review": Review,
    "state": State,
    "user": User,
}


@app_views.route("/status")
def get_status():
    """Return the status of the api.

    Returns:
        Response: Response containing the status.
    """
    return {"status": "OK"}


@app_views.route("/stats")
def get_stats():
    """Retrieves the number of each objects by type.

    Returns:
        Response: Response containing the number of objects
            of each type.
    """
    stats = [storage.count(cls) for cls in classes.values()]

    return jsonify(
        {
            "amenities": stats[0],
            "cities": stats[1],
            "places": stats[2],
            "reviews": stats[3],
            "states": stats[4],
            "users": stats[5],
        }
    )
