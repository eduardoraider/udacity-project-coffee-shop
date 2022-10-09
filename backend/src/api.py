import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()


# GET ALL DRINKS ENDPOINT
@app.route('/drinks', methods=['GET'])
def get_drinks():

    list_drinks = Drink.query.all()

    drinks = [drink.short() for drink in list_drinks]

    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200


# GET DRINK DETAILS ENDPOINT
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_details(payload):

    list_drinks = Drink.query.all()

    drinks = [drink.long() for drink in list_drinks]

    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200


# POST NEW DRINK ENDPOINT
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(payload):

    body = request.get_json()

    try:

        new_recipe = body['recipe']
        if type(new_recipe) is dict:
            new_recipe = [new_recipe]

        new_title = body['title']

        new_drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
        new_drink.insert()
        drink = [new_drink.long()]

        return jsonify({
            'success': True,
            'drinks': drink
        })

    except Exception as ex:
        abort(422)


# EDIT DRINK ENDPOINT
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(payload, id):

    body = request.get_json()
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if drink is None:
        abort(404)

    try:

        edit_title = body.get('title', None)
        edit_recipe = body.get('recipe', None)

        if edit_title != None:
            drink.title = edit_title

        if edit_recipe != None:
            drink.recipe = json.dumps(body['recipe'])

        drink.update()

        drink = [drink.long()]

        return jsonify({
            'success': True,
            'drinks': drink
        }), 200

    except Exception as ex:
        abort(422)


# DELETE DRINK ENDPOINT
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):

    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if drink is None:
        abort(404)

    try:

        drink.delete()

        return jsonify({
            'success': True,
            'delete': id
        }), 200

    except Exception as ex:
        abort(422)


# 400 Bad Request
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Error 400 / Bad Request'
    }), 400


# 401 Unauthorized
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'Error 401 / Unauthorized'
    }), 401


# 403 Forbidden
@app.errorhandler(403)
def forbiden(error):
    return jsonify({
        'success': False,
        'error': 403,
        'message': 'Error 403 / Forbidden'
    }), 403


# 404 Not Found
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'Error 404 / Not Found'
    }), 404


# 405 Method Not Allowed
@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'Error 405 / Method Not Allowed'
    }), 405


# 409 Conflict
@app.errorhandler(409)
def conflict(error):
    return jsonify({
        'success': False,
        'error': 409,
        'message': 'Error 409 / Conflict'
    }), 409


# 422 Unprocessable Entity
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Error 422 / Unprocessable Entity"
    }), 422


# 500 Internal Server Error
@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Error 500 / Internal Server Error'
    }), 500


# Auth Error Handling
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error['description']
    }), error.status_code
