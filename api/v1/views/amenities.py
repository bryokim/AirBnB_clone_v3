#!/usr/bin/python3
"""View for the Amenity object.

Routes:
    - /amenities => methods[GET, POST]
    - /amenities/<amenity_id> => methods[GET, DELETE, PUT]
"""

from flask import abort, request, jsonify, make_response

from api.v1.views import app_views
from models import storage
from models.amenity import Amenity


@app_views.route("/amenities", strict_slashes=False)
def get_amenities():
    """Retrieves the list of all Amenity objects.

    Returns:
        list: List of all the Amenity objects' dictionaries.
    """
    amenities = storage.all(Amenity)
    return jsonify([amenity.to_dict() for amenity in amenities.values()])


@app_views.route("/amenities/<amenity_id>", strict_slashes=False)
def get_amenity(amenity_id):
    """Retrieves an Amenity object with the given amenity_id.

    Errors raised:
        - 404 (msg: "Not found") -> If the amenity_id is not
            linked to any Amenity object.

    Args:
        amenity_id (str): Amenity ID as from the URL.

    Returns:
        dict: Dictionary of the requested Amenity.
        Status code: 200.
    """
    amenity = storage.get(Amenity, amenity_id)

    if amenity:
        return jsonify(amenity.to_dict())
    else:
        abort(404)


@app_views.route("/amenities/<amenity_id>", methods=["DELETE"],
                 strict_slashes=False)
def delete_amenity(amenity_id):
    """Deletes a Amenity object with the given amenity_id.

    Errors raised:
        - 404 (msg: "Not found") -> If the amenity_id is not
            linked to any Amenity object.

    Args:
        amenity_id (str): Amenity ID as from the URL.

    Returns:
        tuple: Tuple of an empty dictionary and the status code.
        Status code: 200 if successful, 404 otherwise.
    """
    amenity = storage.get(Amenity, amenity_id)

    if amenity:
        storage.delete(amenity)
        storage.save()
        return make_response(jsonify({}), 200)
    else:
        abort(404)


@app_views.route("/amenities", methods=["POST"], strict_slashes=False)
def create_amenity():
    """Creates a new Amenity.

    Errors raised:
        - 400 (msg: "Not a JSON") -> If HTTP request body is
            not valid JSON.
        - 400 (msg: "Missing name") -> If the data from the
            HTTP request does not contain the key name.
        - 404 (msg: "Not found") -> If amenity_id is not linked
            to any Amenity object.

    Returns:
        tuple: Tuple of the dictionary of the newly created Amenity
            and the status code.
        Status code: 201 if successful, 400/404 if unsuccessful.
    """
    data = request.get_json(silent=True)

    if data and data.get("name", None):
        amenity = Amenity(**data)
        amenity.save()
        return make_response(jsonify(amenity.to_dict()), 201)
    elif not data:
        abort(400, description="Not a JSON")
    elif data and not data.get("name", None):
        abort(400, description="Missing name")


@app_views.route("/amenities/<amenity_id>", methods=["PUT"],
                 strict_slashes=False)
def update_amenity(amenity_id):
    """Updates an Amenity Object.

    Ignored keys:
        - id
        - created_at
        - updated_at

    Errors raised:
        - 400 (msg: "Not a JSON") -> Raised if HTTP request
            body is not valid JSON.
        - 404 (msg: "Not found") -> Raised if amenity_id is not
            linked to any Amenity object.

    Args:
        amenity_id (str): Amenity ID as from the URL.

    Returns:
        tuple: If no errors are raised a tuple of the dictionary
            of the updated Amenity and the status code.
        Status code: 200.
    """
    amenity = storage.get(Amenity, amenity_id)
    data = request.get_json(silent=True)

    ignored_keys = ["id", "created_at", "updated_at"]
    if amenity and data:
        for key, value in data.items():
            if key not in ignored_keys:
                setattr(amenity, key, value)
                amenity.save()
        return make_response(jsonify(amenity.to_dict()), 200)
    elif not data:
        abort(400, description="Not a JSON")
    else:
        abort(404)
