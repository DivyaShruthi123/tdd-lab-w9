# src/api/users.py
from flask import Blueprint, request
from flask_restx import Resource, Api, fields # updated

from src import db
from src.api.models import User

users_blueprint = Blueprint('users', __name__)
api = Api(users_blueprint)

# new
user = api.model('User', {
 'id': fields.Integer(readOnly=True),
 'username': fields.String(required=True),
 'email': fields.String(required=True),
 'created_date': fields.DateTime,
})

class Users(Resource):
 @api.marshal_with(user)
 def get(self, user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        api.abort(404, f"User {user_id} does not exist")
    return user, 200
 @api.expect(user, validate=True)
 @api.marshal_with(user)
 def put(self, user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        api.abort(404, f"User {user_id} does not exist")

    # Update user fields based on the request data
    update_data = request.get_json()
    user.username = update_data.get('username', user.username)
    user.email = update_data.get('email', user.email)
    db.session.commit()
    response_object = {'message': f'User {user_id} has been updated'}
    return user, 200

 def delete(self, user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        api.abort(404, f"User {user_id} does not exist")

    db.session.delete(user)
    db.session.commit()

    response_object = {'message': f'User {user_id} has been deleted'}
    return response_object, 200

class UsersList(Resource):
 @api.marshal_with(user, as_list=True)
 def get(self):
    return User.query.all(), 200
 @api.expect(user, validate=True) # new
 def post(self):
    post_data = request.get_json()
    username = post_data.get('username')
    email = post_data.get('email')
    response_object = {}
    user = User.query.filter_by(email=email).first()
    if user:
        response_object['message'] = 'Sorry. That email already exists.'
        return response_object, 400
    db.session.add(User(username=username, email=email))
    db.session.commit()
    response_object['message'] = f'{email} was added!'
    return response_object, 201
 
api.add_resource(UsersList, '/users')
api.add_resource(Users, '/users/<int:user_id>')