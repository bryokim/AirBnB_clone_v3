#!/usr/bin/python3
"""View for the Place object.

Routes:
    - /cities/<city_id>/places => methods[GET, POST]
    - /places/<place_id> => methods[GET, DELETE, PUT]
    - /search_places => methods[POST]
"""

from flask import abort, request, jsonify, make_response

from api.v1.views import app_views
from models import storage
from models.city import City
from models.place import Place
from models.user import User


@app_views.route("/cities/<city_id>/places", strict_slashes=False)
def get_places(city_id):
    """Retrieve the list of Place objects of a City.

    Args:
        city_id (str): City ID.

    Errors raised:
        - 404 (msg: "Not found") -> If the city_id is not
            linked to any City object.

    Returns:
        list: List of all Place objects' dictionaries in the given city.
    """
    city = storage.get(City, city_id)

    if city:
        places = city.places
        return jsonify([place.to_dict() for place in places])
    else:
        abort(404)


@app_views.route("/places/<place_id>", strict_slashes=False)
def get_place(place_id):
    """Retrieves a Place object.

    Args:
        place_id (str): Place ID.

    Errors raised:
        - 404 (msg: "Not found") -> If the place_id is not
            linked to any Place object.

    Returns:
        dict: Dictionary of the requested Place.
    """
    place = storage.get(Place, place_id)

    if place:
        return jsonify(place.to_dict())
    else:
        abort(404)


@app_views.route("/places/<place_id>", methods=["DELETE"],
                 strict_slashes=False)
def delete_place(place_id):
    """Deletes a Place object.

    Args:
        place_id: Place ID.

    Errors raised:
        - 404 (msg: "Not found") -> If the place_id is not
            linked to any Place object.

    Returns:
        tuple: Tuple of an empty dictionary and the status code.
    """
    place = storage.get(Place, place_id)

    if place:
        storage.delete(place)
        storage.save()
        return make_response(jsonify({}), 200)
    else:
        abort(404)


@app_views.route("/cities/<city_id>/places", methods=["POST"],
                 strict_slashes=False)
def create_place(city_id):
    """Creates a Place.

    Args:
        city_id (str): City ID.

    Errors raised:
        - 404 (msg: "Not found") -> If the city_id is not
            linked to any City object.
        - 404 (msg: "Not found") -> If the user_id from data is not
            linked to any User object.
        - 400 (msg: "Not a JSON") -> If HTTP request body is
            not valid JSON.
        - 400 (msg: "Missing name") -> If the data from the
            HTTP request does not contain the key name.
        - 400 (msg: "Missing user_id") -> If the data from the
            HTTP request does not contain the key user_id.

    Returns:
        tuple: Tuple of the dictionary of the newly created Place
            and the status code.
    """
    city = storage.get(City, city_id)
    data = request.get_json(silent=True)
    user = data and storage.get(User, data.get("user_id"))

    if city and user and data and data.get("name"):
        data["city_id"] = city_id
        place = Place(**data)
        place.save()
        return make_response(jsonify(place.to_dict()), 201)
    elif data and not data.get("name"):
        abort(400, description="Missing name")
    elif data and not data.get("user_id"):
        abort(400, description="Missing user_id")
    elif not data:
        abort(400, description="Not a JSON")
    elif not city or not user:
        abort(404)


@app_views.route("/places/<place_id>", methods=["PUT"], strict_slashes=False)
def update_place(place_id):
    """Updates a Place object.

    Args:
        place_id (str): Place ID.

    Ignored keys:
        - id
        - user_id
        - city_id
        - created_at
        - updated_at

    Errors raised:
        - 404 (msg: "Not found") -> If the place_id is not
            linked to any Place object.
        - 400 (msg: "Not a JSON") -> If HTTP request body is
            not valid JSON.

    Returns:
        tuple: Tuple of the dictionary of the updated Place
            and the status code.
    """
    place = storage.get(Place, place_id)
    data = request.get_json(silent=True)
    ignored_keys = ["id", "city_id", "user_id", "created_at", "updated_at"]

    if place and data:
        for key, value in data.items():
            if key not in ignored_keys:
                setattr(place, key, value)
                place.save()
        return make_response(jsonify(place.to_dict()), 200)
    elif not data:
        abort(400, description="Not a JSON")
    elif not place:
        abort(404)


@app_views.route("/places_search", methods=["POST"])
def search_place():
    """Retrieves all Place objects depending on the JSON in
    the body of the request.

    The JSON can contain 3 optional keys:
        - states: list of State ids
        - cities: list of City ids
        - amenities: list of Amenity ids

    If the JSON body is empty or each list of all keys are empty,
    retrieves all Place objects.

    If states list is not empty, results include all Place objects
    for each State id listed.

    If cities list is not empty, results include all Place objects
    for each City id listed.

    If amenities list is not empty, search results are limited
    to only Place objects having all Amenity ids listed.
    The key amenities is exclusive, acting as a filter on the results
    generated by states and cities, or on all Place if states and cities
    are both empty or missing.

    Errors raised:
        - 400 (msg: "Not a JSON") -> If HTTP request body is
            not valid JSON.

    Returns:
        list : Place objects as per the search request.
    """
    from models.state import State

    data = request.get_json(silent=True)

    places = []

    if data is None:
        abort(400, description="Not a JSON")

    if not data or (
            data and not data.get("states") and not data.get("cities")):
        places.extend(storage.all(Place).values())

    if data and data.get("states"):
        state_ids = data.get("states")

        if len(state_ids):
            for state_id in state_ids:
                state = storage.get(State, state_id)
                if state:
                    for city in state.cities:
                        places.extend(city.places)

    if data and data.get("cities"):
        city_ids = data.get("cities")

        if len(city_ids):
            for city_id in city_ids:
                city = storage.get(City, city_id)
                if city and city.state_id not in state_ids:
                    places.extend(city.places)

    if data and data.get("amenities"):
        amenity_ids = data.get("amenities")

        if len(amenity_ids):
            valid_places = []
            for place in places:
                for amenity_id in amenity_ids:
                    if amenity_id not in place.amenity_ids:
                        valid = False
                        break
                    valid = True
                if valid:
                    valid_places.append(place)
            places = valid_places

    return jsonify([place.to_dict() for place in places])
