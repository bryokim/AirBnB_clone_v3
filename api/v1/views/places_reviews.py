#!/usr/bin/python3
"""View for the Review objects.

Routes:
    - /places/<place_id>/reviews => methods[GET, POST]
    - /reviews/<review_id> => methods[GET, DELETE, PUT]
"""

from flask import abort, request, jsonify, make_response

from api.v1.views import app_views
from models import storage
from models.place import Place
from models.review import Review
from models.user import User


@app_views.route("/places/<place_id>/reviews", strict_slashes=False)
def get_reviews(place_id):
    """Retrieves the list of Review objects of a place.

    Args:
        place_id (str): Place ID.

    Errors raised:
        - 404 (msg: "Not found") -> If the place_id is not
            linked to any Place object.

    Returns:
        list: List of all Review objects dictionaries in the
            given Place.
    """
    place = storage.get(Place, place_id)

    if place:
        reviews = place.reviews
        return jsonify([review.to_dict() for review in reviews])
    else:
        abort(404)


@app_views.route("/reviews/<review_id>", strict_slashes=False)
def get_review(review_id):
    """Retrieves a Review object.

    Args:
        review_id (str): Review ID.

    Errors raised:
        - 404 (msg: "Not found") -> If the review_id is not
            linked to any review object.

    Returns:
        dict: Dictionary of the requested Review.
    """
    review = storage.get(Review, review_id)

    if review:
        return jsonify(review.to_dict())
    else:
        abort(404)


@app_views.route("/reviews/<review_id>", methods=["DELETE"],
                 strict_slashes=False)
def delete_review(review_id):
    """Deletes a Review object.

    Args:
        review_id: Review ID.

    Errors raised:
        - 404 (msg: "Not found") -> If the review_id is not
            linked to any Review object.

    Returns:
        tuple: Tuple of an empty dictionary and the status code.
    """
    review = storage.get(Review, review_id)

    if review:
        storage.delete(review)
        storage.save()
        return make_response(jsonify({}), 200)
    else:
        abort(404)


@app_views.route("/places/<place_id>/reviews", methods=["POST"],
                 strict_slashes=False)
def create_review(place_id):
    """Creates a Review.

    Args:
        place_id (str): Place ID.

    Errors raised:
        - 404 (msg: "Not found") -> If the place_id is not
            linked to any Place object.
        - 404 (msg: "Not found") -> If the user_id  in data is not
            linked to any User object.
        - 400 (msg: "Not a JSON") -> If HTTP request body is
            not valid JSON.
        - 400 (msg: "Missing text") -> If the data from the
            HTTP request does not contain the key text.
        - 400 (msg: "Missing user_id") -> If the data from the
            HTTP request does not contain the key user_id.

    Returns:
        tuple: Tuple of the dictionary of the newly created Review
            and the status code.
    """
    place = storage.get(Place, place_id)
    data = request.get_json(silent=True)
    user = data and storage.get(User, data.get("user_id"))

    if place and user and data and data.get("text"):
        data["place_id"] = place_id
        review = Review(**data)
        review.save()
        return make_response(jsonify(review.to_dict()), 201)
    elif data and not data.get("text"):
        abort(400, description="Missing text")
    elif data and not data.get("user_id"):
        abort(400, description="Missing user_id")
    elif not data:
        abort(400, description="Not a JSON")
    elif not place or not user:
        abort(404)


@app_views.route("/reviews/<review_id>", methods=["PUT"], strict_slashes=False)
def update_review(review_id):
    """Updates a Review object.

    Args:
        review_id (str): Review ID.

    Ignored keys:
        - id
        - place_id
        - user_id
        - created_at
        - updated_at

    Errors raised:
        - 404 (msg: "Not found") -> If the review_id is not
            linked to any Review object.
        - 400 (msg: "Not a JSON") -> If HTTP request body is
            not valid JSON.

    Returns:
        tuple: Tuple of the dictionary of the updated Review
            and the status code.
    """
    review = storage.get(Review, review_id)
    data = request.get_json(silent=True)

    ignored_keys = ["id", "created_at", "updated_at", "user_id", "place_id"]
    if review and data:
        for key, value in data.items():
            if key not in ignored_keys:
                setattr(review, key, value)
                review.save()
        return make_response(jsonify(review.to_dict()), 200)
    elif not data:
        abort(400, description="Not a JSON")
    elif not review:
        abort(404)
