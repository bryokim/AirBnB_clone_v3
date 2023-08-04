#!/usr/bin/python3
"""View for the User object.

Routes:
    - /users => methods[GET, POST]
    - /users/<user_id> => methods[GET, DELETE, PUT]
"""

from flask import abort, request, jsonify, make_response
import hashlib

from api.v1.views import app_views
from models import storage
from models.user import User


@app_views.route("/users", strict_slashes=False)
def get_users():
    """Retrieves the list of all User objects.

    Returns:
        list: List of all the User objects' dictionaries.
    """
    users = storage.all(User)
    return jsonify([user.to_dict() for user in users.values()])


@app_views.route("/users/<user_id>", strict_slashes=False)
def get_user(user_id):
    """Retrieves an User object with the given user_id.

    Errors raised:
        - 404 (msg: "Not found") -> If the User_id is not
            linked to any User object.

    Args:
        User_id (str): User ID as from the URL.

    Returns:
        dict: Dictionary of the requested User.
        Status code: 200.
    """
    user = storage.get(User, user_id)

    if user:
        return jsonify(user.to_dict())
    else:
        abort(404)


@app_views.route("/users/<user_id>", methods=["DELETE"], strict_slashes=False)
def delete_user(user_id):
    """Deletes a User object with the given user_id.

    Errors raised:
        - 404 (msg: "Not found") -> If the user_id is not
            linked to any User object.

    Args:
        user_id (str): User ID as from the URL.

    Returns:
        tuple: Tuple of an empty dictionary and the status code.
        Status code: 200 if successful, 404 otherwise.
    """
    user = storage.get(User, user_id)

    if user:
        storage.delete(user)
        storage.save()
        return make_response(jsonify({}), 200)
    else:
        abort(404)


@app_views.route("/users", methods=["POST"], strict_slashes=False)
def create_user():
    """Creates a new User.

    Errors raised:
        - 400 (msg: "Not a JSON") -> If HTTP request body is
            not valid JSON.
        - 400 (msg: "Missing email") -> If the data from the
            HTTP request does not contain the key email.
        - 400 (msg: "Missing password") -> If the data from the
            HTTP request does not contain the key password.
        - 404 (msg: "Not found") -> If user_id is not linked
            to any User object.

    Returns:
        tuple: Tuple of the dictionary of the newly created User
            and the status code.
        Status code: 201 if successful, 400/404 if unsuccessful.
    """
    data = request.get_json(silent=True)

    if data and data.get("email") and data.get("password"):
        user = User(**data)
        user.save()
        return make_response(jsonify(user.to_dict()), 201)
    elif data and not data.get("email"):
        abort(400, description="Missing email")
    elif data and not data.get("password"):
        abort(400, description="Missing password")
    elif not data:
        abort(400, description="Not a JSON")


@app_views.route("/users/<user_id>", methods=["PUT"], strict_slashes=False)
def update_user(user_id):
    """Updates an User Object.

    Ignored keys:
        - id
        - created_at
        - updated_at
        - email

    Errors raised:
        - 400 (msg: "Not a JSON") -> Raised if HTTP request
            body is not valid JSON.
        - 404 (msg: "Not found") -> Raised if user_id is not
            linked to any User object.

    Args:
        User_id (str): User ID as from the URL.

    Returns:
        tuple: If no errors are raised a tuple of the dictionary
            of the updated User and the status code.
        Status code: 200.
    """
    data = request.get_json(silent=True)
    user = storage.get(User, user_id)

    ignore_keys = ["id", "created_at", "updated_at", "email"]
    if user and data:
        for key, value in data.items():
            if key == "password":
                value = value.encode("ascii")
                setattr(user, key, hashlib.md5(value).hexdigest())
            elif key not in ignore_keys:
                setattr(user, key, value)
        user.save()
        return make_response(jsonify(user.to_dict()), 200)
    elif not user:
        abort(404)
    elif not data:
        abort(400, description="Not a JSON")
