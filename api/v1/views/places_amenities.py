#!/usr/bin/python3
"""View for the link between Place and Amenity objects.

Routes:
    - /places/<place_id>/amenities => methods[GET]
    - /places/place_id>/amenities/<amenity_id> => methods[DELETE, POST]
"""

from flask import abort, jsonify, make_response

from api.v1.views import app_views
from models import storage, storage_t
from models.amenity import Amenity
from models.place import Place


@app_views.route("/places/<place_id>/amenities", strict_slashes=False)
def get_amenities_for_place(place_id):
    """Retrieves the list of all Amenity objects of a Place.

    Args:
        - place_id (str): Place ID.

    Returns:
        list: List of all amenities of a given place.
    """
    place = storage.get(Place, place_id)

    if place:
        amenities = place.amenities
        return jsonify([amenity.to_dict() for amenity in amenities])
    else:
        abort(404)


@app_views.route("/places/<place_id>/amenities/<amenity_id>",
                 methods=["DELETE"], strict_slashes=False)
def delete_amenity_from_place(place_id, amenity_id):
    """Deletes an Amenity object to a Place.

    Args:
        - place_id (str): Place ID.
        - amenity_id (str): Amenity ID.

    Returns:
        tuple: Tuple of an empty dictionary and status code.
    """
    place = storage.get(Place, place_id)
    amenity = storage.get(Amenity, amenity_id)

    if place and amenity:
        try:
            if storage_t == "db":
                place.amenities.remove(amenity)
            else:
                place.amenity_ids.remove(amenity.id)
        except ValueError:
            # If the amenity is not linked to the Place.
            abort(404)

        place.save()
        return make_response(jsonify({}), 200)
    elif not place or not amenity:
        abort(404)


@app_views.route("/places/<place_id>/amenities/<amenity_id>", methods=["POST"],
                 strict_slashes=False)
def add_amenity_to_place(place_id, amenity_id):
    """Link an Amenity object to a Place.
    If the Amenity was already linked then status code of 200
    is returned instead of 201.
    The Amenity is returned in both cases.

    Args:
        - place_id (str): Place ID.
        - amenity_id (str): Amenity ID.

    Returns:
        Tuple: Tuple of the newly linked Amenity and the status code.
    """
    place = storage.get(Place, place_id)
    amenity = storage.get(Amenity, amenity_id)

    if place and amenity and amenity not in place.amenities:
        if storage_t == "db":
            place.amenities.append(amenity)
        else:
            place.amenities = amenity
        place.save()
        return make_response(jsonify(amenity.to_dict()), 201)
    elif not place or not amenity:
        abort(404)
    elif amenity and amenity in place.amenities:
        return make_response(jsonify(amenity.to_dict()), 200)
