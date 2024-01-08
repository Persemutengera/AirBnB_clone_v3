#!/usr/bin/python3

""" Module for places
"""
from api.v1.views import app_views
from flask import jsonify, request, make_response, abort
from models import storage
from models.city import City
from models.place import Place


@app_views.route('/cities/<city_id>/places', strict_slashes=False)
def places_by_city(city_id):
    """
    Return places by city with the id
    """
    list_place = []
    city = storage.get("City", city_id)
    if city is not None:
        for place in city.places:
            list_place.append(place.to_dict())
        return jsonify(list_place)
    return jsonify({"error": "Not found"}), 404


@app_views.route('/places/<place_id>')
def places_by_id(place_id):
    """
    Return places by id
    """
    place = storage.get("Place", place_id)
    if place is not None:
        return jsonify(place.to_dict())
    return jsonify({"error": "Not found"}), 404


@app_views.route('/places/<place_id>', methods=['DELETE'])
def del_place(place_id):
    """
    Delete a place by id
    """
    place = storage.get("Place", place_id)
    if place is not None:
        storage.delete(place)
        storage.save()
        return jsonify({}), 200
    return jsonify({"error": "Not found"}), 404


@app_views.route(
    '/cities/<city_id>/places',
    strict_slashes=False,
    methods=['POST'])
def create_place(city_id):
    """
    Create a new object place
    """
    if not request.get_json():
        return make_response(jsonify({"error": 'Not a JSON'}), 400)
    if 'name' not in request.get_json():
        return make_response(jsonify({"error": 'Missing name'}), 400)
    if 'user_id' not in request.get_json():
        return make_response(jsonify({"error": 'Missing user_id'}), 400)

    city = storage.get("City", city_id)
    if city is None:
        abort(404)

    place = request.get_json()
    user = storage.get("User", place["user_id"])
    if user is None:
        abort(404)

    place['city_id'] = city_id
    new_place = Place(**place)
    storage.new(new_place)
    storage.save()
    return jsonify(new_place.to_dict()), 201


@app_views.route('/places/<place_id>', methods=['PUT'])
def update_place(place_id):
    """
    Update a place by id
    """
    place = storage.get('Place', place_id)
    if place is None:
        abort(404)
    if not request.get_json():
        return make_response(jsonify({"error": 'Not a JSON'}), 400)
    params = request.get_json()
    skip = ['id', 'user_id', 'city_id', 'created_at', 'updated_at']
    for key, value in params.items():
        if key not in skip:
            setattr(place, key, value)
    storage.save()
    return jsonify(place.to_dict())


@app_views.errorhandler(404)
def page_not_found(error):
    """
    Handle 404 error
    """
    return jsonify({"error": "Not found"}), 404


@app_views.route('/places_search', methods=['POST'])
def places_search():
    """
        places route to handle http method for request to search places
    """
    all_places = [p for p in storage.all('Place').values()]
    req_json = request.get_json()
    if req_json is None:
        abort(400, 'Not a JSON')
    states = req_json.get('states')
    if states and len(states) > 0:
        all_cities = storage.all('City')
        state_cities = set([city.id for city in all_cities.values()
                            if city.state_id in states])
    else:
        state_cities = set()
    cities = req_json.get('cities')
    if cities and len(cities) > 0:
        cities = set([
            c_id for c_id in cities if storage.get('City', c_id)])
        state_cities = state_cities.union(cities)
    amenities = req_json.get('amenities')
    if len(state_cities) > 0:
        all_places = [p for p in all_places if p.city_id in state_cities]
    elif amenities is None or len(amenities) == 0:
        result = [place.to_json() for place in all_places]
        return jsonify(result)
    places_amenities = []
    if amenities and len(amenities) > 0:
        amenities = set([
            a_id for a_id in amenities if storage.get('Amenity', a_id)])
        for p in all_places:
            p_amenities = None
            if STORAGE_TYPE == 'db' and p.amenities:
                p_amenities = [a.id for a in p.amenities]
            elif len(p.amenities) > 0:
                p_amenities = p.amenities
            if p_amenities and all([a in p_amenities for a in amenities]):
                places_amenities.append(p)
    else:
        places_amenities = all_places
    result = [place.to_json() for place in places_amenities]
    return jsonify(result)
