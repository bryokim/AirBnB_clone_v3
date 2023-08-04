#!/usr/bin/python3
"""View for the State objects.

Routes:
    - /states => methods=[GET, POST]
    - /states/<state_id> => methods=[GET, PUT, DELETE]
"""

from flask import abort, request, jsonify, make_response

from api.v1.views import app_views
from models import storage
from models.state import State


@app_views.route("/states", strict_slashes=False)
def get_states():
    """Retrieves the list of all State objects.

    Returns:
        list: List of all State objects dictionaries.
    """
    states = storage.all(State)
    return jsonify([state.to_dict() for state in states.values()])


@app_views.route("/states/<state_id>", strict_slashes=False)
def get_state(state_id):
    """Retrieves a State object with the given state_id.

    Errors raised:
        - 404 (msg: "Not found") -> If the state_id is not
            linked to any State object.

    Args:
        state_id (str): State ID as from the URL.

    Returns:
        dict: Dictionary of the requested State.
        Status code: 200.
    """
    state = storage.get(State, state_id)

    if state:
        return jsonify(state.to_dict())
    else:
        abort(404)


@app_views.route("/states/<state_id>", methods=["DELETE"],
                 strict_slashes=False)
def delete_state(state_id):
    """Deletes a State object with the given state_id.

    Errors raised:
        - 404 (msg: "Not found") -> If the state_id is not
            linked to any State object.

    Args:
        state_id (str): State ID as from the URL.

    Returns:
        tuple: Tuple of an empty dictionary and the status code.
        Status code: 200 if successful, 404 otherwise.
    """
    state = storage.get(State, state_id)

    if state:
        storage.delete(state)
        storage.save()
        return make_response(jsonify({}), 200)
    else:
        abort(404)


@app_views.route("/states", methods=["POST"], strict_slashes=False)
def create_state():
    """Creates a new State.

    Errors raised:
        - 400 (msg: "Not a JSON") -> If HTTP request body is
            not valid JSON.
        - 400 (msg: "Missing name") -> If the data from the
            HTTP request does not contain the key name.
        - 404 (msg: "Not found") -> If state_id is not linked
            to any State object.

    Returns:
        tuple: Tuple of the dictionary of the newly created State and
            the status code.
        Status code: 201 if successful, 400/404 if unsuccessful.
    """
    data = request.get_json(silent=True)
    if data and data.get("name", None):
        new_state = State(**data)
        new_state.save()
        return make_response(jsonify(new_state.to_dict()), 201)
    elif data and not data.get("name", None):
        abort(400, description="Missing name")
    else:
        abort(400, description="Not a JSON")


@app_views.route("/states/<state_id>", methods=["PUT"], strict_slashes=False)
def update_state(state_id):
    """Updates a State Object.

    Ignored keys:
        - id
        - created_at
        - updated_at

    Errors raised:
        - 400 (msg: "Not a JSON") -> Raised if HTTP request
            body is not valid JSON.
        - 404 (msg: "Not found") -> Raised if state_id is not
            linked to any State object.

    Args:
        state_id (str): State ID as from the URL.

    Returns:
        dict: If no errors are raised a dictionary of
            the updated State as JSON is returned.
        Status code: 200.
    """
    state = storage.get(State, state_id)
    data = request.get_json(silent=True)

    ignored_keys = ["id", "created_at", "updated_at"]
    if state and data:
        for key, value in data.items():
            if key not in ignored_keys:
                setattr(state, key, value)
        state.save()
        return make_response(jsonify(state.to_dict()), 200)
    elif not state:
        abort(404)
    elif not data:
        abort(400, description="Not a JSON")
