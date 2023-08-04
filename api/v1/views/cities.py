#!/usr/bin/python3
"""View for the City object.

Routes:
    - /states/<state_id>/cities => methods[GET, POST]
    - /cities/<city_id> => methods[GET, DELETE, PUT]
"""

from flask import abort, request, jsonify, make_response

from api.v1.views import app_views
from models import storage
from models.city import City
from models.state import State


@app_views.route("/states/<state_id>/cities", strict_slashes=False)
def get_cities(state_id):
    """Retrieve the list of City objects of a State.

    Args:
        state_id (str): State ID.

    Errors raised:
        - 404 (msg: "Not found") -> If the state_id is not
            linked to any State object.

    Returns:
        list: List of all City objects' dictionaries in the given state.
    """
    state = storage.get(State, state_id)

    if state:
        cities = state.cities
        return jsonify([city.to_dict() for city in cities])
    else:
        abort(404)


@app_views.route("/cities/<city_id>", strict_slashes=False)
def get_city(city_id):
    """Retrieves a City object.

    Args:
        city_id (str): City ID.

    Errors raised:
        - 404 (msg: "Not found") -> If the city_id is not
            linked to any City object.

    Returns:
        dict: Dictionary of the requested City.
    """
    city = storage.get(City, city_id)

    if city:
        return jsonify(city.to_dict())
    else:
        abort(404)


@app_views.route("/cities/<city_id>", methods=["DELETE"],
                 strict_slashes=False)
def delete_city(city_id):
    """Deletes a City object.

    Args:
        city_id: City ID.

    Errors raised:
        - 404 (msg: "Not found") -> If the city_id is not
            linked to any City object.

    Returns:
        tuple: Tuple of an empty dictionary and the status code.
    """
    city = storage.get(City, city_id)

    if city:
        storage.delete(city)
        storage.save()
        return make_response(jsonify({}), 200)
    else:
        abort(404)


@app_views.route("/states/<state_id>/cities", methods=["POST"],
                 strict_slashes=False)
def add_city(state_id):
    """Creates a City.

    Args:
        state_id (str): State ID.

    Errors raised:
        - 404 (msg: "Not found") -> If the state_id is not
            linked to any State object.
        - 400 (msg: "Not a JSON") -> If HTTP request body is
            not valid JSON.
        - 400 (msg: "Missing name") -> If the data from the
            HTTP request does not contain the key name.

    Returns:
        tuple: Tuple of the dictionary of the newly created City
            and the status code.
    """
    data = request.get_json(silent=True)
    state = storage.get(State, state_id)

    if data and data.get("name", None) and state:
        data["state_id"] = state_id
        city = City(**data)
        city.save()
        return make_response(jsonify(city.to_dict()), 201)
    elif not state:
        abort(404)
    elif data and not data.get("name", None):
        abort(400, description="Missing name")
    elif not data:
        abort(400, description="Not a JSON")


@app_views.route("/cities/<city_id>", methods=["PUT"], strict_slashes=False)
def update_city(city_id):
    """Updates a City object.

    Args:
        city_id (str): City ID.

    Ignored keys:
        - id
        - state_id
        - created_at
        - updated_at

    Errors raised:
        - 404 (msg: "Not found") -> If the city_id is not
            linked to any City object.
        - 400 (msg: "Not a JSON") -> If HTTP request body is
            not valid JSON.

    Returns:
        tuple: Tuple of the dictionary of the updated City
            and the status code.
    """
    city = storage.get(City, city_id)
    data = request.get_json(silent=True)

    ignored_keys = ["created_at", "updated_at", "id", "state_id"]
    if city and data:
        for key, value in data.items():
            if key not in ignored_keys:
                setattr(city, key, value)
                city.save()
        return make_response(jsonify(city.to_dict()), 200)
    elif not city:
        abort(404)
    elif not data:
        abort(400, description="Not a JSON")
